
'use client';

import React, { useState } from 'react';
// Removed Navbar import as it's handled in layout.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { PortfolioCard } from '@/components/ui/Cards'; // Assuming Cards.tsx exports PortfolioCard
import { DoughnutChart } from '@/components/ui/Charts'; // Assuming Charts.tsx exports DoughnutChart
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/lib/utils';

export default function Portfolio() {
  const [activeTab, setActiveTab] = useState('portfolios');

  // Mock data for portfolios
  const portfolios = [
    { id: 1, name: 'Growth Portfolio', value: 750000, change: 8.5, assetCount: 8, lastUpdated: '2025-04-12' },
    { id: 2, name: 'Income Portfolio', value: 350000, change: 3.2, assetCount: 5, lastUpdated: '2025-04-12' },
    { id: 3, name: 'Crypto Portfolio', value: 150000, change: -2.8, assetCount: 6, lastUpdated: '2025-04-12' },
  ];

  // Mock data for assets in selected portfolio (assuming Growth Portfolio)
  const portfolioAssets = [
    { id: 1, symbol: 'AAPL', name: 'Apple Inc.', quantity: 100, purchasePrice: 150.25, currentPrice: 180.50, value: 18050, change: 20.13 },
    { id: 2, symbol: 'MSFT', name: 'Microsoft Corporation', quantity: 75, purchasePrice: 280.75, currentPrice: 410.25, value: 30768.75, change: 46.13 },
    { id: 3, symbol: 'GOOGL', name: 'Alphabet Inc.', quantity: 25, purchasePrice: 2100.50, currentPrice: 2450.75, value: 61268.75, change: 16.67 },
    { id: 4, symbol: 'AMZN', name: 'Amazon.com Inc.', quantity: 30, purchasePrice: 3200.00, currentPrice: 3550.25, value: 106507.50, change: 10.95 },
    { id: 5, symbol: 'TSLA', name: 'Tesla, Inc.', quantity: 50, purchasePrice: 220.50, currentPrice: 210.75, value: 10537.50, change: -4.42 },
    { id: 6, symbol: 'BTC', name: 'Bitcoin', quantity: 2.5, purchasePrice: 50000.00, currentPrice: 65000.00, value: 162500, change: 30.00 },
    { id: 7, symbol: 'ETH', name: 'Ethereum', quantity: 15, purchasePrice: 2800.00, currentPrice: 3200.00, value: 48000, change: 14.29 },
    { id: 8, symbol: 'VTI', name: 'Vanguard Total Stock Market ETF', quantity: 200, purchasePrice: 210.25, currentPrice: 230.50, value: 46100, change: 9.63 },
  ];

  // Mock data for allocation chart
  const allocationData = {
    labels: ['Technology', 'Finance', 'Healthcare', 'Consumer', 'Energy', 'Crypto', 'ETFs'],
    datasets: [
      {
        data: [35, 15, 10, 12, 8, 15, 5],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(79, 70, 229, 0.8)',
          'rgba(67, 56, 202, 0.8)',
          'rgba(55, 48, 163, 0.8)',
          'rgba(49, 46, 129, 0.8)',
          'rgba(129, 140, 248, 0.8)',
          'rgba(165, 180, 252, 0.8)',
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(79, 70, 229, 1)',
          'rgba(67, 56, 202, 1)',
          'rgba(55, 48, 163, 1)',
          'rgba(49, 46, 129, 1)',
          'rgba(129, 140, 248, 1)',
          'rgba(165, 180, 252, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Portfolio Management</h1>
        <Button size="sm">Create New Portfolio</Button>
      </div>
      
      {/* Tabs - Scrollable on mobile */}
      <div className="overflow-x-auto pb-2">
        <div className="flex border-b border-gray-200 dark:border-gray-700 min-w-max">
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'portfolios'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('portfolios')}
          >
            My Portfolios
          </button>
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'performance'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('performance')}
          >
            Performance
          </button>
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'transactions'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('transactions')}
          >
            Transactions
          </button>
        </div>
      </div>
      
      {activeTab === 'portfolios' && (
        <div className="space-y-6">
          {/* Portfolios Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfolios.map((portfolio) => (
              <PortfolioCard
                key={portfolio.id}
                name={portfolio.name}
                value={portfolio.value}
                change={portfolio.change}
                assetCount={portfolio.assetCount}
                lastUpdated={portfolio.lastUpdated}
                onClick={() => { /* Add logic to select portfolio */ }}
              />
            ))}
          </div>
          
          {/* Selected Portfolio Details */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Growth Portfolio Assets</CardTitle>
                </CardHeader>
                <CardContent className="p-0 sm:p-6"> {/* Remove padding on smallest screens for table */}
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Asset</TableHead>
                        <TableHead className="hidden sm:table-cell">Qty</TableHead>
                        <TableHead className="hidden md:table-cell">Purchase</TableHead>
                        <TableHead className="hidden lg:table-cell">Current</TableHead>
                        <TableHead>Value</TableHead>
                        <TableHead>Change</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {portfolioAssets.map((asset) => (
                        <TableRow key={asset.id}>
                          <TableCell className="font-medium">
                            <div className="font-semibold">{asset.symbol}</div>
                            <div className="text-xs text-gray-500 hidden sm:block">{asset.name}</div>
                          </TableCell>
                          <TableCell className="hidden sm:table-cell">{asset.quantity}</TableCell>
                          <TableCell className="hidden md:table-cell">{formatCurrency(asset.purchasePrice)}</TableCell>
                          <TableCell className="hidden lg:table-cell">{formatCurrency(asset.currentPrice)}</TableCell>
                          <TableCell>{formatCurrency(asset.value)}</TableCell>
                          <TableCell className={asset.change >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {asset.change >= 0 ? '+' : ''}{asset.change.toFixed(2)}%
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
            <div>
              <DoughnutChart 
                data={allocationData} 
                title="Asset Allocation" 
                height={300} // Adjusted height
              />
            </div>
          </div>
          
          {/* Portfolio Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2">Add Assets</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Add new assets to your portfolio.
                </p>
                <Button variant="default" size="sm" className="w-full">Add Assets</Button>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2">Rebalance</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Optimize allocation based on AI.
                </p>
                <Button variant="outline" size="sm" className="w-full">Rebalance</Button>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2">Export Data</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Download portfolio data.
                </p>
                <Button variant="subtle" size="sm" className="w-full">Export</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
      
      {activeTab === 'performance' && (
        <div className="text-center py-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Performance Analysis</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Detailed performance metrics and charts will be displayed here.
          </p>
        </div>
      )}
      
      {activeTab === 'transactions' && (
        <div className="text-center py-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Transaction History</h3>
          <p className="text-gray-600 dark:text-gray-400">
            A complete history of all portfolio transactions will be displayed here.
          </p>
        </div>
      )}
    </div>
  );
}
