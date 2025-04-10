// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TestToken
 * @dev ERC20 token for testing on Goerli testnet
 */
contract TestToken is ERC20, Ownable {
    constructor() ERC20("QuantumNest Test Token", "QNT") Ownable(msg.sender) {
        // Mint 1,000,000 tokens to the contract creator
        _mint(msg.sender, 1000000 * 10**decimals());
    }
    
    /**
     * @dev Mint new tokens
     * @param to Recipient address
     * @param amount Amount to mint
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    /**
     * @dev Burn tokens
     * @param amount Amount to burn
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
