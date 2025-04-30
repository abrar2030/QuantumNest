'use client';

import React, { useState } from 'react';
// Removed Navbar import as it's handled in layout.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { AssetCard, StatCard } from '@/components/ui/Cards';
import { LineChart, BarChart } from '@/components/ui/Charts';
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/lib/utils';

export default function MarketAnalysis() {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('1m');

  // Mock data for market overview
  const marketStats = [
    { title: 'S&P 500', value: '5,320.45', change: 0.85 },
    { title: 'NASDAQ', value: '16,780.32', change: 1.25 },
    { title: 'Bitcoin', value: '$65,420.75', change: -2.15 },
    { title: 'Ethereum', value: '$3,240.50', change: 0.65 },
  ];

  // Mock data for trending assets
  const trendingAssets = [
    { symbol: 'AAPL', name: 'Apple Inc.', price: 180.50, change24h: 1.2, marketCap: 2850000000000, volume24h: 15200000000 },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 950.25, change24h: 3.5, marketCap: 2350000000000, volume24h: 25600000000 },
    { symbol: 'TSLA', name: 'Tesla, Inc.', price: 210.75, change24h: -1.8, marketCap: 670000000000, volume24h: 18900000000 },
    { symbol: 'BTC', name: 'Bitcoin', price: 65420.75, change24h: -2.15, marketCap: 1280000000000, volume24h: 42500000000 },
    { symbol: 'ETH', name: 'Ethereum', price: 3240.50, change24h: 0.65, marketCap: 390000000000, volume24h: 21300000000 },
    { symbol: 'MSFT', name: 'Microsoft Corporation', price: 410.25, change24h: 0.9, marketCap: 3050000000000, volume24h: 12800000000 },
  ];

  // Mock data for market performance chart
  const marketPerformanceData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'S&P 500',
        data: [4800, 4750, 4900, 5000, 5100, 5050, 5150, 5200, 5250, 5300, 5350, 5320],
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: false,
      },
      {
        label: 'NASDAQ',
        data: [15000, 14800, 15200, 15500, 15800, 15600, 16000, 16200, 16400, 16600, 16700, 16780],
        borderColor: 'rgba(79, 70, 229, 1)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        fill: false,
      },
    ],
  };

  // Mock data for sector performance
  const sectorPerformanceData = {
    labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Utilities', 'Real Estate'],
    datasets: [
      {
        label: 'Sector Performance (%)',
        data: [12.5, 8.2, 5.4, -2.1, 3.8, 1.5, -0.8],
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

  // Mock data for market news
  const marketNews = [
    {
      id: 1,
      title: 'Federal Reserve Maintains Interest Rates, Signals Potential Cut Later This Year',
      source: 'Financial Times',
      date: '2025-04-12',
      snippet: 'The Federal Reserve kept its benchmark interest rate unchanged but indicated it could cut rates later this year if inflation continues to cool.',
    },
    {
      id: 2,
      title: 'Tech Giants Report Strong Quarterly Earnings, Exceeding Analyst Expectations',
      source: 'Wall Street Journal',
      date: '2025-04-10',
      snippet: 'Major technology companies reported better-than-expected earnings for Q1 2025, driven by AI and cloud computing growth.',
    },
    {
      id: 3,
      title: 'Cryptocurrency Market Faces Volatility as Regulatory Concerns Resurface',
      source: 'Bloomberg',
      date: '2025-04-08',
      snippet: 'Bitcoin and other cryptocurrencies experienced increased volatility following new regulatory proposals from several major economies.',
    },
    {
      id: 4,
      title: 'Global Supply Chain Improvements Lead to Reduced Inflation Pressures',
      source: 'Reuters',
      date: '2025-04-05',
      snippet: 'Recent improvements in global supply chains have helped ease inflation pressures, according to a new economic report.',
    },
    {
      id: 5,
      title: 'Renewable Energy Sector Sees Surge in Investment Following New Climate Policies',
      source: 'CNBC',
      date: '2025-04-03',
      snippet: 'Investments in renewable energy companies have increased significantly following the announcement of new climate policies by major economies.',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Market Analysis</h1>
        <div className="flex flex-wrap gap-2">
          <Button 
            variant={timeRange === '1w' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTimeRange('1w')}
          >
            1W
          </Button>
          <Button 
            variant={timeRange === '1m' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTimeRange('1m')}
          >
            1M
          </Button>
          <Button 
            variant={timeRange === '3m' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTimeRange('3m')}
          >
            3M
          </Button>
          <Button 
            variant={timeRange === '1y' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTimeRange('1y')}
          >
            1Y
          </Button>
          <Button 
            variant={timeRange === 'all' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTimeRange('all')}
          >
            All
          </Button>
        </div>
      </div>
      
      {/* Tabs - Scrollable on mobile */}
      <div className="overflow-x-auto pb-2">
        <div className="flex border-b border-gray-200 dark:border-gray-700 min-w-max">
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'overview'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'stocks'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('stocks')}
          >
            Stocks
          </button>
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'crypto'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('crypto')}
          >
            Crypto
          </button>
          <button
            className={`py-3 px-4 sm:py-4 sm:px-6 text-sm font-medium ${
              activeTab === 'news'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('news')}
          >
            News
          </button>
        </div>
      </div>
      
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Market Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {marketStats.map((stat, index) => (
              <StatCard 
                key={index}
                title={stat.title} 
                value={stat.value} 
                change={stat.change} 
              />
            ))}
          </div>
          
          {/* Market Performance Chart */}
          <div>
            <LineChart 
              data={marketPerformanceData} 
              title="Market Performance" 
              height={300}
            />
          </div>
          
          {/* Sector Performance */}
          <div>
            <BarChart 
              data={sectorPerformanceData} 
              title="Sector Performance" 
              height={300}
            />
          </div>
          
          {/* Trending Assets */}
          <Card>
            <CardHeader>
              <CardTitle>Trending Assets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {trendingAssets.map((asset, index) => (
                  <AssetCard
                    key={index}
                    symbol={asset.symbol}
                    name={asset.name}
                    price={asset.price}
                    change24h={asset.change24h}
                    marketCap={asset.marketCap}
                    volume24h={asset.volume24h}
                    onClick={() => {}}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {activeTab === 'stocks' && (
        <div className="text-center py-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Stock Market Analysis</h3>
          <p className="text-gray-600 dark:text-gray-400">
            This tab would contain detailed stock market data, sector analysis, and individual stock information.
          </p>
        </div>
      )}
      
      {activeTab === 'crypto' && (
        <div className="text-center py-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Cryptocurrency Market</h3>
          <p className="text-gray-600 dark:text-gray-400">
            This tab would display cryptocurrency market data, token information, and blockchain analytics.
          </p>
        </div>
      )}
      
      {activeTab === 'news' && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Market News</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {marketNews.map((news) => (
                <div key={news.id} className="border-b border-gray-200 dark:border-gray-700 pb-6 last:border-0 last:pb-0">
                  <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2">{news.title}</h3>
                  <div className="flex items-center text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-3">
                    <span>{news.source}</span>
                    <span className="mx-2">•</span>
                    <span>{news.date}</span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{news.snippet}</p>
                  <Button variant="link" className="mt-2 p-0 text-sm">Read more</Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
