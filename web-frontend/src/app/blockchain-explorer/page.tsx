'use client';

import React, { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { formatCurrency, shortenAddress, formatDateWithTime } from '@/lib/utils';

export default function BlockchainExplorer() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for blockchain stats
  const blockchainStats = [
    { title: 'Latest Block', value: '18,245,632' },
    { title: 'Transactions (24h)', value: '1,245,876' },
    { title: 'Average Gas', value: '25 Gwei' },
    { title: 'Network Hashrate', value: '1.2 PH/s' },
  ];

  // Mock data for recent transactions
  const recentTransactions = [
    { 
      hash: '0x7d92f8a1b4e6c74a9b5e3a65d1e2c8f3b4e5d6c7a8b9c0d1e2f3a4b5c6d7e8f9',
      from: '0x1234567890123456789012345678901234567890',
      to: '0x0987654321098765432109876543210987654321',
      value: 1.25,
      gasUsed: 21000,
      timestamp: new Date('2025-04-13T12:45:32'),
      status: 'confirmed'
    },
    { 
      hash: '0x8c7b6a5d4e3f2c1b0a9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
      from: '0x2345678901234567890123456789012345678901',
      to: '0x1098765432109876543210987654321098765432',
      value: 0.5,
      gasUsed: 35000,
      timestamp: new Date('2025-04-13T12:42:18'),
      status: 'confirmed'
    },
    { 
      hash: '0x9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e',
      from: '0x3456789012345678901234567890123456789012',
      to: '0x2109876543210987654321098765432109876543',
      value: 3.75,
      gasUsed: 42000,
      timestamp: new Date('2025-04-13T12:40:05'),
      status: 'confirmed'
    },
    { 
      hash: '0xa9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8',
      from: '0x4567890123456789012345678901234567890123',
      to: '0x3210987654321098765432109876543210987654',
      value: 0.125,
      gasUsed: 28000,
      timestamp: new Date('2025-04-13T12:38:47'),
      status: 'confirmed'
    },
    { 
      hash: '0xb0a9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9',
      from: '0x5678901234567890123456789012345678901234',
      to: '0x4321098765432109876543210987654321098765',
      value: 2.0,
      gasUsed: 31000,
      timestamp: new Date('2025-04-13T12:35:22'),
      status: 'confirmed'
    },
  ];

  // Mock data for smart contracts
  const smartContracts = [
    {
      address: '0x7890123456789012345678901234567890123456',
      name: 'TokenizedAsset',
      type: 'ERC20',
      deployedAt: new Date('2025-03-15T10:25:12'),
      transactions: 1245,
      verified: true
    },
    {
      address: '0x8901234567890123456789012345678901234567',
      name: 'PortfolioManager',
      type: 'Custom',
      deployedAt: new Date('2025-03-15T10:28:45'),
      transactions: 876,
      verified: true
    },
    {
      address: '0x9012345678901234567890123456789012345678',
      name: 'TradingPlatform',
      type: 'Custom',
      deployedAt: new Date('2025-03-15T10:32:18'),
      transactions: 532,
      verified: true
    },
    {
      address: '0x0123456789012345678901234567890123456789',
      name: 'DeFiIntegration',
      type: 'Custom',
      deployedAt: new Date('2025-03-15T10:35:56'),
      transactions: 324,
      verified: true
    },
    {
      address: '0x1234567890123456789012345678901234567890',
      name: 'TestToken',
      type: 'ERC20',
      deployedAt: new Date('2025-03-15T10:22:33'),
      transactions: 1876,
      verified: true
    },
  ];

  // Mock data for user assets
  const userAssets = [
    {
      token: 'QNT',
      name: 'QuantumNest Test Token',
      balance: 1000,
      value: 5000,
      contractAddress: '0x1234567890123456789012345678901234567890'
    },
    {
      token: 'AAPL',
      name: 'Tokenized Apple Inc.',
      balance: 10,
      value: 1805,
      contractAddress: '0x2345678901234567890123456789012345678901'
    },
    {
      token: 'MSFT',
      name: 'Tokenized Microsoft Corporation',
      balance: 5,
      value: 2051.25,
      contractAddress: '0x3456789012345678901234567890123456789012'
    },
    {
      token: 'BTC',
      name: 'Wrapped Bitcoin',
      balance: 0.25,
      value: 16250,
      contractAddress: '0x4567890123456789012345678901234567890123'
    },
    {
      token: 'ETH',
      name: 'Wrapped Ethereum',
      balance: 1.5,
      value: 4800,
      contractAddress: '0x5678901234567890123456789012345678901234'
    },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would search the blockchain for the query
    console.log('Searching for:', searchQuery);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Blockchain Explorer</h1>
        
        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex w-full">
            <input
              type="text"
              placeholder="Search by address, transaction hash, or block number"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-grow px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-l-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:text-white"
            />
            <Button type="submit" className="rounded-l-none">Search</Button>
          </form>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 mb-8">
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'overview'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'transactions'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('transactions')}
          >
            Transactions
          </button>
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'contracts'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('contracts')}
          >
            Smart Contracts
          </button>
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'assets'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('assets')}
          >
            My Assets
          </button>
        </div>
        
        {activeTab === 'overview' && (
          <>
            {/* Blockchain Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {blockchainStats.map((stat, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardContent className="p-6">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.title}</h3>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            {/* Recent Transactions */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Transaction Hash</TableHead>
                      <TableHead>From</TableHead>
                      <TableHead>To</TableHead>
                      <TableHead>Value (ETH)</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recentTransactions.map((tx, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{shortenAddress(tx.hash, 8)}</TableCell>
                        <TableCell>{shortenAddress(tx.from)}</TableCell>
                        <TableCell>{shortenAddress(tx.to)}</TableCell>
                        <TableCell>{tx.value}</TableCell>
                        <TableCell>{formatDateWithTime(tx.timestamp)}</TableCell>
                        <TableCell>
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            {tx.status}
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <div className="mt-4 text-center">
                  <Button variant="outline">View All Transactions</Button>
                </div>
              </CardContent>
            </Card>
            
            {/* Network Information */}
            <Card>
              <CardHeader>
                <CardTitle>Network Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Chain Details</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Network Name:</span>
                        <span className="font-medium text-gray-900 dark:text-white">Ethereum Mainnet</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Chain ID:</span>
                        <span className="font-medium text-gray-900 dark:text-white">1</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Currency:</span>
                        <span className="font-medium text-gray-900 dark:text-white">ETH</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Block Time:</span>
                        <span className="font-medium text-gray-900 dark:text-white">~12 seconds</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Consensus:</span>
                        <span className="font-medium text-gray-900 dark:text-white">Proof of Stake</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Current Status</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Gas Price (Standard):</span>
                        <span className="font-medium text-gray-900 dark:text-white">25 Gwei</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Gas Price (Fast):</span>
                        <span className="font-medium text-gray-900 dark:text-white">32 Gwei</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Active Validators:</span>
                        <span className="font-medium text-gray-900 dark:text-white">784,532</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Network Utilization:</span>
                        <span className="font-medium text-gray-900 dark:text-white">68%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">ETH Staked:</span>
                        <span className="font-medium text-gray-900 dark:text-white">25.4M ETH</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
        
        {activeTab === 'transactions' && (
          <Card>
            <CardHeader>
              <CardTitle>Transaction History</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction Hash</TableHead>
                    <TableHead>From</TableHead>
                    <TableHead>To</TableHead>
                    <TableHead>Value (ETH)</TableHead>
                    <TableHead>Gas Used</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentTransactions.map((tx, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{shortenAddress(tx.hash, 8)}</TableCell>
                      <TableCell>{shortenAddress(tx.from)}</TableCell>
                      <TableCell>{shortenAddress(tx.to)}</TableCell>
                      <TableCell>{tx.value}</TableCell>
                      <TableCell>{tx.gasUsed}</TableCell>
                      <TableCell>{formatDateWithTime(tx.timestamp)}</TableCell>
                      <TableCell>
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          {tx.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-6 flex justify-between items-center">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Showing 1-5 of 1,245 transactions
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" disabled>Previous</Button>
                  <Button variant="outline" size="sm">Next</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
        {activeTab === 'contracts' && (
          <Card>
            <CardHeader>
              <CardTitle>Smart Contracts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Contract Address</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Deployed At</TableHead>
                    <TableHead>Transactions</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {smartContracts.map((contract, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{shortenAddress(contract.address)}</TableCell>
                      <TableCell>{contract.name}</TableCell>
                      <TableCell>{contract.type}</TableCell>
                      <TableCell>{formatDateWithTime(contract.deployedAt)}</TableCell>
                      <TableCell>{contract.transactions}</TableCell>
                      <TableCell>
                        {contract.verified ? (
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            Verified
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                            Unverified
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-6 flex justify-center">
                <Button variant="outline">View All Contracts</Button>
              </div>
            </CardContent>
          </Card>
        )}
        
        {activeTab === 'assets' && (
          <Card>
            <CardHeader>
              <CardTitle>My Blockchain Assets</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Token</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Balance</TableHead>
                    <TableHead>Value (USD)</TableHead>
                    <TableHead>Contract Address</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {userAssets.map((asset, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{asset.token}</TableCell>
                      <TableCell>{asset.name}</TableCell>
                      <TableCell>{asset.balance}</TableCell>
                      <TableCell>{formatCurrency(asset.value)}</TableCell>
                      <TableCell>{shortenAddress(asset.contractAddress)}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">Send</Button>
                          <Button size="sm">Trade</Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-6 flex justify-between items-center">
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  Total Value: {formatCurrency(29906.25)}
                </div>
                <Button>Add Token</Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
