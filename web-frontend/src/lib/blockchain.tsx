// lib/blockchain.tsx - Enhanced implementation

import Web3 from 'web3';
import { AbiItem } from 'web3-utils';
import { Contract } from 'web3-eth-contract';

// Contract ABIs
import PortfolioManagerABI from '../contracts/PortfolioManager.json';
import TokenizedAssetABI from '../contracts/TokenizedAsset.json';
import DeFiIntegrationABI from '../contracts/DeFiIntegration.json';
import TradingPlatformABI from '../contracts/TradingPlatform.json';

// Contract addresses (these would typically be environment variables)
const PORTFOLIO_MANAGER_ADDRESS = process.env.NEXT_PUBLIC_PORTFOLIO_MANAGER_ADDRESS || '0x123...';
const TOKENIZED_ASSET_ADDRESS = process.env.NEXT_PUBLIC_TOKENIZED_ASSET_ADDRESS || '0x456...';
const DEFI_INTEGRATION_ADDRESS = process.env.NEXT_PUBLIC_DEFI_INTEGRATION_ADDRESS || '0x789...';
const TRADING_PLATFORM_ADDRESS = process.env.NEXT_PUBLIC_TRADING_PLATFORM_ADDRESS || '0xabc...';

// Interface for blockchain transaction options
interface TransactionOptions {
  from?: string;
  gas?: number;
  gasPrice?: string;
  value?: number | string;
}

// Interface for portfolio asset
export interface PortfolioAsset {
  id: string;
  name: string;
  symbol: string;
  quantity: number;
  value: number;
  tokenAddress?: string;
}

// Interface for transaction data
export interface TransactionData {
  hash: string;
  from: string;
  to: string;
  value: string;
  timestamp: number;
  status: 'pending' | 'confirmed' | 'failed';
  blockNumber?: number;
  gasUsed?: number;
}

class BlockchainService {
  private web3: Web3 | null = null;
  private portfolioManagerContract: Contract | null = null;
  private tokenizedAssetContract: Contract | null = null;
  private defiIntegrationContract: Contract | null = null;
  private tradingPlatformContract: Contract | null = null;
  private account: string | null = null;
  private networkId: number | null = null;
  private isInitialized: boolean = false;

  // Initialize Web3 and contracts
  async initialize(): Promise<boolean> {
    try {
      if (typeof window !== 'undefined' && typeof window.ethereum !== 'undefined') {
        // Modern dapp browsers
        this.web3 = new Web3(window.ethereum);
        try {
          // Request account access
          await window.ethereum.request({ method: 'eth_requestAccounts' });
          
          // Get the connected account
          const accounts = await this.web3.eth.getAccounts();
          this.account = accounts[0];
          
          // Get network ID
          this.networkId = await this.web3.eth.net.getId();
          
          // Initialize contracts
          this.initializeContracts();
          
          // Listen for account changes
          window.ethereum.on('accountsChanged', (accounts: string[]) => {
            this.account = accounts[0];
            this.handleAccountChange(accounts[0]);
          });
          
          // Listen for network changes
          window.ethereum.on('chainChanged', (chainId: string) => {
            window.location.reload();
          });
          
          this.isInitialized = true;
          return true;
        } catch (error) {
          console.error('User denied account access:', error);
          return false;
        }
      } else if (typeof window !== 'undefined' && typeof window.web3 !== 'undefined') {
        // Legacy dapp browsers
        this.web3 = new Web3(window.web3.currentProvider);
        
        // Get the connected account
        const accounts = await this.web3.eth.getAccounts();
        this.account = accounts[0];
        
        // Get network ID
        this.networkId = await this.web3.eth.net.getId();
        
        // Initialize contracts
        this.initializeContracts();
        
        this.isInitialized = true;
        return true;
      } else {
        // Fallback to a public provider
        const provider = new Web3.providers.HttpProvider(
          'https://mainnet.infura.io/v3/your-infura-project-id'
        );
        this.web3 = new Web3(provider);
        
        // Get network ID
        this.networkId = await this.web3.eth.net.getId();
        
        // Initialize contracts
        this.initializeContracts();
        
        this.isInitialized = true;
        return true;
      }
    } catch (error) {
      console.error('Error initializing blockchain service:', error);
      return false;
    }
  }

  // Initialize smart contracts
  private initializeContracts(): void {
    if (!this.web3) return;
    
    this.portfolioManagerContract = new this.web3.eth.Contract(
      PortfolioManagerABI.abi as AbiItem[],
      PORTFOLIO_MANAGER_ADDRESS
    );
    
    this.tokenizedAssetContract = new this.web3.eth.Contract(
      TokenizedAssetABI.abi as AbiItem[],
      TOKENIZED_ASSET_ADDRESS
    );
    
    this.defiIntegrationContract = new this.web3.eth.Contract(
      DeFiIntegrationABI.abi as AbiItem[],
      DEFI_INTEGRATION_ADDRESS
    );
    
    this.tradingPlatformContract = new this.web3.eth.Contract(
      TradingPlatformABI.abi as AbiItem[],
      TRADING_PLATFORM_ADDRESS
    );
  }

