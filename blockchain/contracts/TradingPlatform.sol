// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title TradingPlatform
 * @dev Smart contract for secure trading of tokenized assets
 */
contract TradingPlatform is Ownable, ReentrancyGuard {
    // Order structure
    struct Order {
        uint256 id;
        address maker;
        address tokenAddress;
        uint256 amount;
        uint256 price; // In USD cents
        bool isBuyOrder;
        uint256 timestamp;
        bool isActive;
    }
    
    // Trade structure
    struct Trade {
        uint256 id;
        uint256 buyOrderId;
        uint256 sellOrderId;
        address buyer;
        address seller;
        address tokenAddress;
        uint256 amount;
        uint256 price; // In USD cents
        uint256 timestamp;
    }
    
    // Platform settings
    uint256 public tradingFee; // Basis points (e.g., 0.25% = 25)
    address public feeCollector;
    bool public tradingEnabled;
    
    // Order and trade storage
    mapping(uint256 => Order) public orders;
    mapping(uint256 => Trade) public trades;
    mapping(address => uint256[]) public userBuyOrders;
    mapping(address => uint256[]) public userSellOrders;
    mapping(address => uint256[]) public userTrades;
    
    // Counters
    uint256 private orderIdCounter;
    uint256 private tradeIdCounter;
    
    // Whitelisted tokens
    mapping(address => bool) public whitelistedTokens;
    
    // Events
    event OrderCreated(uint256 indexed orderId, address indexed maker, address tokenAddress, uint256 amount, uint256 price, bool isBuyOrder);
    event OrderCancelled(uint256 indexed orderId);
    event OrderFilled(uint256 indexed orderId, uint256 indexed tradeId);
    event TradeExecuted(uint256 indexed tradeId, address indexed buyer, address indexed seller, address tokenAddress, uint256 amount, uint256 price);
    event TokenWhitelisted(address indexed tokenAddress);
    event TokenRemovedFromWhitelist(address indexed tokenAddress);
    event TradingStatusChanged(bool enabled);
    event TradingFeeUpdated(uint256 newFee);
    event FeeCollectorUpdated(address newFeeCollector);
    
    /**
     * @dev Constructor
     * @param _tradingFee Initial trading fee in basis points
     * @param _feeCollector Address to collect fees
     */
    constructor(uint256 _tradingFee, address _feeCollector) Ownable(msg.sender) {
        require(_tradingFee <= 100, "Fee too high"); // Max 1%
        require(_feeCollector != address(0), "Invalid fee collector");
        
        tradingFee = _tradingFee;
        feeCollector = _feeCollector;
        tradingEnabled = false;
        orderIdCounter = 1;
        tradeIdCounter = 1;
    }
    
    /**
     * @dev Create a new order
     * @param _tokenAddress Token contract address
     * @param _amount Token amount
     * @param _price Price per token in USD cents
     * @param _isBuyOrder Whether order is buy or sell
     * @return orderId New order ID
     */
    function createOrder(
        address _tokenAddress,
        uint256 _amount,
        uint256 _price,
        bool _isBuyOrder
    ) external nonReentrant returns (uint256) {
        require(tradingEnabled, "Trading not enabled");
        require(whitelistedTokens[_tokenAddress], "Token not whitelisted");
        require(_amount > 0, "Amount must be greater than 0");
        require(_price > 0, "Price must be greater than 0");
        
        // For sell orders, check token balance and approval
        if (!_isBuyOrder) {
            IERC20 token = IERC20(_tokenAddress);
            require(token.balanceOf(msg.sender) >= _amount, "Insufficient token balance");
            require(token.allowance(msg.sender, address(this)) >= _amount, "Insufficient token allowance");
        }
        
        // Create order
        uint256 orderId = orderIdCounter++;
        
        orders[orderId] = Order({
            id: orderId,
            maker: msg.sender,
            tokenAddress: _tokenAddress,
            amount: _amount,
            price: _price,
            isBuyOrder: _isBuyOrder,
            timestamp: block.timestamp,
            isActive: true
        });
        
        // Add to user orders
        if (_isBuyOrder) {
            userBuyOrders[msg.sender].push(orderId);
        } else {
            userSellOrders[msg.sender].push(orderId);
        }
        
        emit OrderCreated(orderId, msg.sender, _tokenAddress, _amount, _price, _isBuyOrder);
        
        // Try to match order
        matchOrder(orderId);
        
        return orderId;
    }
    
    /**
     * @dev Cancel an order
     * @param _orderId Order ID
     */
    function cancelOrder(uint256 _orderId) external nonReentrant {
        Order storage order = orders[_orderId];
        
        require(order.maker == msg.sender, "Not order maker");
        require(order.isActive, "Order not active");
        
        order.isActive = false;
        
        emit OrderCancelled(_orderId);
    }
    
    /**
     * @dev Match order with existing orders
     * @param _orderId Order ID
     */
    function matchOrder(uint256 _orderId) internal {
        Order storage order = orders[_orderId];
        
        if (!order.isActive) {
            return;
        }
        
        // Find matching orders
        for (uint256 i = 1; i < orderIdCounter; i++) {
            if (i == _orderId) {
                continue;
            }
            
            Order storage matchingOrder = orders[i];
            
            if (!matchingOrder.isActive) {
                continue;
            }
            
            if (matchingOrder.tokenAddress != order.tokenAddress) {
                continue;
            }
            
            if (matchingOrder.isBuyOrder == order.isBuyOrder) {
                continue;
            }
            
            // Check price match
            bool priceMatches = false;
            
            if (order.isBuyOrder) {
                // Buy order matches if its price >= sell order price
                priceMatches = order.price >= matchingOrder.price;
            } else {
                // Sell order matches if its price <= buy order price
                priceMatches = order.price <= matchingOrder.price;
            }
            
            if (!priceMatches) {
                continue;
            }
            
            // Execute trade
            executeTrade(order.isBuyOrder ? _orderId : i, order.isBuyOrder ? i : _orderId);
            
            // If order is fully filled, stop matching
            if (!order.isActive) {
                break;
            }
        }
    }
    
    /**
     * @dev Execute trade between buy and sell orders
     * @param _buyOrderId Buy order ID
     * @param _sellOrderId Sell order ID
     */
    function executeTrade(uint256 _buyOrderId, uint256 _sellOrderId) internal {
        Order storage buyOrder = orders[_buyOrderId];
        Order storage sellOrder = orders[_sellOrderId];
        
        require(buyOrder.isActive && sellOrder.isActive, "Orders not active");
        require(buyOrder.isBuyOrder && !sellOrder.isBuyOrder, "Invalid order types");
        require(buyOrder.tokenAddress == sellOrder.tokenAddress, "Token mismatch");
        
        // Determine trade amount and price
        uint256 tradeAmount = buyOrder.amount < sellOrder.amount ? buyOrder.amount : sellOrder.amount;
        uint256 tradePrice = sellOrder.price; // Use sell order price
        
        // Calculate total value and fee
        uint256 totalValue = tradeAmount * tradePrice;
        uint256 fee = (totalValue * tradingFee) / 10000;
        
        // Transfer tokens from seller to buyer
        IERC20 token = IERC20(buyOrder.tokenAddress);
        require(token.transferFrom(sellOrder.maker, buyOrder.maker, tradeAmount), "Token transfer failed");
        
        // Transfer fee to fee collector
        if (fee > 0) {
            // Fee is paid by both parties
            // Implementation depends on how fees are collected (e.g., separate token, off-chain)
        }
        
        // Update order amounts
        buyOrder.amount -= tradeAmount;
        sellOrder.amount -= tradeAmount;
        
        // Deactivate filled orders
        if (buyOrder.amount == 0) {
            buyOrder.isActive = false;
        }
        
        if (sellOrder.amount == 0) {
            sellOrder.isActive = false;
        }
        
        // Create trade record
        uint256 tradeId = tradeIdCounter++;
        
        trades[tradeId] = Trade({
            id: tradeId,
            buyOrderId: _buyOrderId,
            sellOrderId: _sellOrderId,
            buyer: buyOrder.maker,
            seller: sellOrder.maker,
            tokenAddress: buyOrder.tokenAddress,
            amount: tradeAmount,
            price: tradePrice,
            timestamp: block.timestamp
        });
        
        // Add to user trades
        userTrades[buyOrder.maker].push(tradeId);
        userTrades[sellOrder.maker].push(tradeId);
        
        // Emit events
        emit OrderFilled(_buyOrderId, tradeId);
        emit OrderFilled(_sellOrderId, tradeId);
        emit TradeExecuted(tradeId, buyOrder.maker, sellOrder.maker, buyOrder.tokenAddress, tradeAmount, tradePrice);
    }
    
    /**
     * @dev Whitelist token
     * @param _tokenAddress Token contract address
     */
    function whitelistToken(address _tokenAddress) external onlyOwner {
        require(_tokenAddress != address(0), "Invalid token address");
        
        whitelistedTokens[_tokenAddress] = true;
        
        emit TokenWhitelisted(_tokenAddress);
    }
    
    /**
     * @dev Remove token from whitelist
     * @param _tokenAddress Token contract address
     */
    function removeTokenFromWhitelist(address _tokenAddress) external onlyOwner {
        require(whitelistedTokens[_tokenAddress], "Token not whitelisted");
        
        whitelistedTokens[_tokenAddress] = false;
        
        emit TokenRemovedFromWhitelist(_tokenAddress);
    }
    
    /**
     * @dev Set trading status
     * @param _enabled Trading status
     */
    function setTradingEnabled(bool _enabled) external onlyOwner {
        tradingEnabled = _enabled;
        
        emit TradingStatusChanged(_enabled);
    }
    
    /**
     * @dev Set trading fee
     * @param _tradingFee Trading fee in basis points
     */
    function setTradingFee(uint256 _tradingFee) external onlyOwner {
        require(_tradingFee <= 100, "Fee too high"); // Max 1%
        
        tradingFee = _tradingFee;
        
        emit TradingFeeUpdated(_tradingFee);
    }
    
    /**
     * @dev Set fee collector
     * @param _feeCollector Fee collector address
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid fee collector");
        
        feeCollector = _feeCollector;
        
        emit FeeCollectorUpdated(_feeCollector);
    }
    
    /**
     * @dev Get user buy orders
     * @param _user User address
     * @return orderIds Array of order IDs
     */
    function getUserBuyOrders(address _user) external view returns (uint256[] memory) {
        return userBuyOrders[_user];
    }
    
    /**
     * @dev Get user sell orders
     * @param _user User address
     * @return orderIds Array of order IDs
     */
    function getUserSellOrders(address _user) external view returns (uint256[] memory) {
        return userSellOrders[_user];
    }
    
    /**
     * @dev Get user trades
     * @param _user User address
     * @return tradeIds Array of trade IDs
     */
    function getUserTrades(address _user) external view returns (uint256[] memory) {
        return userTrades[_user];
    }
    
    /**
     * @dev Get active orders for token
     * @param _tokenAddress Token contract address
     * @param _isBuyOrder Whether to get buy or sell orders
     * @param _startIndex Start index
     * @param _count Number of orders to return
     * @return activeOrders Array of active orders
     */
    function getActiveOrders(
        address _tokenAddress,
        bool _isBuyOrder,
        uint256 _startIndex,
        uint256 _count
    ) external view returns (Order[] memory) {
        // Count active orders
        uint256 activeCount = 0;
        for (uint256 i = 1; i < orderIdCounter; i++) {
            Order storage order = orders[i];
            if (order.isActive && order.tokenAddress == _tokenAddress && order.isBuyOrder == _isBuyOrder) {
                activeCount++;
            }
        }
        
        if (_startIndex >= activeCount) {
            return new Order[](0);
        }
        
        uint256 endIndex = _startIndex + _count;
        if (endIndex > activeCount) {
            endIndex = activeCount;
        }
        
        uint256 resultCount = endIndex - _startIndex;
        Order[] memory result = new Order[](resultCount);
        
        uint256 currentIndex = 0;
        uint256 resultIndex = 0;
        
        for (uint256 i = 1; i < orderIdCounter && resultIndex < resultCount; i++) {
            Order storage order = orders[i];
            if (order.isActive && order.tokenAddress == _tokenAddress && order.isBuyOrder == _isBuyOrder) {
                if (currentIndex >= _startIndex && currentIndex < endIndex) {
                    result[resultIndex] = order;
                    resultIndex++;
                }
                currentIndex++;
            }
        }
        
        return result;
    }
}
