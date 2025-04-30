import Layout from '../components/Layout';
import { useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AdminPanel({ darkMode, toggleDarkMode }) {
  // Mock data for user growth
  const userGrowthData = [
    { month: 'Jan', users: 120 },
    { month: 'Feb', users: 150 },
    { month: 'Mar', users: 200 },
    { month: 'Apr', users: 250 },
    { month: 'May', users: 300 },
    { month: 'Jun', users: 380 },
    { month: 'Jul', users: 450 },
  ];

  // Mock data for transaction volume
  const transactionVolumeData = [
    { month: 'Jan', volume: 1200000 },
    { month: 'Feb', volume: 1500000 },
    { month: 'Mar', volume: 1800000 },
    { month: 'Apr', volume: 1600000 },
    { month: 'May', volume: 2100000 },
    { month: 'Jun', volume: 2400000 },
    { month: 'Jul', volume: 2800000 },
  ];

  // Mock data for user tiers
  const userTiersData = [
    { name: 'Basic', value: 250 },
    { name: 'Premium', value: 150 },
    { name: 'Enterprise', value: 50 },
  ];

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  // Mock data for recent users
  const recentUsers = [
    {
      id: "USR001",
      name: "John Smith",
      email: "john.smith@example.com",
      joined: "Apr 9, 2025",
      tier: "Premium",
      status: "Active"
    },
    {
      id: "USR002",
      name: "Emily Johnson",
      email: "emily.johnson@example.com",
      joined: "Apr 8, 2025",
      tier: "Basic",
      status: "Active"
    },
    {
      id: "USR003",
      name: "Michael Brown",
      email: "michael.brown@example.com",
      joined: "Apr 7, 2025",
      tier: "Enterprise",
      status: "Active"
    },
    {
      id: "USR004",
      name: "Sarah Davis",
      email: "sarah.davis@example.com",
      joined: "Apr 5, 2025",
      tier: "Premium",
      status: "Inactive"
    },
    {
      id: "USR005",
      name: "Robert Wilson",
      email: "robert.wilson@example.com",
      joined: "Apr 3, 2025",
      tier: "Basic",
      status: "Active"
    }
  ];

  // Mock data for system alerts
  const systemAlerts = [
    {
      title: "High API Usage",
      description: "API usage has exceeded 85% of the allocated quota.",
      time: "2 hours ago",
      severity: "warning"
    },
    {
      title: "Database Backup Completed",
      description: "Scheduled database backup completed successfully.",
      time: "5 hours ago",
      severity: "info"
    },
    {
      title: "Failed Login Attempts",
      description: "Multiple failed login attempts detected from IP 192.168.1.105.",
      time: "1 day ago",
      severity: "critical"
    },
    {
      title: "System Update Available",
      description: "New system update v2.3.5 is available for installation.",
      time: "2 days ago",
      severity: "info"
    }
  ];

  // Mock data for recent transactions
  const recentTransactions = [
    {
      id: "TRX001",
      user: "John Smith",
      type: "Deposit",
      amount: "$25,000",
      date: "Apr 9, 2025",
      status: "Completed"
    },
    {
      id: "TRX002",
      user: "Emily Johnson",
      type: "Withdrawal",
      amount: "$10,000",
      date: "Apr 8, 2025",
      status: "Pending"
    },
    {
      id: "TRX003",
      user: "Michael Brown",
      type: "Trade",
      amount: "$50,000",
      date: "Apr 7, 2025",
      status: "Completed"
    },
    {
      id: "TRX004",
      user: "Sarah Davis",
      type: "Deposit",
      amount: "$15,000",
      date: "Apr 6, 2025",
      status: "Completed"
    },
    {
      id: "TRX005",
      user: "Robert Wilson",
      type: "Trade",
      amount: "$8,500",
      date: "Apr 5, 2025",
      status: "Failed"
    }
  ];

  // Tabs for admin panel sections
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Admin Panel</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage users, monitor system performance, and oversee platform operations.
          </p>
        </div>

        {/* Admin Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8 overflow-x-auto">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`${
                  activeTab === 'dashboard'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('users')}
                className={`${
                  activeTab === 'users'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                User Management
              </button>
              <button
                onClick={() => setActiveTab('transactions')}
                className={`${
                  activeTab === 'transactions'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Transactions
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`${
                  activeTab === 'analytics'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Analytics
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`${
                  activeTab === 'settings'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                System Settings
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`${
                  activeTab === 'logs'
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                System Logs
              </button>
            </nav>
          </div>
        </div>

        {/* Dashboard Tab Content */}
        {activeTab === 'dashboard' && (
          <div>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">450</p>
                <p className="text-green-500 text-sm">+18.4% <span className="text-gray-500 dark:text-gray-400">this month</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Transaction Volume</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">$2.8M</p>
                <p className="text-green-500 text-sm">+16.7% <span className="text-gray-500 dark:text-gray-400">this month</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">Active Smart Contracts</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">32</p>
                <p className="text-green-500 text-sm">+3 <span className="text-gray-500 dark:text-gray-400">this month</span></p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">System Health</p>
                <p className="text-2xl font-bold text-green-500">98.5%</p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Uptime last 30 days</p>
              </div>
            </div>

            {/* User Growth Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">User Growth</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={userGrowthData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" />
                    <YAxis />
                    <CartesianGrid strokeDasharray="3 3" />
                    <Tooltip />
                    <Area type="monotone" dataKey="users" stroke="#8884d8" fillOpacity={1} fill="url(#colorUsers)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Transaction Volume and User Tiers */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Transaction Volume</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={transactionVolumeData}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                      <Bar dataKey="volume" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">User Tiers</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={userTiersData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {userTiersData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value} users`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Recent Users and System Alerts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Recent Users</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Joined</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Tier</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {recentUsers.map((user, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{user.id}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{user.name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{user.joined}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{user.tier}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              user.status === 'Active' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}>
                              {user.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4 text-center">
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                    View All Users
                  </button>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">System Alerts</h2>
                <div className="space-y-4">
                  {systemAlerts.map((alert, index) => (
                    <div key={index} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
                      <div className="flex items-start">
                        <div className={`flex-shrink-0 rounded-full w-2 h-2 mt-2 mr-3 ${
                          alert.severity === 'critical' 
                            ? 'bg-red-500' 
                            : alert.severity === 'warning'
                              ? 'bg-yellow-500'
                              : 'bg-blue-500'
                        }`}></div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{alert.title}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{alert.description}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{alert.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-center">
                  <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                    View All Alerts
                  </button>
                </div>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Recent Transactions</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">User</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Amount</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {recentTransactions.map((transaction, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{transaction.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{transaction.user}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{transaction.type}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{transaction.amount}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{transaction.date}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            transaction.status === 'Completed' 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                              : transaction.status === 'Pending'
                                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {transaction.status}
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

            {/* Admin Actions */}
            <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Add User</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Generate Report</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">System Alerts</span>
                </button>
                <button className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">Settings</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* User Management Tab Content */}
        {activeTab === 'users' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">User Management</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Detailed user management interface will be displayed here.
            </p>
          </div>
        )}

        {/* Transactions Tab Content */}
        {activeTab === 'transactions' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Transaction Management</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Detailed transaction management interface will be displayed here.
            </p>
          </div>
        )}

        {/* Analytics Tab Content */}
        {activeTab === 'analytics' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Analytics Dashboard</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Detailed analytics dashboard will be displayed here.
            </p>
          </div>
        )}

        {/* Settings Tab Content */}
        {activeTab === 'settings' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">System Settings</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              System settings interface will be displayed here.
            </p>
          </div>
        )}

        {/* Logs Tab Content */}
        {activeTab === 'logs' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">System Logs</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              System logs will be displayed here.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
