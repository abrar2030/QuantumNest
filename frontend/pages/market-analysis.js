import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function MarketAnalysis({ darkMode, toggleDarkMode }) {
  // Mock data for market indices
  const marketIndicesData = [
    { date: '2025-03-10', sp500: 5200, nasdaq: 17800, dowJones: 38500 },
    { date: '2025-03-11', sp500: 5220, nasdaq: 17850, dowJones: 38550 },
    { date: '2025-03-12', sp500: 5180, nasdaq: 17750, dowJones: 38450 },
    { date: '2025-03-13', sp500: 5210, nasdaq: 17900, dowJones: 38600 },
    { date: '2025-03-14', sp500: 5250, nasdaq: 18000, dowJones: 38700 },
    { date: '2025-03-17', sp500: 5240, nasdaq: 17950, dowJones: 38650 },
    { date: '2025-03-18', sp500: 5270, nasdaq: 18050, dowJones: 38750 },
    { date: '2025-03-19', sp500: 5300, nasdaq: 18100, dowJones: 38800 },
    { date: '2025-03-20', sp500: 5320, nasdaq: 18150, dowJones: 38850 },
    { date: '2025-03-21', sp500: 5350, nasdaq: 18200, dowJones: 38900 },
  ];

  // Mock data for sector performance
  const sectorPerformanceData = [
    { name: 'Technology', value: 8.5 },
    { name: 'Healthcare', value: 5.2 },
    { name: 'Finance', value: 3.7 },
    { name: 'Energy', value: -2.1 },
    { name: 'Consumer', value: 4.3 },
    { name: 'Utilities', value: 1.8 },
    { name: 'Materials', value: 2.9 },
    { name: 'Real Estate', value: -1.5 },
    { name: 'Industrials', value: 3.2 },
    { name: 'Telecom', value: 2.5 },
  ];

  // Mock data for economic indicators
  const economicIndicatorsData = [
    { name: 'GDP Growth', value: 3.2, prevValue: 2.8 },
    { name: 'Inflation Rate', value: 2.5, prevValue: 2.7 },
    { name: 'Unemployment', value: 3.8, prevValue: 4.0 },
    { name: 'Interest Rate', value: 2.0, prevValue: 1.75 },
    { name: 'Consumer Confidence', value: 110.5, prevValue: 108.2 },
  ];

  // Mock data for market sentiment
  const sentimentData = [
    { date: '2025-03-10', bullish: 55, neutral: 25, bearish: 20 },
    { date: '2025-03-11', bullish: 53, neutral: 27, bearish: 20 },
    { date: '2025-03-12', bullish: 51, neutral: 28, bearish: 21 },
    { date: '2025-03-13', bullish: 54, neutral: 26, bearish: 20 },
    { date: '2025-03-14', bullish: 57, neutral: 24, bearish: 19 },
    { date: '2025-03-17', bullish: 56, neutral: 25, bearish: 19 },
    { date: '2025-03-18', bullish: 58, neutral: 24, bearish: 18 },
    { date: '2025-03-19', bullish: 60, neutral: 23, bearish: 17 },
    { date: '2025-03-20', bullish: 59, neutral: 24, bearish: 17 },
    { date: '2025-03-21', bullish: 61, neutral: 23, bearish: 16 },
  ];

  // Market news
  const marketNews = [
    {
      title: "Fed Signals Potential Rate Cut in Q3",
      source: "Financial Times",
      time: "2 hours ago",
      summary: "Federal Reserve officials hinted at a possible interest rate cut in the third quarter as inflation pressures ease."
    },
    {
      title: "Tech Stocks Rally on AI Breakthrough",
      source: "Wall Street Journal",
      time: "4 hours ago",
      summary: "Major technology companies saw significant gains following announcements of new artificial intelligence capabilities."
    },
    {
      title: "Global Supply Chain Improvements Boost Manufacturing",
      source: "Bloomberg",
      time: "6 hours ago",
      summary: "Manufacturing indices show improvement as global supply chain disruptions continue to resolve."
    },
    {
      title: "Energy Sector Faces Pressure Amid Renewable Push",
      source: "Reuters",
      time: "8 hours ago",
      summary: "Traditional energy companies face challenges as governments worldwide accelerate renewable energy initiatives."
    },
    {
      title: "Consumer Spending Remains Strong Despite Inflation",
      source: "CNBC",
      time: "10 hours ago",
      summary: "Retail sales data indicates robust consumer spending despite ongoing inflation concerns."
    }
  ];

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Market Analysis</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Comprehensive analysis of market trends, economic indicators, and sentiment data.
          </p>
        </div>

        {/* Market Summary Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Market Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">S&P 500</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">5,350.24</p>
              <p className="text-green-500 text-sm">+30.12 (+0.57%)</p>
            </div>
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">NASDAQ</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">18,200.75</p>
              <p className="text-green-500 text-sm">+50.45 (+0.28%)</p>
            </div>
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">Dow Jones</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">38,900.18</p>
              <p className="text-green-500 text-sm">+45.32 (+0.12%)</p>
            </div>
          </div>
        </div>

        {/* Market Indices Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Market Indices (Last 10 Days)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={marketIndicesData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="sp500" stroke="#8884d8" name="S&P 500" activeDot={{ r: 8 }} />
                <Line yAxisId="left" type="monotone" dataKey="nasdaq" stroke="#82ca9d" name="NASDAQ" />
                <Line yAxisId="right" type="monotone" dataKey="dowJones" stroke="#ff7300" name="Dow Jones" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Sector Performance (YTD %)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={sectorPerformanceData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="value" fill={(data) => data.value >= 0 ? "#82ca9d" : "#ff7373"} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Economic Indicators and Market Sentiment */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Economic Indicators</h2>
            <div className="space-y-4">
              {economicIndicatorsData.map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-300">{item.name}</span>
                  <div className="text-right">
                    <span className="font-semibold text-gray-900 dark:text-white">{item.value}%</span>
                    {item.value > item.prevValue ? (
                      <span className="ml-2 text-green-500">↑</span>
                    ) : item.value < item.prevValue ? (
                      <span className="ml-2 text-red-500">↓</span>
                    ) : (
                      <span className="ml-2 text-gray-500">→</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Market Sentiment</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={sentimentData}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  stackOffset="expand"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis tickFormatter={(tick) => `${tick * 100}%`} />
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Legend />
                  <Area type="monotone" dataKey="bullish" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Bullish" />
                  <Area type="monotone" dataKey="neutral" stackId="1" stroke="#8884d8" fill="#8884d8" name="Neutral" />
                  <Area type="monotone" dataKey="bearish" stackId="1" stroke="#ff7373" fill="#ff7373" name="Bearish" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Market News */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Latest Market News</h2>
          <div className="space-y-4">
            {marketNews.map((news, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0 last:pb-0">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">{news.title}</h3>
                <div className="flex text-sm text-gray-500 dark:text-gray-400 mb-2">
                  <span>{news.source}</span>
                  <span className="mx-2">•</span>
                  <span>{news.time}</span>
                </div>
                <p className="text-gray-600 dark:text-gray-300">{news.summary}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
              View All Market News
            </button>
          </div>
        </div>

        {/* AI Market Insights */}
        <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-start mb-4">
            <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">AI-Generated Market Insights</h2>
              <p className="text-gray-600 dark:text-gray-300">Predictive analytics based on current market conditions</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Market Trend Analysis</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-2">
                Our AI models indicate a continued bullish trend in technology and healthcare sectors over the next 30 days, with a 78% confidence level. 
                Recent economic data supports this projection, particularly the strong consumer confidence numbers and easing inflation pressures.
              </p>
              <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">View Detailed Analysis</button>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Volatility Forecast</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-2">
                Market volatility is projected to decrease by 15% in the coming weeks based on our predictive models. 
                This suggests a stabilizing market environment, potentially favorable for long-term investment strategies.
              </p>
              <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">View Volatility Models</button>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Sector Rotation Prediction</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-2">
                Our AI predicts a potential sector rotation from technology to healthcare and consumer staples within the next 45-60 days. 
                This projection is based on historical patterns, current economic indicators, and sentiment analysis.
              </p>
              <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">View Sector Analysis</button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
