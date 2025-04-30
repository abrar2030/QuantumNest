'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ethers } from 'ethers';
import { Web3Provider } from '@ethersproject/providers';
import { InjectedConnector } from '@web3-react/injected-connector';

// Contract ABIs would be imported here in a real application
// import TokenizedAssetABI from '@/contracts/TokenizedAsset.json';
// import PortfolioManagerABI from '@/contracts/PortfolioManager.json';
// import TradingPlatformABI from '@/contracts/TradingPlatform.json';
// import DeFiIntegrationABI from '@/contracts/DeFiIntegration.json';
// import TestTokenABI from '@/contracts/TestToken.json';

// Mock ABIs for development
const TokenizedAssetABI = ["function balanceOf(address owner) view returns (uint256)"] as const;
const PortfolioManagerABI = ["function getPortfolios(address owner) view returns (string[])"] as const;
const TradingPlatformABI = ["function executeTrade(address token, uint256 amount, bool isBuy) returns (bool)"] as const;
const DeFiIntegrationABI = ["function getYieldOptions() view returns (string[])"] as const;
const TestTokenABI = ["function transfer(address to, uint256 amount) returns (bool)"] as const;

// Contract addresses would be configured based on the network
const CONTRACT_ADDRESSES = {
  TokenizedAsset: '0x7890123456789012345678901234567890123456',
  PortfolioManager: '0x8901234567890123456789012345678901234567',
  TradingPlatform: '0x9012345678901234567890123456789012345678',
  DeFiIntegration: '0x0123456789012345678901234567890123456789',
  TestToken: '0x1234567890123456789012345678901234567890',
};

// Configure supported chains
const injected = new InjectedConnector({
  supportedChainIds: [1, 5, 11155111], // Mainnet, Goerli, Sepolia
});

interface BlockchainContextType {
  account: string | null;
  chainId: number | null;
  provider: Web3Provider | null;
  signer: ethers.Signer | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  contracts: {
    tokenizedAsset: ethers.Contract | null;
    portfolioManager: ethers.Contract | null;
    tradingPlatform: ethers.Contract | null;
    defiIntegration: ethers.Contract | null;
    testToken: ethers.Contract | null;
  };
}

const BlockchainContext = createContext<BlockchainContextType | undefined>(undefined);

interface BlockchainProviderProps {
  children: ReactNode;
}

export function BlockchainProvider({ children }: BlockchainProviderProps) {
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [provider, setProvider] = useState<Web3Provider | null>(null);
  const [signer, setSigner] = useState<ethers.Signer | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contracts, setContracts] = useState<{
    tokenizedAsset: ethers.Contract | null;
    portfolioManager: ethers.Contract | null;
    tradingPlatform: ethers.Contract | null;
    defiIntegration: ethers.Contract | null;
    testToken: ethers.Contract | null;
  }>({
    tokenizedAsset: null,
    portfolioManager: null,
    tradingPlatform: null,
    defiIntegration: null,
    testToken: null,
  });

  const connectWallet = async () => {
    // Use type assertion to handle window.ethereum
    if (!(window as any).ethereum) {
      setError('No Ethereum wallet found. Please install MetaMask or another wallet.');
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Activate the injected connector
      await injected.activate();
      
      // Get provider and signer
      const provider = new ethers.providers.Web3Provider((window as any).ethereum);
      setProvider(provider);
      
      const signer = provider.getSigner();
      setSigner(signer);
      
      // Get account and chain ID
      const accounts = await provider.listAccounts();
      setAccount(accounts[0]);
      
      const { chainId } = await provider.getNetwork();
      setChainId(chainId);
      
      // Initialize contracts
      initializeContracts(provider);
      
      // Listen for account and chain changes
      (window as any).ethereum.on('accountsChanged', handleAccountsChanged);
      (window as any).ethereum.on('chainChanged', handleChainChanged);
    } catch (err) {
      console.error('Error connecting wallet:', err);
      setError('Failed to connect wallet. Please try again.');
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectWallet = () => {
    if ((window as any).ethereum) {
      (window as any).ethereum.removeListener('accountsChanged', handleAccountsChanged);
      (window as any).ethereum.removeListener('chainChanged', handleChainChanged);
    }
    
    setAccount(null);
    setChainId(null);
    setProvider(null);
    setSigner(null);
    setContracts({
      tokenizedAsset: null,
      portfolioManager: null,
      tradingPlatform: null,
      defiIntegration: null,
      testToken: null,
    });
  };

  const handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length === 0) {
      // User disconnected their wallet
      disconnectWallet();
    } else {
      setAccount(accounts[0]);
    }
  };

  const handleChainChanged = (chainIdHex: string) => {
    // Chain ID is provided as a hexadecimal string
    const newChainId = parseInt(chainIdHex, 16);
    setChainId(newChainId);
    
    // Refresh the page to ensure all state is updated correctly
    window.location.reload();
  };

  const initializeContracts = (provider: Web3Provider) => {
    try {
      const signer = provider.getSigner();
      
      const tokenizedAsset = new ethers.Contract(
        CONTRACT_ADDRESSES.TokenizedAsset,
        TokenizedAssetABI,
        signer
      );
      
      const portfolioManager = new ethers.Contract(
        CONTRACT_ADDRESSES.PortfolioManager,
        PortfolioManagerABI,
        signer
      );
      
      const tradingPlatform = new ethers.Contract(
        CONTRACT_ADDRESSES.TradingPlatform,
        TradingPlatformABI,
        signer
      );
      
      const defiIntegration = new ethers.Contract(
        CONTRACT_ADDRESSES.DeFiIntegration,
        DeFiIntegrationABI,
        signer
      );
      
      const testToken = new ethers.Contract(
        CONTRACT_ADDRESSES.TestToken,
        TestTokenABI,
        signer
      );
      
      setContracts({
        tokenizedAsset,
        portfolioManager,
        tradingPlatform,
        defiIntegration,
        testToken,
      });
    } catch (err) {
      console.error('Error initializing contracts:', err);
      setError('Failed to initialize blockchain contracts.');
    }
  };

  // Check if wallet is already connected on component mount
  useEffect(() => {
    const checkConnection = async () => {
      if ((window as any).ethereum && (window as any).ethereum.isConnected && (window as any).ethereum.selectedAddress) {
        connectWallet();
      }
    };
    
    checkConnection();
    
    return () => {
      // Clean up event listeners
      if ((window as any).ethereum) {
        (window as any).ethereum.removeListener('accountsChanged', handleAccountsChanged);
        (window as any).ethereum.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, []);

  const value = {
    account,
    chainId,
    provider,
    signer,
    isConnected: !!account,
    isConnecting,
    error,
    connectWallet,
    disconnectWallet,
    contracts,
  };

  return <BlockchainContext.Provider value={value}>{children}</BlockchainContext.Provider>;
}

export function useBlockchain() {
  const context = useContext(BlockchainContext);
  
  if (context === undefined) {
    throw new Error('useBlockchain must be used within a BlockchainProvider');
  }
  
  return context;
}
