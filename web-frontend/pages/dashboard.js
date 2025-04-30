import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard({ darkMode, toggleDarkMode }) {
  // Mock data for portfolio value over time
  const portfolioValueData = [
    { month: 'Jan', value: 1000000 },
    { month: 'Feb', value: 1050000 },
    { month: 'Mar', value: 1120000 },
    { month: 'Apr', value: 1080000 },
    { month: 'May', value: 1150000 },
    { month: 'Jun', value: 1220000 },
    { month: 'Jul', value: 1245000 },
  ];

  // Mock data for asset allocation
  const assetAllocationData = [
    { name: 'Stocks', value: 45 },
    { name: 'Bonds', value: 25 },
    { name: 'Crypto', value: 15 },
    { name: 'Cash', value: 10 },
    { name: 'Commodities', value: 5 },
  ];

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  // Mock data for recent activities
  const recentActivities = [
    {
      type: "Purchase",
      asset: "AAPL",
      amount: "$25,000",
      date: "Today, 10:30 AM",
      status: "Completed"
    },
    {
      type: "Sale",
      asset: "TSLA",
      amount: "$18,500",
      date: "Yesterday, 3:45 PM",
      status: "Completed"
    },
    {
      type: "Deposit",
      asset: "USD",
      amount: "$50,000",
      date: "Apr 7, 2025",
      status: "Completed"
    },
    {
      type: "Rebalance",
      asset: "Portfolio",
      amount: "-",
      date: "Apr 5, 2025",
      status: "Completed"
    },
    {
      type: "Dividend",
      asset: "VTI",
      amount: "$1,250",
      date: "Apr 3, 2025",
      status: "Completed"
    }
  ];

  // Mock data for notifications
  const notifications = [
    {
      title: "Portfolio Rebalance Recommended",
      description: "Our AI suggests rebalancing your portfolio to reduce technology exposure by 5%.",
      time: "2 hours ago",
      priority: "high"
    },
    {
      title: "New AI Insight Available",
      description: "A new market analysis report is available for your review.",
      time: "5 hours ago",
      priority: "medium"
    },
    {
      title: "Dividend Payment Received",
      description: "You received a dividend payment of $1,250 from VTI.",
      time: "2 days ago",
      priority: "low"
    },
    {
      title: "Smart Contract Executed",
      description: "Your automated trading smart contract executed successfully.",
      time: "3 days ago",
      priority: "medium"
    }
  ];

  // Mock data for upcoming events
  const upcomingEvents = [
    {
      title: "Quarterly Portfolio Review",
      date: "Apr 15, 2025",
      time: "10:00 AM"
    },
    {
      title: "Earnings Report: AAPL",
      date: "Apr 18, 2025",
      time: "After Market Close"
    },
    {
      title: "Fed Interest Rate Decision",
      date: "Apr 22, 2025",
      time: "2:00 PM"
    }
  ];

  // Tabs for dashboard sections
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">User Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Welcome back! Here's an overview of your portfolio and recent activities.
          </p>
        </div>

        {/* Dashboard Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`${
                  activeTab === 'overview'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('portfolio')}
                className={`${
                  activeTab === 'portfolio'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Portfolio
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`${
                  activeTab === 'activity'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Activity
              </button>
              <button
                onClick={() => setActiveTab('notifications')}
                className={`${
                  activeTab === 'notifications'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Notifications
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`${
                  activeTab === 'settings'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Settings
              </button>
            </nav>
          </div>
        </div>

        {/* Overview Tab Content */}
        {activeTab === 'overview' && (
          <div>
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Portfolio Value</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">$1,245,000</p>
                <p className="text-green-500 text-sm">+2.1% <span className="text-gray-500 dark:text-gray-400">today</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Monthly Return</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">+5.8%</p>
                <p className="text-green-500 text-sm">+1.2% <span className="text-gray-500 dark:text-gray-400">vs benchmark</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">YTD Return</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">+18.3%</p>
                <p className="text-green-500 text-sm">+3.5% <span className="text-gray-500 dark:text-gray-400">vs benchmark</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Available Cash</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">$124,500</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">10% of portfolio</p>
              </div>
            </div>

            {/* Portfolio Value Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Portfolio Value</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={portfolioValueData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" />
                    <YAxis />
                    <CartesianGrid strokeDasharray="3 3" />
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Asset Allocation and Recent Activity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Asset Allocation</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={assetAllocationData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {assetAllocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value}%`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Recent Activity</h2>
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {recentActivities.map((activity, index) => (
                    <div key={index} className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-2 last:border-0">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{activity.type}: {activity.asset}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{activity.date}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900 dark:text-white">{activity.amount}</p>
                        <p className="text-sm text-green-500">{activity.status}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-center">
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                    View All Activity
                  </button>
                </div>
              </div>
            </div>

            {/* Notifications and Upcoming Events */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Notifications</h2>
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {notifications.map((notification, index) => (
                    <div key={index} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
                      <div className="flex items-start">
                        <div className={`flex-shrink-0 rounded-full w-2 h-2 mt-2 mr-3 ${
                          notification.priority === 'high' 
                            ? 'bg-red-500' 
                            : notification.priority === 'medium'
                              ? 'bg-yellow-500'
                              : 'bg-green-500'
                        }`}></div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{notification.title}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{notification.description}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{notification.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-center">
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                    View All Notifications
                  </button>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Upcoming Events</h2>
                <div className="space-y-4">
                  {upcomingEvents.map((event, index) => (
                    <div key={index} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
                      <p className="font-medium text-gray-900 dark:text-white">{event.title}</p>
                      <div className="flex text-sm text-gray-500 dark:text-gray-400 mt-1">
                        <p>{event.date}</p>
                        <span className="mx-2">•</span>
                        <p>{event.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-center">
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                    View Calendar
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Deposit Funds</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Transfer</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Trade</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Reports</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Tab Content */}
        {activeTab === 'portfolio' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Portfolio Details</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Detailed portfolio information will be displayed here.
            </p>
          </div>
        )}

        {/* Activity Tab Content */}
        {activeTab === 'activity' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Activity History</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Detailed activity history will be displayed here.
            </p>
          </div>
        )}

        {/* Notifications Tab Content */}
        {activeTab === 'notifications' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">All Notifications</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              All notifications will be displayed here.
            </p>
          </div>
        )}

        {/* Settings Tab Content */}
        {activeTab === 'settings' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Account Settings</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Account settings will be displayed here.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