  // Handle account change
  private handleAccountChange(account: string): void {
    this.account = account;
    // Emit event or callback for UI update
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('accountChanged', { detail: account });
      window.dispatchEvent(event);
    }
  }

  // Check if blockchain service is initialized
  isConnected(): boolean {
    return this.isInitialized && !!this.account;
  }

  // Get current account
  getAccount(): string | null {
    return this.account;
  }

  // Get network ID
  getNetworkId(): number | null {
    return this.networkId;
  }

  // Get network name based on ID
  getNetworkName(): string {
    if (!this.networkId) return 'Unknown';
    
    switch (this.networkId) {
      case 1:
        return 'Ethereum Mainnet';
      case 3:
        return 'Ropsten Testnet';
      case 4:
        return 'Rinkeby Testnet';
      case 5:
        return 'Goerli Testnet';
      case 42:
        return 'Kovan Testnet';
      case 56:
        return 'Binance Smart Chain';
      case 137:
        return 'Polygon Mainnet';
      default:
        return `Unknown (${this.networkId})`;
    }
  }

  // Connect wallet
  async connectWallet(): Promise<string | null> {
    if (!this.web3) {
      const initialized = await this.initialize();
      if (!initialized) return null;
    }
    
    if (typeof window !== 'undefined' && typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        this.account = accounts[0];
        return this.account;
      } catch (error) {
        console.error('Error connecting wallet:', error);
        return null;
      }
    }
    
    return null;
  }

  // Disconnect wallet (for UI purposes)
  disconnectWallet(): void {
    this.account = null;
    // Emit event or callback for UI update
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('walletDisconnected');
      window.dispatchEvent(event);
    }
  }

  // Get user portfolio
  async getUserPortfolio(): Promise<PortfolioAsset[]> {
    if (!this.isConnected() || !this.portfolioManagerContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const portfolioCount = await this.portfolioManagerContract.methods.getUserPortfolioCount(this.account).call();
      const portfolio: PortfolioAsset[] = [];
      
      for (let i = 0; i < portfolioCount; i++) {
        const asset = await this.portfolioManagerContract.methods.getUserPortfolioAsset(this.account, i).call();
        portfolio.push({
          id: asset.id,
          name: asset.name,
          symbol: asset.symbol,
          quantity: parseFloat(this.web3!.utils.fromWei(asset.quantity, 'ether')),
          value: parseFloat(this.web3!.utils.fromWei(asset.value, 'ether')),
          tokenAddress: asset.tokenAddress
        });
      }
      
      return portfolio;
    } catch (error) {
      console.error('Error fetching user portfolio:', error);
      throw error;
    }
  }

  // Buy asset
  async buyAsset(symbol: string, quantity: number, options?: TransactionOptions): Promise<string> {
    if (!this.isConnected() || !this.tradingPlatformContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const quantityWei = this.web3!.utils.toWei(quantity.toString(), 'ether');
      const tx = await this.tradingPlatformContract.methods.buyAsset(symbol, quantityWei).send({
        from: this.account,
        ...options
      });
      
      return tx.transactionHash;
    } catch (error) {
      console.error('Error buying asset:', error);
      throw error;
    }
  }

  // Sell asset
  async sellAsset(symbol: string, quantity: number, options?: TransactionOptions): Promise<string> {
    if (!this.isConnected() || !this.tradingPlatformContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const quantityWei = this.web3!.utils.toWei(quantity.toString(), 'ether');
      const tx = await this.tradingPlatformContract.methods.sellAsset(symbol, quantityWei).send({
        from: this.account,
        ...options
      });
      
      return tx.transactionHash;
    } catch (error) {
      console.error('Error selling asset:', error);
      throw error;
    }
  }

  // Stake tokens in DeFi protocol
  async stakeTokens(amount: number, options?: TransactionOptions): Promise<string> {
    if (!this.isConnected() || !this.defiIntegrationContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const amountWei = this.web3!.utils.toWei(amount.toString(), 'ether');
      const tx = await this.defiIntegrationContract.methods.stake(amountWei).send({
        from: this.account,
        ...options
      });
      
      return tx.transactionHash;
    } catch (error) {
      console.error('Error staking tokens:', error);
      throw error;
    }
  }

  // Unstake tokens from DeFi protocol
  async unstakeTokens(amount: number, options?: TransactionOptions): Promise<string> {
    if (!this.isConnected() || !this.defiIntegrationContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const amountWei = this.web3!.utils.toWei(amount.toString(), 'ether');
      const tx = await this.defiIntegrationContract.methods.unstake(amountWei).send({
        from: this.account,
        ...options
      });
      
      return tx.transactionHash;
    } catch (error) {
      console.error('Error unstaking tokens:', error);
      throw error;
    }
  }

  // Get staking rewards
  async getStakingRewards(): Promise<number> {
    if (!this.isConnected() || !this.defiIntegrationContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const rewards = await this.defiIntegrationContract.methods.getRewards(this.account).call();
      return parseFloat(this.web3!.utils.fromWei(rewards, 'ether'));
    } catch (error) {
      console.error('Error getting staking rewards:', error);
      throw error;
    }
  }

  // Claim staking rewards
  async claimRewards(options?: TransactionOptions): Promise<string> {
    if (!this.isConnected() || !this.defiIntegrationContract || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const tx = await this.defiIntegrationContract.methods.claimRewards().send({
        from: this.account,
        ...options
      });
      
      return tx.transactionHash;
    } catch (error) {
      console.error('Error claiming rewards:', error);
      throw error;
    }
  }

  // Get transaction history
  async getTransactionHistory(limit: number = 10): Promise<TransactionData[]> {
    if (!this.isConnected() || !this.web3 || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      // Get the latest block number
      const latestBlock = await this.web3.eth.getBlockNumber();
      
      // Get transactions from the last 1000 blocks (adjust as needed)
      const fromBlock = Math.max(0, latestBlock - 1000);
      
      // Get transactions for the current account
      const transactions: TransactionData[] = [];
      
      // This is a simplified approach - in a real app, you'd use an indexer or API
      for (let i = latestBlock; i >= fromBlock && transactions.length < limit; i--) {
        const block = await this.web3.eth.getBlock(i, true);
        
        if (block && block.transactions) {
          for (const tx of block.transactions) {
            if (typeof tx === 'object' && 
                (tx.from.toLowerCase() === this.account.toLowerCase() || 
                 tx.to?.toLowerCase() === this.account.toLowerCase())) {
              
              const receipt = await this.web3.eth.getTransactionReceipt(tx.hash);
              
              transactions.push({
                hash: tx.hash,
                from: tx.from,
                to: tx.to || '',
                value: this.web3.utils.fromWei(tx.value, 'ether'),
                timestamp: block.timestamp as number,
                status: receipt.status ? 'confirmed' : 'failed',
                blockNumber: tx.blockNumber,
                gasUsed: receipt.gasUsed
              });
              
              if (transactions.length >= limit) break;
            }
          }
        }
      }
      
      return transactions;
    } catch (error) {
      console.error('Error fetching transaction history:', error);
      throw error;
    }
  }

  // Get token balance
  async getTokenBalance(tokenAddress: string): Promise<number> {
    if (!this.isConnected() || !this.web3 || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const tokenContract = new this.web3.eth.Contract(
        [
          {
            constant: true,
            inputs: [{ name: '_owner', type: 'address' }],
            name: 'balanceOf',
            outputs: [{ name: 'balance', type: 'uint256' }],
            type: 'function'
          }
        ] as AbiItem[],
        tokenAddress
      );
      
      const balance = await tokenContract.methods.balanceOf(this.account).call();
      return parseFloat(this.web3.utils.fromWei(balance, 'ether'));
    } catch (error) {
      console.error('Error getting token balance:', error);
      throw error;
    }
  }

  // Get ETH balance
  async getEthBalance(): Promise<number> {
    if (!this.isConnected() || !this.web3 || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const balance = await this.web3.eth.getBalance(this.account);
      return parseFloat(this.web3.utils.fromWei(balance, 'ether'));
    } catch (error) {
      console.error('Error getting ETH balance:', error);
      throw error;
    }
  }

  // Sign message (for authentication)
  async signMessage(message: string): Promise<string> {
    if (!this.isConnected() || !this.web3 || !this.account) {
      throw new Error('Blockchain service not initialized or not connected');
    }
    
    try {
      const signature = await this.web3.eth.personal.sign(
        message,
        this.account,
        '' // Password is not needed for MetaMask
      );
      
      return signature;
    } catch (error) {
      console.error('Error signing message:', error);
      throw error;
    }
  }

  // Verify signature
  async verifySignature(message: string, signature: string, address: string): Promise<boolean> {
    if (!this.web3) {
      throw new Error('Blockchain service not initialized');
    }
    
    try {
      const recoveredAddress = await this.web3.eth.personal.ecRecover(message, signature);
      return recoveredAddress.toLowerCase() === address.toLowerCase();
    } catch (error) {
      console.error('Error verifying signature:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const blockchainService = new BlockchainService();
export default blockchainService;
