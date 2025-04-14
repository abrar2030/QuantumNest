'use client';

import React, { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { AssetCard, StatCard } from '@/components/ui/Cards';
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/lib/utils';

export default function Recommendations() {
  const [activeTab, setActiveTab] = useState('personalized');
  const [riskLevel, setRiskLevel] = useState('moderate');

  // Mock data for recommended assets
  const recommendedAssets = [
    { 
      symbol: 'NVDA', 
      name: 'NVIDIA Corporation', 
      price: 950.25, 
      change24h: 3.5, 
      marketCap: 2350000000000, 
      volume24h: 25600000000,
      recommendation: 'Strong Buy',
      aiConfidence: 92,
      reason: 'Leading position in AI hardware market with strong growth potential'
    },
    { 
      symbol: 'MSFT', 
      name: 'Microsoft Corporation', 
      price: 410.25, 
      change24h: 0.9, 
      marketCap: 3050000000000, 
      volume24h: 12800000000,
      recommendation: 'Buy',
      aiConfidence: 87,
      reason: 'Cloud business growth and AI integration across product lines'
    },
    { 
      symbol: 'ETH', 
      name: 'Ethereum', 
      price: 3240.50, 
      change24h: 0.65, 
      marketCap: 390000000000, 
      volume24h: 21300000000,
      recommendation: 'Buy',
      aiConfidence: 85,
      reason: 'Network upgrades and growing DeFi ecosystem'
    },
    { 
      symbol: 'AMZN', 
      name: 'Amazon.com Inc.', 
      price: 3550.25, 
      change24h: 1.15, 
      marketCap: 3650000000000, 
      volume24h: 14500000000,
      recommendation: 'Buy',
      aiConfidence: 83,
      reason: 'E-commerce dominance and AWS cloud growth'
    },
    { 
      symbol: 'TSLA', 
      name: 'Tesla, Inc.', 
      price: 210.75, 
      change24h: -1.8, 
      marketCap: 670000000000, 
      volume24h: 18900000000,
      recommendation: 'Hold',
      aiConfidence: 65,
      reason: 'EV market competition increasing but strong innovation pipeline'
    },
    { 
      symbol: 'GOOGL', 
      name: 'Alphabet Inc.', 
      price: 2450.75, 
      change24h: 0.45, 
      marketCap: 3150000000000, 
      volume24h: 11200000000,
      recommendation: 'Buy',
      aiConfidence: 80,
      reason: 'AI integration and search dominance with growing cloud business'
    },
  ];

  // Mock data for portfolio recommendations
  const portfolioRecommendations = [
    {
      id: 1,
      title: 'Increase Technology Exposure',
      description: 'Your portfolio is underweight in technology stocks compared to the optimal allocation for your risk profile. Consider increasing exposure to high-quality tech companies.',
      impact: 'Potential 2.5% increase in expected annual return',
      confidence: 88
    },
    {
      id: 2,
      title: 'Reduce Cash Position',
      description: 'Your current cash position of 15% is higher than optimal in the current market environment. Consider deploying capital to fixed income or equity positions.',
      impact: 'Potential 1.2% increase in expected annual return',
      confidence: 82
    },
    {
      id: 3,
      title: 'Add Cryptocurrency Allocation',
      description: 'A small allocation to top cryptocurrencies could improve portfolio diversification and potential returns. Consider a 3-5% allocation to Bitcoin and Ethereum.',
      impact: 'Improved diversification with potential upside',
      confidence: 75
    },
    {
      id: 4,
      title: 'Rebalance Sector Weights',
      description: 'Your portfolio is overweight in consumer discretionary and underweight in healthcare. Rebalancing these sectors could improve risk-adjusted returns.',
      impact: 'Reduced sector-specific risk',
      confidence: 85
    }
  ];

  // Mock data for market insights
  const marketInsights = [
    {
      id: 1,
      title: 'AI Sector Growth Acceleration',
      description: 'Companies focused on artificial intelligence infrastructure and applications are showing accelerated growth patterns. Consider increasing exposure to this sector.',
      sentiment: 'Bullish',
      timeframe: 'Long-term'
    },
    {
      id: 2,
      title: 'Renewable Energy Momentum',
      description: 'Renewable energy companies are gaining momentum due to policy support and technological advancements. This sector presents attractive long-term investment opportunities.',
      sentiment: 'Bullish',
      timeframe: 'Long-term'
    },
    {
      id: 3,
      title: 'Potential Interest Rate Cuts',
      description: 'Economic indicators suggest potential interest rate cuts in the next 6 months, which could benefit growth stocks and real estate investments.',
      sentiment: 'Neutral',
      timeframe: 'Medium-term'
    },
    {
      id: 4,
      title: 'Consumer Spending Resilience',
      description: 'Consumer spending remains resilient despite inflation concerns, supporting retail and consumer services sectors.',
      sentiment: 'Neutral',
      timeframe: 'Short-term'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Recommendations</h1>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Risk Level:</span>
            <select
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
              className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md text-sm p-2"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 mb-8">
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'personalized'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('personalized')}
          >
            Personalized Recommendations
          </button>
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'assets'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('assets')}
          >
            Recommended Assets
          </button>
          <button
            className={`py-4 px-6 text-sm font-medium ${
              activeTab === 'insights'
                ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('insights')}
          >
            Market Insights
          </button>
        </div>
        
        {activeTab === 'personalized' && (
          <>
            {/* AI Summary */}
            <Card className="mb-8">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mr-4">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">AI Portfolio Analysis</h3>
                    <p className="text-gray-600 dark:text-gray-400">Last updated: April 13, 2025</p>
                  </div>
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  Based on your {riskLevel} risk profile and current market conditions, our AI has analyzed your portfolio and identified several optimization opportunities. Your current portfolio has a projected annual return of 8.2% with a risk score of 65/100.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <StatCard title="Current Return" value="8.2%" />
                  <StatCard title="Optimized Return" value="10.5%" change={2.3} />
                  <StatCard title="Risk Score" value="65/100" />
                </div>
                <Button>View Detailed Analysis</Button>
              </CardContent>
            </Card>
            
            {/* Portfolio Recommendations */}
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Portfolio Recommendations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {portfolioRecommendations.map((recommendation) => (
                <Card key={recommendation.id}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{recommendation.title}</h3>
                      <div className="bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        {recommendation.confidence}% confidence
                      </div>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 mb-4">{recommendation.description}</p>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      <strong>Potential Impact:</strong> {recommendation.impact}
                    </div>
                    <div className="flex justify-between">
                      <Button variant="outline" size="sm">Details</Button>
                      <Button size="sm">Apply</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
        
        {activeTab === 'assets' && (
          <>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Top Recommended Assets</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Based on your {riskLevel} risk profile, market conditions, and AI analysis, these assets are recommended for your consideration.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendedAssets.map((asset, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardContent className="p-0">
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{asset.symbol}</h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{asset.name}</p>
                        </div>
                        <div className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          asset.recommendation === 'Strong Buy' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                            : asset.recommendation === 'Buy'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                          {asset.recommendation}
                        </div>
                      </div>
                      <div className="flex justify-between mb-4">
                        <div>
                          <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(asset.price)}</p>
                          <p className={`text-sm ${
                            asset.change24h >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                          }`}>
                            {asset.change24h >= 0 ? '+' : ''}{asset.change24h}%
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="inline-flex items-center">
                            <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">AI Confidence:</span>
                            <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                              <div 
                                className="bg-indigo-600 dark:bg-indigo-500 h-2.5 rounded-full" 
                                style={{ width: `${asset.aiConfidence}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">{asset.reason}</p>
                      <div className="flex justify-between">
                        <Button variant="outline" size="sm">Details</Button>
                        <Button size="sm">Add to Portfolio</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
        
        {activeTab === 'insights' && (
          <>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">AI Market Insights</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Our AI analyzes market trends, news, and sentiment to provide actionable insights for your investment strategy.
            </p>
            <div className="space-y-6">
              {marketInsights.map((insight) => (
                <Card key={insight.id}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{insight.title}</h3>
                      <div className="flex space-x-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          insight.sentiment === 'Bullish' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                            : insight.sentiment === 'Bearish'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                        }`}>
                          {insight.sentiment}
                        </span>
                        <span className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {insight.timeframe}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 mb-4">{insight.description}</p>
                    <Button variant="link" className="p-0">Read full analysis</Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
