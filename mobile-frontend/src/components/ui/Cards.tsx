'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  description?: string;
  isLoading?: boolean;
}

export function StatCard({ title, value, change, icon, description, isLoading }: StatCardProps) {
  const isPositiveChange = typeof change === 'number' && change > 0;
  const isNegativeChange = typeof change === 'number' && change < 0;

  return (
    <Card className="overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
            {isLoading ? (
              <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mt-1"></div>
            ) : (
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</h3>
            )}
          </div>
          {icon && <div className="text-indigo-600 dark:text-indigo-400">{icon}</div>}
        </div>
        
        {(isPositiveChange || isNegativeChange) && (
          <div className="mt-2 flex items-center">
            <div
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                isPositiveChange
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}
            >
              {isPositiveChange ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
            </div>
            {description && (
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">{description}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

interface AssetCardProps {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  marketCap?: number;
  volume24h?: number;
  logoUrl?: string;
  onClick?: () => void;
}

export function AssetCard({
  symbol,
  name,
  price,
  change24h,
  marketCap,
  volume24h,
  logoUrl,
  onClick,
}: AssetCardProps) {
  const isPositive = change24h > 0;

  return (
    <Card 
      className={`overflow-hidden transition-all duration-200 ${onClick ? 'cursor-pointer hover:shadow-md' : ''}`}
      onClick={onClick}
    >
      <div className="p-4">
        <div className="flex items-center">
          {logoUrl && (
            <div className="flex-shrink-0 mr-3">
              <div className="h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden">
                <img src={logoUrl} alt={`${symbol} logo`} className="h-8 w-8" />
              </div>
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">{name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">{symbol}</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{formatCurrency(price)}</p>
            <p
              className={`text-sm ${
                isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}
            >
              {isPositive ? '+' : ''}{change24h.toFixed(2)}%
            </p>
          </div>
        </div>
        
        {(marketCap || volume24h) && (
          <div className="mt-4 grid grid-cols-2 gap-4 border-t border-gray-200 dark:border-gray-700 pt-4">
            {marketCap && (
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Market Cap</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{formatCurrency(marketCap)}</p>
              </div>
            )}
            {volume24h && (
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">24h Volume</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{formatCurrency(volume24h)}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

interface PortfolioCardProps {
  name: string;
  value: number;
  change?: number;
  assetCount: number;
  lastUpdated?: string;
  onClick?: () => void;
}

export function PortfolioCard({
  name,
  value,
  change,
  assetCount,
  lastUpdated,
  onClick,
}: PortfolioCardProps) {
  const isPositive = typeof change === 'number' && change > 0;
  const isNegative = typeof change === 'number' && change < 0;

  return (
    <Card 
      className={`overflow-hidden transition-all duration-200 ${onClick ? 'cursor-pointer hover:shadow-md' : ''}`}
      onClick={onClick}
    >
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{name}</h3>
        <div className="mt-2 flex items-center justify-between">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(value)}</p>
          {(isPositive || isNegative) && (
            <div
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                isPositive
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}
            >
              {isPositive ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
            </div>
          )}
        </div>
        <div className="mt-4 flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
          <span>{assetCount} assets</span>
          {lastUpdated && <span>Updated: {lastUpdated}</span>}
        </div>
      </div>
    </Card>
  );
}
