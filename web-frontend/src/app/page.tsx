'use client';

import React, { useState, useEffect } from 'react';
import { useApi } from '@/lib/api';
import { useBlockchain } from '@/lib/blockchain';
import { Button } from '@/components/ui/Button';
import Navbar from '@/components/layout/Navbar';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

export default function Home() {
  const { get, isLoading: apiLoading } = useApi();
  const { connectWallet, isConnected, account, isConnecting, error: walletError } = useBlockchain();
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    const checkApiConnection = async () => {
      try {
        await get('/health');
        setApiStatus('connected');
      } catch (error) {
        setApiStatus('error');
        setApiError('Could not connect to backend API. Please ensure the backend server is running.');
      }
    };

    checkApiConnection();
  }, [get]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-center text-center max-w-3xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Welcome to QuantumNest Capital
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            A futuristic fintech platform integrating AI, Blockchain, Data Science, and Automation.
          </p>
          
          {!isConnected ? (
            <Button 
              size="lg" 
              onClick={connectWallet} 
              isLoading={isConnecting}
              className="mb-8"
            >
              Connect Wallet to Get Started
            </Button>
          ) : (
            <div className="mb-8">
              <p className="text-green-600 dark:text-green-400 font-medium mb-2">
                Wallet Connected: {account?.substring(0, 6)}...{account?.substring(account.length - 4)}
              </p>
              <Button 
                size="lg" 
                onClick={() => window.location.href = '/dashboard'}
              >
                Go to Dashboard
              </Button>
            </div>
          )}
          
          {walletError && (
            <div className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 p-4 rounded-md mb-8">
              {walletError}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mb-12">
            <Card>
              <CardHeader>
                <CardTitle>Backend API Status</CardTitle>
              </CardHeader>
              <CardContent>
                {apiStatus === 'loading' && (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <span className="ml-2">Checking connection...</span>
                  </div>
                )}
                {apiStatus === 'connected' && (
                  <div className="text-green-600 dark:text-green-400 font-medium">
                    Connected to Backend API
                  </div>
                )}
                {apiStatus === 'error' && (
                  <div className="text-red-600 dark:text-red-400 font-medium">
                    {apiError}
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Blockchain Status</CardTitle>
              </CardHeader>
              <CardContent>
                {isConnected ? (
                  <div className="text-green-600 dark:text-green-400 font-medium">
                    Connected to Ethereum Network
                  </div>
                ) : (
                  <div className="text-yellow-600 dark:text-yellow-400 font-medium">
                    Not connected to blockchain. Please connect your wallet.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
            <Card>
              <CardContent className="p-6 flex flex-col items-center">
                <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">AI-Powered Analysis</h3>
                <p className="text-gray-600 dark:text-gray-400 text-center">
                  LSTM models for financial prediction, GARCH models for volatility forecasting, sentiment analysis, and portfolio optimization.
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 flex flex-col items-center">
                <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Blockchain Integration</h3>
                <p className="text-gray-600 dark:text-gray-400 text-center">
                  Asset tokenization, secure trading, portfolio management, and DeFi yield strategies.
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 flex flex-col items-center">
                <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Data Science</h3>
                <p className="text-gray-600 dark:text-gray-400 text-center">
                  Advanced data visualization, market analysis, and predictive analytics for informed investment decisions.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
