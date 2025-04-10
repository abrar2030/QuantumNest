// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TokenizedAsset
 * @dev ERC20 token representing a tokenized real-world asset
 */
contract TokenizedAsset is ERC20, Ownable {
    // Asset details
    string public assetSymbol;
    string public assetName;
    string public assetType; // e.g., "stock", "bond", "commodity", "real_estate"
    uint256 public assetValue; // Value in USD cents (e.g., $10.50 = 1050)
    
    // Asset metadata
    string public description;
    string public issuer;
    uint256 public issuanceDate;
    uint256 public maturityDate; // 0 if no maturity
    
    // Asset performance
    int256 public yearToDateReturn; // Basis points (e.g., 5.25% = 525)
    uint256 public lastValuationDate;
    
    // Trading parameters
    bool public tradingEnabled;
    uint256 public tradingFee; // Basis points
    
    // Events
    event AssetRevalued(uint256 oldValue, uint256 newValue, uint256 timestamp);
    event TradingStatusChanged(bool enabled);
    event PerformanceUpdated(int256 ytdReturn, uint256 timestamp);
    
    /**
     * @dev Constructor
     * @param _name Token name
     * @param _symbol Token symbol
     * @param _assetSymbol Underlying asset symbol
     * @param _assetName Underlying asset name
     * @param _assetType Type of asset
     * @param _initialSupply Initial token supply
     * @param _initialValue Initial asset value in USD cents
     * @param _description Asset description
     * @param _issuer Asset issuer
     */
    constructor(
        string memory _name,
        string memory _symbol,
        string memory _assetSymbol,
        string memory _assetName,
        string memory _assetType,
        uint256 _initialSupply,
        uint256 _initialValue,
        string memory _description,
        string memory _issuer
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        assetSymbol = _assetSymbol;
        assetName = _assetName;
        assetType = _assetType;
        assetValue = _initialValue;
        description = _description;
        issuer = _issuer;
        issuanceDate = block.timestamp;
        lastValuationDate = block.timestamp;
        tradingEnabled = false;
        tradingFee = 25; // Default 0.25% fee
        
        // Mint initial supply to contract creator
        _mint(msg.sender, _initialSupply * 10**decimals());
    }
    
    /**
     * @dev Update asset value
     * @param _newValue New asset value in USD cents
     */
    function updateAssetValue(uint256 _newValue) external onlyOwner {
        uint256 oldValue = assetValue;
        assetValue = _newValue;
        lastValuationDate = block.timestamp;
        
        emit AssetRevalued(oldValue, _newValue, block.timestamp);
    }
    
    /**
     * @dev Update asset performance
     * @param _ytdReturn Year-to-date return in basis points
     */
    function updatePerformance(int256 _ytdReturn) external onlyOwner {
        yearToDateReturn = _ytdReturn;
        
        emit PerformanceUpdated(_ytdReturn, block.timestamp);
    }
    
    /**
     * @dev Enable or disable trading
     * @param _enabled Trading status
     */
    function setTradingEnabled(bool _enabled) external onlyOwner {
        tradingEnabled = _enabled;
        
        emit TradingStatusChanged(_enabled);
    }
    
    /**
     * @dev Set trading fee
     * @param _fee Trading fee in basis points
     */
    function setTradingFee(uint256 _fee) external onlyOwner {
        require(_fee <= 500, "Fee too high"); // Max 5%
        tradingFee = _fee;
    }
    
    /**
     * @dev Update asset metadata
     * @param _description New description
     * @param _maturityDate New maturity date (0 if no maturity)
     */
    function updateMetadata(
        string memory _description,
        uint256 _maturityDate
    ) external onlyOwner {
        description = _description;
        maturityDate = _maturityDate;
    }
    
    /**
     * @dev Mint new tokens
     * @param _to Recipient address
     * @param _amount Amount to mint
     */
    function mint(address _to, uint256 _amount) external onlyOwner {
        _mint(_to, _amount);
    }
    
    /**
     * @dev Burn tokens
     * @param _amount Amount to burn
     */
    function burn(uint256 _amount) external {
        _burn(msg.sender, _amount);
    }
    
    /**
     * @dev Override transfer function to enforce trading rules
     */
    function _transfer(
        address sender,
        address recipient,
        uint256 amount
    ) internal override {
        require(tradingEnabled || sender == owner() || recipient == owner(), "Trading not enabled");
        
        // Calculate fee if sender is not owner
        if (sender != owner() && tradingFee > 0) {
            uint256 fee = (amount * tradingFee) / 10000;
            super._transfer(sender, owner(), fee);
            super._transfer(sender, recipient, amount - fee);
        } else {
            super._transfer(sender, recipient, amount);
        }
    }
    
    /**
     * @dev Get asset details
     * @return Asset details as a struct
     */
    function getAssetDetails() external view returns (
        string memory _assetSymbol,
        string memory _assetName,
        string memory _assetType,
        uint256 _assetValue,
        string memory _description,
        string memory _issuer,
        uint256 _issuanceDate,
        uint256 _maturityDate,
        int256 _yearToDateReturn,
        uint256 _lastValuationDate,
        bool _tradingEnabled,
        uint256 _tradingFee
    ) {
        return (
            assetSymbol,
            assetName,
            assetType,
            assetValue,
            description,
            issuer,
            issuanceDate,
            maturityDate,
            yearToDateReturn,
            lastValuationDate,
            tradingEnabled,
            tradingFee
        );
    }
}
