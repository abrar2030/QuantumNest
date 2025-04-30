
'use client';

import React from 'react';
// Removed Navbar import as it's handled in layout.tsx
import { StatCard } from '@/components/ui/Cards'; // Assuming Cards.tsx exports StatCard
import { LineChart, DoughnutChart } from '@/components/ui/Charts'; // Assuming Charts.tsx exports these
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { formatCurrency } from '@/lib/utils';

export default function Dashboard() {
  // Mock data for dashboard
  const portfolioValue = 1250000;
  const portfolioChange = 5.2;
  const totalAssets = 12;
  const totalTransactions = 48;

  // Mock data for portfolio allocation chart
  const allocationData = {
    labels: ['Stocks', 'Bonds', 'Crypto', 'Real Estate', 'Commodities'],
    datasets: [
      {
        data: [45, 20, 15, 12, 8],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(79, 70, 229, 0.8)',
          'rgba(67, 56, 202, 0.8)',
          'rgba(55, 48, 163, 0.8)',
          'rgba(49, 46, 129, 0.8)',
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(79, 70, 229, 1)',
          'rgba(67, 56, 202, 1)',
          'rgba(55, 48, 163, 1)',
          'rgba(49, 46, 129, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Mock data for performance chart
  const performanceData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Portfolio Performance',
        data: [1000000, 1020000, 1050000, 1040000, 1080000, 1100000, 1150000, 1180000, 1200000, 1220000, 1240000, 1250000],
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
      },
      {
        label: 'Benchmark',
        data: [1000000, 1010000, 1030000, 1020000, 1050000, 1070000, 1100000, 1120000, 1140000, 1150000, 1160000, 1170000],
        borderColor: 'rgba(156, 163, 175, 1)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        fill: true,
      },
    ],
  };

  // Mock data for recent transactions
  const recentTransactions = [
    { id: 1, type: 'Buy', asset: 'AAPL', amount: 10, price: 180.25, total: 1802.50, date: '2025-04-10' },
    { id: 2, type: 'Sell', asset: 'TSLA', amount: 5, price: 210.75, total: 1053.75, date: '2025-04-08' },
    { id: 3, type: 'Buy', asset: 'ETH', amount: 2.5, price: 3200.00, total: 8000.00, date: '2025-04-05' },
    { id: 4, type: 'Buy', asset: 'MSFT', amount: 8, price: 410.50, total: 3284.00, date: '2025-04-02' },
    { id: 5, type: 'Sell', asset: 'BTC', amount: 0.5, price: 65000.00, total: 32500.00, date: '2025-03-28' },
  ];

  return (
    // Removed min-h-screen and background color as they are handled in layout
    <div className="space-y-8">
      {/* Removed Navbar rendering */}
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
        <StatCard 
          title="Portfolio Value" 
          value={formatCurrency(portfolioValue)} 
          change={portfolioChange} 
          description="vs. last month"
        />
        <StatCard 
          title="Total Assets" 
          value={totalAssets} 
        />
        <StatCard 
          title="Transactions" // Shortened title for mobile
          value={totalTransactions} 
        />
        <StatCard 
          title="Perf. (YTD)" // Shortened title for mobile
          value="+12.5%" 
          description="vs bench +8.3%" // Shortened description
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <LineChart 
            data={performanceData} 
            title="Portfolio Performance" 
            height={300} // Adjusted height slightly
          />
        </div>
        <div>
          <DoughnutChart 
            data={allocationData} 
            title="Asset Allocation" 
            height={300} // Adjusted height slightly
          />
        </div>
      </div>
      
      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent className="p-0 sm:p-6"> {/* Remove padding on smallest screens for table */} 
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Asset</TableHead>
                <TableHead className="hidden sm:table-cell">Amount</TableHead> {/* Hide on small screens */}
                <TableHead className="hidden md:table-cell">Price</TableHead> {/* Hide on small/medium screens */}
                <TableHead>Total</TableHead>
                <TableHead className="hidden lg:table-cell">Date</TableHead> {/* Hide on small/medium/large screens */}
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentTransactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell className={transaction.type === 'Buy' ? 'text-green-600' : 'text-red-600'}>
                    {transaction.type}
                  </TableCell>
                  <TableCell className="font-medium">{transaction.asset}</TableCell>
                  <TableCell className="hidden sm:table-cell">{transaction.amount}</TableCell>
                  <TableCell className="hidden md:table-cell">{formatCurrency(transaction.price)}</TableCell>
                  <TableCell>{formatCurrency(transaction.total)}</TableCell>
                  <TableCell className="hidden lg:table-cell">{transaction.date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* AI Insights */}
      <Card>
        <CardHeader>
          <CardTitle>AI Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg border border-indigo-100 dark:border-indigo-800">
              <h4 className="font-semibold text-indigo-900 dark:text-indigo-300 mb-2">Portfolio Optimization</h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Based on your risk profile and market conditions, our AI suggests increasing your allocation to technology stocks by 5% and reducing exposure to consumer discretionary by 3%.
              </p>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg border border-purple-100 dark:border-purple-800">
              <h4 className="font-semibold text-purple-900 dark:text-purple-300 mb-2">Market Sentiment</h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Current market sentiment analysis shows positive trends for renewable energy and AI sectors. Consider exploring opportunities in these areas for potential growth.
              </p>
            </div>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-100 dark:border-blue-800">
              <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Risk Assessment</h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Your portfolio's current volatility is 12% lower than the market average. The diversification strategy is effectively managing risk while maintaining competitive returns.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
