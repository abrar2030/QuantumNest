import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import Web3Modal from 'web3modal';
import WalletConnectProvider from '@walletconnect/web3-provider';
import CoinbaseWalletSDK from '@coinbase/wallet-sdk';

// Create a context for the wallet
export const WalletContext = React.createContext();

// Provider configuration
const providerOptions = {
  walletconnect: {
    package: WalletConnectProvider,
    options: {
      infuraId: process.env.NEXT_PUBLIC_INFURA_ID,
    }
  },
  coinbasewallet: {
    package: CoinbaseWalletSDK,
    options: {
      appName: "QuantumNest Capital",
      infuraId: process.env.NEXT_PUBLIC_INFURA_ID,
    }
  }
};

// Web3Modal instance
let web3Modal;
if (typeof window !== 'undefined') {
  web3Modal = new Web3Modal({
    network: "mainnet", // optional
    cacheProvider: true, // optional
    providerOptions, // required
    theme: "dark"
  });
}

export const WalletProvider = ({ children }) => {
  const [provider, setProvider] = useState(null);
  const [library, setLibrary] = useState(null);
  const [account, setAccount] = useState(null);
  const [network, setNetwork] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [balance, setBalance] = useState(null);

  // Connect to wallet
  const connectWallet = async () => {
    try {
      const provider = await web3Modal.connect();
      const library = new ethers.providers.Web3Provider(provider);
      const accounts = await library.listAccounts();
      const network = await library.getNetwork();
      
      setProvider(provider);
      setLibrary(library);
      
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        const balance = await library.getBalance(accounts[0]);
        setBalance(ethers.utils.formatEther(balance));
      }
      
      setNetwork(network.name);
      setChainId(network.chainId);
      setConnected(true);
      setError(null);
    } catch (error) {
      setError(error);
      console.error("Connection error:", error);
    }
  };

  // Disconnect wallet
  const disconnectWallet = async () => {
    try {
      await web3Modal.clearCachedProvider();
      setProvider(null);
      setLibrary(null);
      setAccount(null);
      setNetwork(null);
      setChainId(null);
      setConnected(false);
      setBalance(null);
    } catch (error) {
      setError(error);
      console.error("Disconnection error:", error);
    }
  };

  // Switch network
  const switchNetwork = async (chainId) => {
    try {
      if (!provider) return;
      
      await provider.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: ethers.utils.hexValue(chainId) }]
      });
    } catch (error) {
      setError(error);
      console.error("Network switch error:", error);
    }
  };

  // Handle account changes
  const handleAccountsChanged = (accounts) => {
    if (accounts.length > 0) {
      setAccount(accounts[0]);
      updateBalance(accounts[0]);
    } else {
      setAccount(null);
      setBalance(null);
    }
  };

  // Handle chain changes
  const handleChainChanged = (chainId) => {
    const newChainId = parseInt(chainId, 16);
    setChainId(newChainId);
    
    // Get network name
    if (newChainId === 1) {
      setNetwork('mainnet');
    } else if (newChainId === 5) {
      setNetwork('goerli');
    } else if (newChainId === 11155111) {
      setNetwork('sepolia');
    } else {
      setNetwork(`chain-${newChainId}`);
    }
    
    // Update balance for new chain
    if (account) {
      updateBalance(account);
    }
  };

  // Update balance
  const updateBalance = async (address) => {
    if (library) {
      const balance = await library.getBalance(address);
      setBalance(ethers.utils.formatEther(balance));
    }
  };

  // Auto connect if cached
  useEffect(() => {
    if (web3Modal.cachedProvider) {
      connectWallet();
    }
  }, []);

  // Set up event listeners
  useEffect(() => {
    if (provider) {
      provider.on("accountsChanged", handleAccountsChanged);
      provider.on("chainChanged", handleChainChanged);
      provider.on("disconnect", disconnectWallet);

      return () => {
        if (provider.removeListener) {
          provider.removeListener("accountsChanged", handleAccountsChanged);
          provider.removeListener("chainChanged", handleChainChanged);
          provider.removeListener("disconnect", disconnectWallet);
        }
      };
    }
  }, [provider]);

  // Contract interaction helpers
  const getContract = (address, abi) => {
    if (!library) return null;
    return new ethers.Contract(address, abi, library.getSigner());
  };

  const callContractMethod = async (contract, method, ...args) => {
    try {
      return await contract[method](...args);
    } catch (error) {
      setError(error);
      console.error(`Error calling ${method}:`, error);
      throw error;
    }
  };

  const sendTransaction = async (contract, method, ...args) => {
    try {
      const tx = await contract[method](...args);
      return await tx.wait();
    } catch (error) {
      setError(error);
      console.error(`Error in transaction ${method}:`, error);
      throw error;
    }
  };

  return (
    <WalletContext.Provider
      value={{
        connectWallet,
        disconnectWallet,
        switchNetwork,
        getContract,
        callContractMethod,
        sendTransaction,
        updateBalance,
        provider,
        library,
        account,
        network,
        chainId,
        connected,
        error,
        balance
      }}
    >
      {children}
    </WalletContext.Provider>
  );
};

// Custom hook to use the wallet context
export const useWallet = () => {
  const context = React.useContext(WalletContext);
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
};
