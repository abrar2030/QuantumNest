import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Define Cell component if not available directly from recharts
const Cell = props => {
  return props.children;
};

export default function Portfolio({ darkMode, toggleDarkMode }) {
  // Mock data for portfolio performance
  const performanceData = [
    { month: 'Jan', value: 4000, benchmark: 3000 },
    { month: 'Feb', value: 3000, benchmark: 2800 },
    { month: 'Mar', value: 5000, benchmark: 4200 },
    { month: 'Apr', value: 2780, benchmark: 2500 },
    { month: 'May', value: 4890, benchmark: 4100 },
    { month: 'Jun', value: 3390, benchmark: 3200 },
    { month: 'Jul', value: 4490, benchmark: 3800 },
  ];

  // Mock data for asset allocation
  const allocationData = [
    { name: 'Stocks', value: 45 },
    { name: 'Bonds', value: 25 },
    { name: 'Crypto', value: 15 },
    { name: 'Cash', value: 10 },
    { name: 'Commodities', value: 5 },
  ];

  // Mock data for sector breakdown
  const sectorData = [
    { name: 'Technology', value: 35 },
    { name: 'Healthcare', value: 20 },
    { name: 'Finance', value: 15 },
    { name: 'Consumer', value: 12 },
    { name: 'Energy', value: 10 },
    { name: 'Other', value: 8 },
  ];

  // Mock data for risk metrics
  const riskData = [
    { name: 'Volatility', value: 12.5 },
    { name: 'Sharpe Ratio', value: 1.8 },
    { name: 'Beta', value: 0.85 },
    { name: 'Alpha', value: 2.3 },
    { name: 'Max Drawdown', value: -15.2 },
  ];

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Portfolio Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Track your investment performance, asset allocation, and risk metrics in real-time.
          </p>
        </div>

        {/* Portfolio Summary Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 text-sm">Total Value</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">$1,245,678</p>
              <p className="text-green-500 text-sm">+5.4% <span className="text-gray-500 dark:text-gray-400">today</span></p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 text-sm">Monthly Return</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">+8.2%</p>
              <p className="text-green-500 text-sm">+2.1% <span className="text-gray-500 dark:text-gray-400">vs benchmark</span></p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 text-sm">YTD Return</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">+22.5%</p>
              <p className="text-green-500 text-sm">+5.3% <span className="text-gray-500 dark:text-gray-400">vs benchmark</span></p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 text-sm">Risk Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">72/100</p>
              <p className="text-blue-500 text-sm">Moderate-High <span className="text-gray-500 dark:text-gray-400">risk</span></p>
            </div>
          </div>
        </div>

        {/* Performance Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Performance History</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={performanceData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" name="Portfolio" />
                <Area type="monotone" dataKey="benchmark" stroke="#82ca9d" fillOpacity={1} fill="url(#colorBenchmark)" name="Benchmark" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Asset Allocation and Sector Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Asset Allocation</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={allocationData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {allocationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}%`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Sector Breakdown</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={sectorData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" />
                  <CartesianGrid strokeDasharray="3 3" />
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Bar dataKey="value" fill="#8884d8">
                    {sectorData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Risk Metrics and Top Holdings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Risk Metrics</h2>
            <div className="space-y-4">
              {riskData.map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-300">{item.name}</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Top Holdings</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-300 mr-3">A</div>
                  <span className="text-gray-800 dark:text-white">Apple Inc.</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">$125,400</div>
                  <div className="text-green-500 text-sm">+1.2%</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center text-green-600 dark:text-green-300 mr-3">M</div>
                  <span className="text-gray-800 dark:text-white">Microsoft Corp.</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">$98,750</div>
                  <div className="text-green-500 text-sm">+0.8%</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center text-yellow-600 dark:text-yellow-300 mr-3">T</div>
                  <span className="text-gray-800 dark:text-white">Tesla Inc.</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">$87,320</div>
                  <div className="text-red-500 text-sm">-2.1%</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center text-purple-600 dark:text-purple-300 mr-3">A</div>
                  <span className="text-gray-800 dark:text-white">Amazon.com Inc.</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">$76,540</div>
                  <div className="text-green-500 text-sm">+1.5%</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center text-red-600 dark:text-red-300 mr-3">G</div>
                  <span className="text-gray-800 dark:text-white">Google (Alphabet)</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">$65,890</div>
                  <div className="text-green-500 text-sm">+0.6%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">AI-Powered Recommendations</h2>
          <div className="space-y-4">
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-800 rounded-full p-2 mr-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-1">Portfolio Rebalancing</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-2">Our AI suggests rebalancing your portfolio to reduce technology exposure by 5% and increase healthcare allocation by 3%.</p>
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">View Details</button>
                </div>
              </div>
            </div>
            <div className="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0 bg-green-100 dark:bg-green-800 rounded-full p-2 mr-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600 dark:text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-1">Investment Opportunity</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-2">Based on your risk profile, we've identified 3 potential investments that align with your goals and may increase returns.</p>
                  <button className="text-green-600 dark:text-green-400 font-medium hover:underline">View Opportunities</button>
                </div>
              </div>
            </div>
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0 bg-yellow-100 dark:bg-yellow-800 rounded-full p-2 mr-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-600 dark:text-yellow-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-1">Risk Alert</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-2">Our volatility models indicate increased market turbulence ahead. Consider hedging strategies to protect your portfolio.</p>
                  <button className="text-yellow-600 dark:text-yellow-400 font-medium hover:underline">View Risk Analysis</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
