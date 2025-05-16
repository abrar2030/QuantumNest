'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table } from '@/components/ui/Table';

export default function Admin() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [systemStats, setSystemStats] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    activeUsers: 0,
    totalTransactions: 0,
    apiRequests: 0,
  });
  const [logs, setLogs] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userModalOpen, setUserModalOpen] = useState(false);
  const [userFormData, setUserFormData] = useState({
    id: '',
    username: '',
    email: '',
    role: 'user',
    status: 'active',
  });

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        
        // Fetch users
        const usersResponse = await fetch('/api/admin/users');
        if (!usersResponse.ok) throw new Error('Failed to fetch users');
        const usersData = await usersResponse.json();
        setUsers(usersData);
        
        // Fetch transactions
        const transactionsResponse = await fetch('/api/admin/transactions');
        if (!transactionsResponse.ok) throw new Error('Failed to fetch transactions');
        const transactionsData = await transactionsResponse.json();
        setTransactions(transactionsData);
        
        // Fetch system stats
        const statsResponse = await fetch('/api/admin/system-stats');
        if (!statsResponse.ok) throw new Error('Failed to fetch system stats');
        const statsData = await statsResponse.json();
        setSystemStats(statsData);
        
        // Fetch logs
        const logsResponse = await fetch('/api/admin/logs');
        if (!logsResponse.ok) throw new Error('Failed to fetch logs');
        const logsData = await logsResponse.json();
        setLogs(logsData);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching admin data:', error);
        setError('Failed to load admin data. Please try again later.');
        setLoading(false);
      }
    };

    fetchAdminData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchAdminData, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
  };

  const handleUserEdit = (user: any) => {
    setSelectedUser(user);
    setUserFormData({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      status: user.status,
    });
    setUserModalOpen(true);
  };

  const handleUserDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete user');
      
      // Update users list
      setUsers(users.filter((user: any) => user.id !== userId));
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user. Please try again.');
    }
  };

  const handleUserFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setUserFormData({
      ...userFormData,
      [name]: value,
    });
  };

  const handleUserFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const method = selectedUser ? 'PUT' : 'POST';
      const url = selectedUser 
        ? `/api/admin/users/${userFormData.id}` 
        : '/api/admin/users';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userFormData),
      });
      
      if (!response.ok) throw new Error(`Failed to ${selectedUser ? 'update' : 'create'} user`);
      
      const updatedUser = await response.json();
      
      // Update users list
      if (selectedUser) {
        setUsers(users.map((user: any) => 
          user.id === updatedUser.id ? updatedUser : user
        ));
      } else {
        setUsers([...users, updatedUser]);
      }
      
      // Close modal
      setUserModalOpen(false);
      setSelectedUser(null);
      setUserFormData({
        id: '',
        username: '',
        email: '',
        role: 'user',
        status: 'active',
      });
    } catch (error) {
      console.error('Error saving user:', error);
      setError(`Failed to ${selectedUser ? 'update' : 'create'} user. Please try again.`);
    }
  };

  const renderUsersTab = () => {
    return (
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">User Management</h2>
          <Button onClick={() => {
            setSelectedUser(null);
            setUserFormData({
              id: '',
              username: '',
              email: '',
              role: 'user',
              status: 'active',
            });
            setUserModalOpen(true);
          }}>
            Add New User
          </Button>
        </div>
        
        <Table
          headers={['Username', 'Email', 'Role', 'Status', 'Actions']}
          data={users.map((user: any) => [
            user.username,
            user.email,
            user.role,
            user.status,
            <div key={user.id} className="flex space-x-2">
              <button 
                className="text-blue-500 hover:text-blue-700"
                onClick={() => handleUserEdit(user)}
              >
                Edit
              </button>
              <button 
                className="text-red-500 hover:text-red-700"
                onClick={() => handleUserDelete(user.id)}
              >
                Delete
              </button>
            </div>
          ])}
        />
      </div>
    );
  };

  const renderTransactionsTab = () => {
    return (
      <div>
        <h2 className="text-xl font-semibold mb-4">Transaction History</h2>
        <Table
          headers={['ID', 'User', 'Type', 'Amount', 'Status', 'Date']}
          data={transactions.map((tx: any) => [
            tx.id,
            tx.username,
            tx.type,
            `$${tx.amount.toFixed(2)}`,
            tx.status,
            new Date(tx.timestamp).toLocaleString(),
          ])}
        />
      </div>
    );
  };

  const renderSystemTab = () => {
    return (
      <div>
        <h2 className="text-xl font-semibold mb-4">System Statistics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">CPU Usage</h3>
            <div className="text-3xl font-bold">{systemStats.cpuUsage}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${systemStats.cpuUsage}%` }}
              ></div>
            </div>
          </Card>
          
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">Memory Usage</h3>
            <div className="text-3xl font-bold">{systemStats.memoryUsage}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className="bg-green-600 h-2.5 rounded-full" 
                style={{ width: `${systemStats.memoryUsage}%` }}
              ></div>
            </div>
          </Card>
          
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">Disk Usage</h3>
            <div className="text-3xl font-bold">{systemStats.diskUsage}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className="bg-yellow-600 h-2.5 rounded-full" 
                style={{ width: `${systemStats.diskUsage}%` }}
              ></div>
            </div>
          </Card>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">Active Users</h3>
            <div className="text-3xl font-bold">{systemStats.activeUsers}</div>
          </Card>
          
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">Total Transactions</h3>
            <div className="text-3xl font-bold">{systemStats.totalTransactions}</div>
          </Card>
          
          <Card className="p-4">
            <h3 className="text-lg font-medium mb-2">API Requests (24h)</h3>
            <div className="text-3xl font-bold">{systemStats.apiRequests}</div>
          </Card>
        </div>
      </div>
    );
  };

  const renderLogsTab = () => {
    return (
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">System Logs</h2>
          <div className="flex space-x-2">
            <select className="border rounded p-1">
              <option value="all">All Levels</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
            <Button>Download Logs</Button>
          </div>
        </div>
        
        <div className="bg-gray-100 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
          {logs.map((log: any, index: number) => (
            <div 
              key={index} 
              className={`mb-1 ${
                log.level === 'error' ? 'text-red-600' : 
                log.level === 'warning' ? 'text-yellow-600' : 
                log.level === 'info' ? 'text-blue-600' : ''
              }`}
            >
              [{new Date(log.timestamp).toLocaleString()}] [{log.level.toUpperCase()}] {log.message}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'users':
        return renderUsersTab();
      case 'transactions':
        return renderTransactionsTab();
      case 'system':
        return renderSystemTab();
      case 'logs':
        return renderLogsTab();
      default:
        return renderUsersTab();
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
        <div className="flex justify-center items-center h-64">
          <p className="text-lg">Loading admin data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="flex border-b mb-6">
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'users' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleTabChange('users')}
        >
          Users
        </button>
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'transactions' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleTabChange('transactions')}
        >
          Transactions
        </button>
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'system' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleTabChange('system')}
        >
          System
        </button>
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'logs' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleTabChange('logs')}
        >
          Logs
        </button>
      </div>

      {renderContent()}

      {userModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">
              {selectedUser ? 'Edit User' : 'Add New User'}
            </h2>
            
            <form onSubmit={handleUserFormSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2" htmlFor="username">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  className="w-full p-2 border rounded"
                  value={userFormData.username}
                  onChange={handleUserFormChange}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2" htmlFor="email">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="w-full p-2 border rounded"
                  value={userFormData.email}
                  onChange={handleUserFormChange}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2" htmlFor="role">
                  Role
                </label>
                <select
                  id="role"
                  name="role"
                  className="w-full p-2 border rounded"
                  value={userFormData.role}
                  onChange={handleUserFormChange}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                  <option value="moderator">Moderator</option>
                </select>
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" htmlFor="status">
                  Status
                </label>
                <select
                  id="status"
                  name="status"
                  className="w-full p-2 border rounded"
                  value={userFormData.status}
                  onChange={handleUserFormChange}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
              
              <div className="flex justify-end space-x-4">
                <Button 
                  variant="secondary" 
                  onClick={() => setUserModalOpen(false)}
                  type="button"
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {selectedUser ? 'Update User' : 'Add User'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
