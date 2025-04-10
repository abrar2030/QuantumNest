import React, { useState, useEffect } from 'react';
import { useWallet } from './WalletProvider';
import { ethers } from 'ethers';

const WalletConnection = () => {
  const { 
    connectWallet, 
    disconnectWallet, 
    account, 
    network, 
    chainId, 
    connected, 
    balance, 
    error,
    switchNetwork
  } = useWallet();

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Format account address for display
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  // Format balance for display
  const formatBalance = (balance) => {
    if (!balance) return '0.00';
    return parseFloat(balance).toFixed(4);
  };

  // Get network color
  const getNetworkColor = () => {
    if (network === 'mainnet') return 'text-green-500';
    if (network === 'goerli') return 'text-yellow-500';
    if (network === 'sepolia') return 'text-purple-500';
    return 'text-gray-500';
  };

  // Handle network switch
  const handleNetworkSwitch = (newChainId) => {
    switchNetwork(newChainId);
    setIsDropdownOpen(false);
  };

  return (
    <div className="relative">
      {connected ? (
        <div className="flex items-center">
          <div className="mr-4 hidden md:block">
            <div className="text-sm text-gray-400">
              {network && (
                <span className={`${getNetworkColor()} font-medium`}>
                  {network.charAt(0).toUpperCase() + network.slice(1)}
                </span>
              )}
            </div>
            <div className="text-sm font-medium">
              {formatBalance(balance)} ETH
            </div>
          </div>
          
          <button 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-colors duration-200"
          >
            <span className="mr-2">{formatAddress(account)}</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50 top-full">
              <div className="py-1" role="menu" aria-orientation="vertical">
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">Account</div>
                  <div className="text-xs truncate">{account}</div>
                </div>
                
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">Balance</div>
                  <div>{formatBalance(balance)} ETH</div>
                </div>
                
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">Network</div>
                  <div className="flex flex-col mt-1 space-y-1">
                    <button 
                      onClick={() => handleNetworkSwitch(1)}
                      className={`text-left px-2 py-1 rounded text-xs ${network === 'mainnet' ? 'bg-green-100 text-green-800' : 'hover:bg-gray-100'}`}
                    >
                      Ethereum Mainnet
                    </button>
                    <button 
                      onClick={() => handleNetworkSwitch(5)}
                      className={`text-left px-2 py-1 rounded text-xs ${network === 'goerli' ? 'bg-yellow-100 text-yellow-800' : 'hover:bg-gray-100'}`}
                    >
                      Goerli Testnet
                    </button>
                    <button 
                      onClick={() => handleNetworkSwitch(11155111)}
                      className={`text-left px-2 py-1 rounded text-xs ${network === 'sepolia' ? 'bg-purple-100 text-purple-800' : 'hover:bg-gray-100'}`}
                    >
                      Sepolia Testnet
                    </button>
                  </div>
                </div>
                
                <button
                  onClick={() => {
                    disconnectWallet();
                    setIsDropdownOpen(false);
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-100"
                  role="menuitem"
                >
                  Disconnect Wallet
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <button
          onClick={connectWallet}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-colors duration-200"
        >
          Connect Wallet
        </button>
      )}
      
      {error && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-red-100 text-red-800 text-xs p-2 rounded">
          {error.message || "An error occurred"}
        </div>
      )}
    </div>
  );
};

export default WalletConnection;
