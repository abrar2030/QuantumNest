// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title PortfolioManager
 * @dev Smart contract for managing investment portfolios on-chain
 */
contract PortfolioManager is Ownable, ReentrancyGuard {
    // Portfolio structure
    struct Portfolio {
        string name;
        string description;
        uint256 creationDate;
        uint256 lastRebalanceDate;
        bool isActive;
        address[] allowedManagers;
    }
    
    // Asset allocation structure
    struct AssetAllocation {
        address tokenAddress;
        string symbol;
        uint256 targetAllocation; // Basis points (e.g., 10% = 1000)
        uint256 currentAllocation; // Basis points
        bool isActive;
    }
    
    // Transaction structure
    struct Transaction {
        uint256 timestamp;
        address tokenAddress;
        string symbol;
        uint256 amount;
        uint256 price; // In USD cents
        bool isBuy; // true for buy, false for sell
        string transactionType; // "rebalance", "deposit", "withdrawal", "manual"
    }
    
    // Portfolio mapping
    mapping(uint256 => Portfolio) public portfolios;
    mapping(uint256 => mapping(address => AssetAllocation)) public assetAllocations;
    mapping(uint256 => address[]) public portfolioAssets;
    mapping(uint256 => Transaction[]) public portfolioTransactions;
    
    // User portfolios
    mapping(address => uint256[]) public userPortfolios;
    
    // Portfolio counter
    uint256 private portfolioCounter;
    
    // Events
    event PortfolioCreated(uint256 indexed portfolioId, address indexed owner, string name);
    event PortfolioUpdated(uint256 indexed portfolioId, string name, string description);
    event AssetAdded(uint256 indexed portfolioId, address tokenAddress, string symbol, uint256 targetAllocation);
    event AssetRemoved(uint256 indexed portfolioId, address tokenAddress, string symbol);
    event AllocationUpdated(uint256 indexed portfolioId, address tokenAddress, uint256 targetAllocation);
    event PortfolioRebalanced(uint256 indexed portfolioId, uint256 timestamp);
    event TransactionRecorded(uint256 indexed portfolioId, address tokenAddress, uint256 amount, bool isBuy);
    event ManagerAdded(uint256 indexed portfolioId, address manager);
    event ManagerRemoved(uint256 indexed portfolioId, address manager);
    
    /**
     * @dev Constructor
     */
    constructor() Ownable(msg.sender) {
        portfolioCounter = 1; // Start from 1
    }
    
    /**
     * @dev Create a new portfolio
     * @param _name Portfolio name
     * @param _description Portfolio description
     * @return portfolioId New portfolio ID
     */
    function createPortfolio(string memory _name, string memory _description) external returns (uint256) {
        uint256 portfolioId = portfolioCounter++;
        
        portfolios[portfolioId] = Portfolio({
            name: _name,
            description: _description,
            creationDate: block.timestamp,
            lastRebalanceDate: block.timestamp,
            isActive: true,
            allowedManagers: new address[](0)
        });
        
        userPortfolios[msg.sender].push(portfolioId);
        
        emit PortfolioCreated(portfolioId, msg.sender, _name);
        
        return portfolioId;
    }
    
    /**
     * @dev Update portfolio details
     * @param _portfolioId Portfolio ID
     * @param _name New portfolio name
     * @param _description New portfolio description
     */
    function updatePortfolio(uint256 _portfolioId, string memory _name, string memory _description) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        
        portfolios[_portfolioId].name = _name;
        portfolios[_portfolioId].description = _description;
        
        emit PortfolioUpdated(_portfolioId, _name, _description);
    }
    
    /**
     * @dev Add asset to portfolio
     * @param _portfolioId Portfolio ID
     * @param _tokenAddress Token contract address
     * @param _symbol Token symbol
     * @param _targetAllocation Target allocation in basis points
     */
    function addAsset(
        uint256 _portfolioId,
        address _tokenAddress,
        string memory _symbol,
        uint256 _targetAllocation
    ) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(_targetAllocation <= 10000, "Allocation too high");
        require(assetAllocations[_portfolioId][_tokenAddress].targetAllocation == 0, "Asset already exists");
        
        // Add asset to portfolio
        assetAllocations[_portfolioId][_tokenAddress] = AssetAllocation({
            tokenAddress: _tokenAddress,
            symbol: _symbol,
            targetAllocation: _targetAllocation,
            currentAllocation: 0,
            isActive: true
        });
        
        portfolioAssets[_portfolioId].push(_tokenAddress);
        
        emit AssetAdded(_portfolioId, _tokenAddress, _symbol, _targetAllocation);
    }
    
    /**
     * @dev Remove asset from portfolio
     * @param _portfolioId Portfolio ID
     * @param _tokenAddress Token contract address
     */
    function removeAsset(uint256 _portfolioId, address _tokenAddress) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(assetAllocations[_portfolioId][_tokenAddress].isActive, "Asset not active");
        
        // Deactivate asset
        assetAllocations[_portfolioId][_tokenAddress].isActive = false;
        
        emit AssetRemoved(_portfolioId, _tokenAddress, assetAllocations[_portfolioId][_tokenAddress].symbol);
    }
    
    /**
     * @dev Update asset allocation
     * @param _portfolioId Portfolio ID
     * @param _tokenAddress Token contract address
     * @param _targetAllocation New target allocation in basis points
     */
    function updateAllocation(
        uint256 _portfolioId,
        address _tokenAddress,
        uint256 _targetAllocation
    ) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(assetAllocations[_portfolioId][_tokenAddress].isActive, "Asset not active");
        require(_targetAllocation <= 10000, "Allocation too high");
        
        assetAllocations[_portfolioId][_tokenAddress].targetAllocation = _targetAllocation;
        
        emit AllocationUpdated(_portfolioId, _tokenAddress, _targetAllocation);
    }
    
    /**
     * @dev Record portfolio rebalance
     * @param _portfolioId Portfolio ID
     * @param _transactions Array of transactions
     */
    function recordRebalance(
        uint256 _portfolioId,
        address[] memory _tokenAddresses,
        string[] memory _symbols,
        uint256[] memory _amounts,
        uint256[] memory _prices,
        bool[] memory _isBuys
    ) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(
            _tokenAddresses.length == _symbols.length &&
            _tokenAddresses.length == _amounts.length &&
            _tokenAddresses.length == _prices.length &&
            _tokenAddresses.length == _isBuys.length,
            "Array length mismatch"
        );
        
        // Record transactions
        for (uint256 i = 0; i < _tokenAddresses.length; i++) {
            Transaction memory transaction = Transaction({
                timestamp: block.timestamp,
                tokenAddress: _tokenAddresses[i],
                symbol: _symbols[i],
                amount: _amounts[i],
                price: _prices[i],
                isBuy: _isBuys[i],
                transactionType: "rebalance"
            });
            
            portfolioTransactions[_portfolioId].push(transaction);
            
            emit TransactionRecorded(_portfolioId, _tokenAddresses[i], _amounts[i], _isBuys[i]);
        }
        
        // Update rebalance date
        portfolios[_portfolioId].lastRebalanceDate = block.timestamp;
        
        emit PortfolioRebalanced(_portfolioId, block.timestamp);
    }
    
    /**
     * @dev Record single transaction
     * @param _portfolioId Portfolio ID
     * @param _tokenAddress Token contract address
     * @param _symbol Token symbol
     * @param _amount Transaction amount
     * @param _price Transaction price in USD cents
     * @param _isBuy Whether transaction is buy or sell
     * @param _transactionType Transaction type
     */
    function recordTransaction(
        uint256 _portfolioId,
        address _tokenAddress,
        string memory _symbol,
        uint256 _amount,
        uint256 _price,
        bool _isBuy,
        string memory _transactionType
    ) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        
        Transaction memory transaction = Transaction({
            timestamp: block.timestamp,
            tokenAddress: _tokenAddress,
            symbol: _symbol,
            amount: _amount,
            price: _price,
            isBuy: _isBuy,
            transactionType: _transactionType
        });
        
        portfolioTransactions[_portfolioId].push(transaction);
        
        emit TransactionRecorded(_portfolioId, _tokenAddress, _amount, _isBuy);
    }
    
    /**
     * @dev Update current allocations
     * @param _portfolioId Portfolio ID
     * @param _tokenAddresses Token addresses
     * @param _currentAllocations Current allocations in basis points
     */
    function updateCurrentAllocations(
        uint256 _portfolioId,
        address[] memory _tokenAddresses,
        uint256[] memory _currentAllocations
    ) external {
        require(isPortfolioOwnerOrManager(_portfolioId, msg.sender), "Not authorized");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(_tokenAddresses.length == _currentAllocations.length, "Array length mismatch");
        
        uint256 totalAllocation = 0;
        
        for (uint256 i = 0; i < _tokenAddresses.length; i++) {
            require(assetAllocations[_portfolioId][_tokenAddresses[i]].isActive, "Asset not active");
            assetAllocations[_portfolioId][_tokenAddresses[i]].currentAllocation = _currentAllocations[i];
            totalAllocation += _currentAllocations[i];
        }
        
        require(totalAllocation <= 10000, "Total allocation exceeds 100%");
    }
    
    /**
     * @dev Add portfolio manager
     * @param _portfolioId Portfolio ID
     * @param _manager Manager address
     */
    function addManager(uint256 _portfolioId, address _manager) external {
        require(isPortfolioOwner(_portfolioId, msg.sender), "Not owner");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        require(_manager != address(0), "Invalid address");
        
        // Check if manager already exists
        for (uint256 i = 0; i < portfolios[_portfolioId].allowedManagers.length; i++) {
            if (portfolios[_portfolioId].allowedManagers[i] == _manager) {
                revert("Manager already exists");
            }
        }
        
        portfolios[_portfolioId].allowedManagers.push(_manager);
        
        emit ManagerAdded(_portfolioId, _manager);
    }
    
    /**
     * @dev Remove portfolio manager
     * @param _portfolioId Portfolio ID
     * @param _manager Manager address
     */
    function removeManager(uint256 _portfolioId, address _manager) external {
        require(isPortfolioOwner(_portfolioId, msg.sender), "Not owner");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        
        bool found = false;
        uint256 index = 0;
        
        for (uint256 i = 0; i < portfolios[_portfolioId].allowedManagers.length; i++) {
            if (portfolios[_portfolioId].allowedManagers[i] == _manager) {
                found = true;
                index = i;
                break;
            }
        }
        
        require(found, "Manager not found");
        
        // Remove manager by replacing with last element and popping
        uint256 lastIndex = portfolios[_portfolioId].allowedManagers.length - 1;
        if (index != lastIndex) {
            portfolios[_portfolioId].allowedManagers[index] = portfolios[_portfolioId].allowedManagers[lastIndex];
        }
        portfolios[_portfolioId].allowedManagers.pop();
        
        emit ManagerRemoved(_portfolioId, _manager);
    }
    
    /**
     * @dev Deactivate portfolio
     * @param _portfolioId Portfolio ID
     */
    function deactivatePortfolio(uint256 _portfolioId) external {
        require(isPortfolioOwner(_portfolioId, msg.sender), "Not owner");
        require(portfolios[_portfolioId].isActive, "Portfolio not active");
        
        portfolios[_portfolioId].isActive = false;
    }
    
    /**
     * @dev Reactivate portfolio
     * @param _portfolioId Portfolio ID
     */
    function reactivatePortfolio(uint256 _portfolioId) external {
        require(isPortfolioOwner(_portfolioId, msg.sender), "Not owner");
        require(!portfolios[_portfolioId].isActive, "Portfolio already active");
        
        portfolios[_portfolioId].isActive = true;
    }
    
    /**
     * @dev Check if address is portfolio owner
     * @param _portfolioId Portfolio ID
     * @param _address Address to check
     * @return isOwner Whether address is portfolio owner
     */
    function isPortfolioOwner(uint256 _portfolioId, address _address) public view returns (bool) {
        uint256[] memory ownerPortfolios = userPortfolios[_address];
        
        for (uint256 i = 0; i < ownerPortfolios.length; i++) {
            if (ownerPortfolios[i] == _portfolioId) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Check if address is portfolio manager
     * @param _portfolioId Portfolio ID
     * @param _address Address to check
     * @return isManager Whether address is portfolio manager
     */
    function isPortfolioManager(uint256 _portfolioId, address _address) public view returns (bool) {
        for (uint256 i = 0; i < portfolios[_portfolioId].allowedManagers.length; i++) {
            if (portfolios[_portfolioId].allowedManagers[i] == _address) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Check if address is portfolio owner or manager
     * @param _portfolioId Portfolio ID
     * @param _address Address to check
     * @return isOwnerOrManager Whether address is portfolio owner or manager
     */
    function isPortfolioOwnerOrManager(uint256 _portfolioId, address _address) public view returns (bool) {
        return isPortfolioOwner(_portfolioId, _address) || isPortfolioManager(_portfolioId, _address);
    }
    
    /**
     * @dev Get portfolio assets
     * @param _portfolioId Portfolio ID
     * @return assets Array of asset addresses
     */
    function getPortfolioAssets(uint256 _portfolioId) external view returns (address[] memory) {
        return portfolioAssets[_portfolioId];
    }
    
    /**
     * @dev Get portfolio managers
     * @param _portfolioId Portfolio ID
     * @return managers Array of manager addresses
     */
    function getPortfolioManagers(uint256 _portfolioId) external view returns (address[] memory) {
        return portfolios[_portfolioId].allowedManagers;
    }
    
    /**
     * @dev Get user portfolios
     * @param _user User address
     * @return portfolioIds Array of portfolio IDs
     */
    function getUserPortfolios(address _user) external view returns (uint256[] memory) {
        return userPortfolios[_user];
    }
    
    /**
     * @dev Get portfolio transaction count
     * @param _portfolioId Portfolio ID
     * @return count Transaction count
     */
    function getPortfolioTransactionCount(uint256 _portfolioId) external view returns (uint256) {
        return portfolioTransactions[_portfolioId].length;
    }
    
    /**
     * @dev Get portfolio transactions
     * @param _portfolioId Portfolio ID
     * @param _startIndex Start index
     * @param _count Number of transactions to return
     * @return transactions Array of transactions
     */
    function getPortfolioTransactions(
        uint256 _portfolioId,
        uint256 _startIndex,
        uint256 _count
    ) external view returns (Transaction[] memory) {
        uint256 totalCount = portfolioTransactions[_portfolioId].length;
        
        if (_startIndex >= totalCount) {
            return new Transaction[](0);
        }
        
        uint256 endIndex = _startIndex + _count;
        if (endIndex > totalCount) {
            endIndex = totalCount;
        }
        
        uint256 resultCount = endIndex - _startIndex;
        Transaction[] memory result = new Transaction[](resultCount);
        
        for (uint256 i = 0; i < resultCount; i++) {
            result[i] = portfolioTransactions[_portfolioId][_startIndex + i];
        }
        
        return result;
    }
}
