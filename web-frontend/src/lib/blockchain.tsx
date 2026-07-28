"use client";

import { ethers } from "ethers";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

interface EthereumProvider {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener: (event: string, handler: (...args: unknown[]) => void) => void;
}

declare global {
  interface Window {
    ethereum?: EthereumProvider;
  }
}

interface BlockchainContextType {
  provider: ethers.providers.Web3Provider | null;
  signer: ethers.Signer | null;
  account: string | null;
  chainId: number | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  getBalance: () => Promise<string>;
  sendTransaction: (
    to: string,
    amount: string,
  ) => Promise<ethers.providers.TransactionResponse>;
}

const BlockchainContext = createContext<BlockchainContextType | undefined>(
  undefined,
);

export function BlockchainProvider({ children }: { children: ReactNode }) {
  const [provider, setProvider] = useState<ethers.providers.Web3Provider | null>(
    null,
  );
  const [signer, setSigner] = useState<ethers.Signer | null>(null);
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const disconnectWallet = useCallback(() => {
    setProvider(null);
    setSigner(null);
    setAccount(null);
    setChainId(null);
    setIsConnected(false);
    setError(null);
  }, []);

  const connectWallet = useCallback(async () => {
    if (typeof window === "undefined" || !window.ethereum) {
      setError(
        "No wallet extension detected. Install MetaMask (or a compatible wallet) to connect.",
      );
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      await window.ethereum.request({ method: "eth_requestAccounts" });

      const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
      setProvider(web3Provider);

      const web3Signer = web3Provider.getSigner();
      setSigner(web3Signer);

      const address = await web3Signer.getAddress();
      setAccount(address);

      const network = await web3Provider.getNetwork();
      setChainId(network.chainId);

      setIsConnected(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to connect wallet";
      setError(message);
      setIsConnected(false);
    } finally {
      setIsConnecting(false);
    }
  }, []);

  // Reconnect silently if the wallet extension already has an authorized session.
  useEffect(() => {
    if (typeof window === "undefined" || !window.ethereum) return;

    let cancelled = false;

    async function checkExistingConnection() {
      try {
        const web3Provider = new ethers.providers.Web3Provider(window.ethereum!);
        const accounts = await web3Provider.listAccounts();
        if (cancelled || accounts.length === 0) return;

        setProvider(web3Provider);
        const web3Signer = web3Provider.getSigner();
        setSigner(web3Signer);
        setAccount(accounts[0]);
        const network = await web3Provider.getNetwork();
        setChainId(network.chainId);
        setIsConnected(true);
      } catch {
        // No existing session — this is expected on first visit.
      }
    }

    checkExistingConnection();

    function handleAccountsChanged(...args: unknown[]) {
      const accounts = args[0] as string[];
      if (accounts.length > 0) {
        setAccount(accounts[0]);
      } else {
        disconnectWallet();
      }
    }

    function handleChainChanged() {
      window.location.reload();
    }

    window.ethereum.on("accountsChanged", handleAccountsChanged);
    window.ethereum.on("chainChanged", handleChainChanged);

    return () => {
      cancelled = true;
      window.ethereum?.removeListener("accountsChanged", handleAccountsChanged);
      window.ethereum?.removeListener("chainChanged", handleChainChanged);
    };
  }, [disconnectWallet]);

  const getBalance = useCallback(async (): Promise<string> => {
    if (!provider || !account) {
      throw new Error("Wallet not connected");
    }
    const balance = await provider.getBalance(account);
    return ethers.utils.formatEther(balance);
  }, [provider, account]);

  const sendTransaction = useCallback(
    async (to: string, amount: string) => {
      if (!signer) {
        throw new Error("Wallet not connected");
      }
      return signer.sendTransaction({
        to,
        value: ethers.utils.parseEther(amount),
      });
    },
    [signer],
  );

  const value: BlockchainContextType = {
    provider,
    signer,
    account,
    chainId,
    isConnected,
    isConnecting,
    error,
    connectWallet,
    disconnectWallet,
    getBalance,
    sendTransaction,
  };

  return (
    <BlockchainContext.Provider value={value}>{children}</BlockchainContext.Provider>
  );
}

export function useBlockchain() {
  const context = useContext(BlockchainContext);
  if (context === undefined) {
    throw new Error("useBlockchain must be used within a BlockchainProvider");
  }
  return context;
}
