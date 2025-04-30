import React, { useState, useEffect } from 'react';
import { useWallet } from './WalletProvider';
import { ethers } from 'ethers';

const BlockchainExplorer = () => {
  const { library, account, network, chainId, connected } = useWallet();
  
  const [view, setView] = useState('transactions'); // 'transactions', 'blocks', 'contracts'
  const [transactions, setTransactions] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [contractData, setContractData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('address'); // 'address', 'tx', 'block', 'token'
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Contract addresses (would be imported from config in production)
  const contractAddresses = {
    TokenizedAsset: '0x123...', // Replace with actual deployed address
    PortfolioManager: '0x456...', // Replace with actual deployed address
    TradingPlatform: '0x789...', // Replace with actual deployed address
    DeFiIntegration: '0xabc...', // Replace with actual deployed address
  };
  
  // Fetch recent transactions
  const fetchRecentTransactions = async () => {
    if (!library || !connected) return;
    
    try {
      setLoading(true);
      
      // Get latest block number
      const blockNumber = await library.getBlockNumber();
      
      // Fetch last 10 blocks
      const blockPromises = [];
      for (let i = 0; i < 10; i++) {
        if (blockNumber - i >= 0) {
          blockPromises.push(library.getBlockWithTransactions(blockNumber - i));
        }
      }
      
      const blocks = await Promise.all(blockPromises);
      
      // Extract transactions
      let allTransactions = [];
      blocks.forEach(block => {
        // Add block timestamp to each transaction
        const txsWithTimestamp = block.transactions.map(tx => ({
          ...tx,
          blockTimestamp: new Date(block.timestamp * 1000),
          blockNumber: block.number
        }));
        allTransactions = [...allTransactions, ...txsWithTimestamp];
      });
      
      // Sort by timestamp (newest first)
      allTransactions.sort((a, b) => b.blockTimestamp - a.blockTimestamp);
      
      // Take only the first 20
      setTransactions(allTransactions.slice(0, 20));
      setLoading(false);
    } catch (error) {
      console.error("Error fetching transactions:", error);
      setError("Failed to fetch recent transactions");
      setLoading(false);
    }
  };
  
  // Fetch recent blocks
  const fetchRecentBlocks = async () => {
    if (!library || !connected) return;
    
    try {
      setLoading(true);
      
      // Get latest block number
      const blockNumber = await library.getBlockNumber();
      
      // Fetch last 10 blocks
      const blockPromises = [];
      for (let i = 0; i < 10; i++) {
        if (blockNumber - i >= 0) {
          blockPromises.push(library.getBlock(blockNumber - i));
        }
      }
      
      const fetchedBlocks = await Promise.all(blockPromises);
      setBlocks(fetchedBlocks);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching blocks:", error);
      setError("Failed to fetch recent blocks");
      setLoading(false);
    }
  };
  
  // Fetch contract data
  const fetchContractData = async (contractAddress) => {
    if (!library || !connected || !contractAddress) return;
    
    try {
      setLoading(true);
      
      // Get contract code
      const code = await library.getCode(contractAddress);
      
      // Get transaction count
      const txCount = await library.getTransactionCount(contractAddress);
      
      // Get balance
      const balance = await library.getBalance(contractAddress);
      
      setContractData({
        address: contractAddress,
        code: code,
        codeSize: (code.length - 2) / 2, // Remove '0x' and divide by 2 for byte count
        txCount: txCount,
        balance: ethers.utils.formatEther(balance)
      });
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching contract data:", error);
      setError("Failed to fetch contract data");
      setLoading(false);
    }
  };
  
  // Handle search
  const handleSearch = async () => {
    if (!searchQuery || !library || !connected) return;
    
    try {
      setSearchLoading(true);
      setError(null);
      
      let result = null;
      
      if (searchType === 'address') {
        // Check if address is valid
        if (!ethers.utils.isAddress(searchQuery)) {
          throw new Error("Invalid Ethereum address");
        }
        
        // Get address details
        const code = await library.getCode(searchQuery);
        const txCount = await library.getTransactionCount(searchQuery);
        const balance = await library.getBalance(searchQuery);
        
        result = {
          type: 'address',
          address: searchQuery,
          isContract: code !== '0x',
          txCount: txCount,
          balance: ethers.utils.formatEther(balance)
        };
        
        if (code !== '0x') {
          result.codeSize = (code.length - 2) / 2;
        }
      } else if (searchType === 'tx') {
        // Get transaction details
        const tx = await library.getTransaction(searchQuery);
        
        if (!tx) {
          throw new Error("Transaction not found");
        }
        
        // Get transaction receipt
        const receipt = await library.getTransactionReceipt(searchQuery);
        
        // Get block for timestamp
        const block = await library.getBlock(tx.blockNumber);
        
        result = {
          type: 'transaction',
          hash: tx.hash,
          from: tx.from,
          to: tx.to,
          value: ethers.utils.formatEther(tx.value),
          blockNumber: tx.blockNumber,
          timestamp: new Date(block.timestamp * 1000),
          status: receipt ? (receipt.status ? 'Success' : 'Failed') : 'Pending',
          gasUsed: receipt ? receipt.gasUsed.toString() : 'N/A'
        };
      } else if (searchType === 'block') {
        // Check if input is a number
        const blockNumber = parseInt(searchQuery);
        
        if (isNaN(blockNumber)) {
          throw new Error("Invalid block number");
        }
        
        // Get block details
        const block = await library.getBlock(blockNumber);
        
        if (!block) {
          throw new Error("Block not found");
        }
        
        result = {
          type: 'block',
          number: block.number,
          hash: block.hash,
          timestamp: new Date(block.timestamp * 1000),
          transactions: block.transactions.length,
          gasUsed: block.gasUsed.toString(),
          gasLimit: block.gasLimit.toString(),
          miner: block.miner
        };
      } else if (searchType === 'token') {
        // Check if address is valid
        if (!ethers.utils.isAddress(searchQuery)) {
          throw new Error("Invalid token address");
        }
        
        // Create ERC20 interface
        const erc20Interface = new ethers.utils.Interface([
          "function name() view returns (string)",
          "function symbol() view returns (string)",
          "function decimals() view returns (uint8)",
          "function totalSupply() view returns (uint256)"
        ]);
        
        // Create contract instance
        const tokenContract = new ethers.Contract(searchQuery, erc20Interface, library);
        
        try {
          // Try to get token details
          const [name, symbol, decimals, totalSupply] = await Promise.all([
            tokenContract.name(),
            tokenContract.symbol(),
            tokenContract.decimals(),
            tokenContract.totalSupply()
          ]);
          
          result = {
            type: 'token',
            address: searchQuery,
            name: name,
            symbol: symbol,
            decimals: decimals,
            totalSupply: ethers.utils.formatUnits(totalSupply, decimals)
          };
        } catch (error) {
          throw new Error("Not a valid ERC20 token");
        }
      }
      
      setSearchResults(result);
      setSearchLoading(false);
    } catch (error) {
      console.error("Search error:", error);
      setError(error.message || "Search failed");
      setSearchResults(null);
      setSearchLoading(false);
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return timestamp.toLocaleString();
  };
  
  // Format address
  const formatAddress = (address) => {
    if (!address) return 'N/A';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };
  
  // Load data based on selected view
  useEffect(() => {
    if (view === 'transactions') {
      fetchRecentTransactions();
    } else if (view === 'blocks') {
      fetchRecentBlocks();
    } else if (view === 'contracts') {
      // Default to first contract in the list
      const firstContract = Object.values(contractAddresses)[0];
      if (firstContract) {
        fetchContractData(firstContract);
      }
    }
  }, [view, connected, library, chainId]);
  
  // Render loading state
  if (!connected) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="text-center py-10">
          <p className="text-gray-600 dark:text-gray-400">Please connect your wallet to use the blockchain explorer</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Blockchain Explorer</h2>
      
      {/* Network info */}
      <div className="mb-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <div className="flex flex-wrap items-center justify-between">
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Network: </span>
            <span className="font-medium text-gray-900 dark:text-white">
              {network ? network.charAt(0).toUpperCase() + network.slice(1) : 'Unknown'}
            </span>
          </div>
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Chain ID: </span>
            <span className="font-medium text-gray-900 dark:text-white">{chainId || 'Unknown'}</span>
          </div>
          <div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Connected Account: </span>
            <span className="font-medium text-gray-900 dark:text-white">
              {account ? formatAddress(account) : 'None'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Search bar */}
      <div className="mb-6">
        <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by address, transaction hash, block number, or token address"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div className="flex space-x-2">
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="address">Address</option>
              <option value="tx">Transaction</option>
              <option value="block">Block</option>
              <option value="token">Token</option>
            </select>
            <button
              onClick={handleSearch}
              disabled={searchLoading || !searchQuery}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {searchLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Search results */}
      {searchResults && (
        <div className="mb-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Search Results</h3>
          
          {searchResults.type === 'address' && (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Address:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.address}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Type:</span>
                <span className="text-gray-900 dark:text-white">
                  {searchResults.isContract ? 'Contract' : 'EOA (Externally Owned Account)'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Balance:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.balance} ETH</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Transaction Count:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.txCount}</span>
              </div>
              {searchResults.isContract && (
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Code Size:</span>
                  <span className="text-gray-900 dark:text-white">{searchResults.codeSize} bytes</span>
                </div>
              )}
            </div>
          )}
          
          {searchResults.type === 'transaction' && (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Hash:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.hash}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">From:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.from}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">To:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.to || 'Contract Creation'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Value:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.value} ETH</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Block:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.blockNumber}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Timestamp:</span>
                <span className="text-gray-900 dark:text-white">{formatTimestamp(searchResults.timestamp)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Status:</span>
                <span className={`${
                  searchResults.status === 'Success' ? 'text-green-600 dark:text-green-400' : 
                  searchResults.status === 'Failed' ? 'text-red-600 dark:text-red-400' : 
                  'text-yellow-600 dark:text-yellow-400'
                }`}>
                  {searchResults.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Gas Used:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.gasUsed}</span>
              </div>
            </div>
          )}
          
          {searchResults.type === 'block' && (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Block Number:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Hash:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.hash}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Timestamp:</span>
                <span className="text-gray-900 dark:text-white">{formatTimestamp(searchResults.timestamp)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Transactions:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.transactions}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Gas Used:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.gasUsed}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Gas Limit:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.gasLimit}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Miner:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.miner}</span>
              </div>
            </div>
          )}
          
          {searchResults.type === 'token' && (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Token Address:</span>
                <span className="font-mono text-gray-900 dark:text-white">{searchResults.address}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Name:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Symbol:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Decimals:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.decimals}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Total Supply:</span>
                <span className="text-gray-900 dark:text-white">{searchResults.totalSupply}</span>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-800 rounded-lg">
          {error}
        </div>
      )}
      
      {/* View selector */}
      <div className="mb-6">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            className={`py-2 px-4 font-medium ${
              view === 'transactions' 
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setView('transactions')}
          >
            Transactions
          </button>
          <button
            className={`py-2 px-4 font-medium ${
              view === 'blocks' 
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setView('blocks')}
          >
            Blocks
          </button>
          <button
            className={`py-2 px-4 font-medium ${
              view === 'contracts' 
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setView('contracts')}
          >
            Smart Contracts
          </button>
        </div>
      </div>
      
      {/* Loading indicator */}
      {loading && (
        <div className="flex justify-center my-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
        </div>
      )}
      
      {/* Transactions view */}
      {view === 'transactions' && !loading && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Hash
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Block
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  From
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  To
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Value
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
              {transactions.length > 0 ? (
                transactions.map((tx, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-white">
                      {formatAddress(tx.hash)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {tx.blockNumber}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-white">
                      {formatAddress(tx.from)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-white">
                      {tx.to ? formatAddress(tx.to) : 'Contract Creation'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {ethers.utils.formatEther(tx.value)} ETH
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatTimestamp(tx.blockTimestamp)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                    No transactions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Blocks view */}
      {view === 'blocks' && !loading && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Number
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Hash
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Timestamp
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Transactions
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Gas Used
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Gas Limit
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
              {blocks.length > 0 ? (
                blocks.map((block, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {block.number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-white">
                      {formatAddress(block.hash)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatTimestamp(new Date(block.timestamp * 1000))}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {block.transactions.length}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {block.gasUsed.toString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {block.gasLimit.toString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                    No blocks found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Contracts view */}
      {view === 'contracts' && !loading && (
        <div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Contract
            </label>
            <select
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              onChange={(e) => fetchContractData(e.target.value)}
            >
              {Object.entries(contractAddresses).map(([name, address]) => (
                <option key={address} value={address}>
                  {name} ({formatAddress(address)})
                </option>
              ))}
            </select>
          </div>
          
          {contractData && (
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Contract Details</h3>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Address:</span>
                  <span className="font-mono text-gray-900 dark:text-white">{contractData.address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Balance:</span>
                  <span className="text-gray-900 dark:text-white">{contractData.balance} ETH</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Transaction Count:</span>
                  <span className="text-gray-900 dark:text-white">{contractData.txCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Code Size:</span>
                  <span className="text-gray-900 dark:text-white">{contractData.codeSize} bytes</span>
                </div>
              </div>
              
              <div className="mt-4">
                <h4 className="text-md font-medium mb-2 text-gray-900 dark:text-white">Contract Bytecode</h4>
                <div className="bg-gray-200 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto">
                  <pre className="text-xs font-mono text-gray-900 dark:text-white whitespace-pre-wrap break-all">
                    {contractData.code}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BlockchainExplorer;
