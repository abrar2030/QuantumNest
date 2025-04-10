import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function BlockchainExplorer({ darkMode, toggleDarkMode }) {
  // Mock data for blockchain transactions
  const transactionData = [
    { day: '04/03', count: 125, volume: 2.5 },
    { day: '04/04', count: 145, volume: 3.2 },
    { day: '04/05', count: 135, volume: 2.8 },
    { day: '04/06', count: 160, volume: 3.5 },
    { day: '04/07', count: 180, volume: 4.1 },
    { day: '04/08', count: 170, volume: 3.8 },
    { day: '04/09', count: 190, volume: 4.3 },
  ];

  // Mock data for smart contracts
  const smartContracts = [
    {
      address: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
      name: "QuantumNest Trading",
      type: "Trading Contract",
      transactions: 1245,
      value: "125.45 ETH",
      status: "Active"
    },
    {
      address: "0x8901DaECbfF9e1d2c7b9C2a154b9dAc45a1B5092",
      name: "Asset Tokenization",
      type: "Token Contract",
      transactions: 876,
      value: "98.32 ETH",
      status: "Active"
    },
    {
      address: "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
      name: "Portfolio Management",
      type: "Management Contract",
      transactions: 542,
      value: "76.18 ETH",
      status: "Active"
    },
    {
      address: "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
      name: "Yield Optimization",
      type: "Yield Contract",
      transactions: 328,
      value: "45.67 ETH",
      status: "Active"
    },
    {
      address: "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
      name: "Risk Management",
      type: "Insurance Contract",
      transactions: 215,
      value: "32.91 ETH",
      status: "Active"
    }
  ];

  // Mock data for recent transactions
  const recentTransactions = [
    {
      hash: "0x7d2a5b3e8f4a1b9c6d8e7f0a2b3c4d5e6f7a8b9c",
      from: "0x742d...f44e",
      to: "0x8901...5092",
      value: "1.25 ETH",
      timestamp: "2 mins ago",
      status: "Confirmed"
    },
    {
      hash: "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
      from: "0x3C44...3BC",
      to: "0x742d...f44e",
      value: "0.75 ETH",
      timestamp: "15 mins ago",
      status: "Confirmed"
    },
    {
      hash: "0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b",
      from: "0x90F7...906",
      to: "0x15d3...A65",
      value: "2.50 ETH",
      timestamp: "32 mins ago",
      status: "Confirmed"
    },
    {
      hash: "0x2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
      from: "0x8901...5092",
      to: "0x3C44...3BC",
      value: "0.45 ETH",
      timestamp: "1 hour ago",
      status: "Confirmed"
    },
    {
      hash: "0x5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b",
      from: "0x15d3...A65",
      to: "0x90F7...906",
      value: "1.80 ETH",
      timestamp: "2 hours ago",
      status: "Confirmed"
    }
  ];

  // Mock data for blockchain stats
  const blockchainStats = [
    { name: "Total Transactions", value: "12,456" },
    { name: "Active Smart Contracts", value: "32" },
    { name: "Total Value Locked", value: "378.45 ETH" },
    { name: "Average Gas Price", value: "25 Gwei" },
    { name: "Network", value: "Goerli Testnet" }
  ];

  // State for transaction search
  const [searchTx, setSearchTx] = useState("");
  const [searchAddress, setSearchAddress] = useState("");

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Blockchain Explorer</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Explore blockchain transactions, smart contracts, and real-time network activity.
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="tx-search" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Transaction Hash
              </label>
              <div className="flex">
                <input
                  type="text"
                  id="tx-search"
                  className="flex-1 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 py-2 px-3 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter transaction hash"
                  value={searchTx}
                  onChange={(e) => setSearchTx(e.target.value)}
                />
                <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-r-md transition-colors duration-300">
                  Search
                </button>
              </div>
            </div>
            <div>
              <label htmlFor="address-search" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Wallet or Contract Address
              </label>
              <div className="flex">
                <input
                  type="text"
                  id="address-search"
                  className="flex-1 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 py-2 px-3 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter wallet or contract address"
                  value={searchAddress}
                  onChange={(e) => setSearchAddress(e.target.value)}
                />
                <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-r-md transition-colors duration-300">
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Blockchain Stats */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Blockchain Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {blockchainStats.map((stat, index) => (
              <div key={index} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.name}</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Transaction Activity Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Transaction Activity (Last 7 Days)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={transactionData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="count" stroke="#8884d8" name="Transaction Count" activeDot={{ r: 8 }} />
                <Line yAxisId="right" type="monotone" dataKey="volume" stroke="#82ca9d" name="Volume (ETH)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Smart Contracts */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Smart Contracts</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Contract Address</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Transactions</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Value</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {smartContracts.map((contract, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline">
                      {contract.address}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{contract.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{contract.type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{contract.transactions}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{contract.value}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        {contract.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-center">
            <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              View All Smart Contracts
            </button>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Recent Transactions</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Transaction Hash</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">From</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">To</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Value</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Time</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {recentTransactions.map((tx, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline">
                      {tx.hash.substring(0, 10)}...{tx.hash.substring(tx.hash.length - 8)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{tx.from}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{tx.to}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{tx.value}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{tx.timestamp}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        {tx.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-center">
            <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              View All Transactions
            </button>
          </div>
        </div>

        {/* Connect Wallet */}
        <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl shadow-lg p-6 mb-8">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">Connect Your Wallet</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Connect your Ethereum wallet to interact with smart contracts and manage your assets.
            </p>
            <button className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-300">
              Connect Wallet
            </button>
          </div>
        </div>

        {/* Blockchain Features */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-6 text-center">Blockchain Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">Secure Transactions</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                All transactions are secured by Ethereum blockchain technology, ensuring transparency and immutability.
              </p>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">Smart Contracts</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Automated, self-executing contracts with the terms directly written into code, eliminating intermediaries.
              </p>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center mb-3">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 dark:text-white">Digital Assets</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Tokenized assets provide liquidity, fractional ownership, and seamless transfer of value across the platform.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
