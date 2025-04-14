'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ApiContextType {
  apiUrl: string;
  isLoading: boolean;
  error: string | null;
  get: <T>(endpoint: string) => Promise<T>;
  post: <T>(endpoint: string, data: any) => Promise<T>;
  put: <T>(endpoint: string, data: any) => Promise<T>;
  delete: <T>(endpoint: string) => Promise<T>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

interface ApiProviderProps {
  children: ReactNode;
}

export function ApiProvider({ children }: ApiProviderProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // In production, this would be set based on environment variables
  const apiUrl = 'http://localhost:8000';

  const handleResponse = async (response: Response) => {
    setIsLoading(false);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Error: ${response.status} ${response.statusText}`;
      setError(errorMessage);
      throw new Error(errorMessage);
    }
    
    return response.json();
  };

  const get = async <T,>(endpoint: string): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // In a real app, we would include authentication headers here
        },
      });
      
      return handleResponse(response);
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const post = async <T,>(endpoint: string, data: any): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // In a real app, we would include authentication headers here
        },
        body: JSON.stringify(data),
      });
      
      return handleResponse(response);
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const put = async <T,>(endpoint: string, data: any): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          // In a real app, we would include authentication headers here
        },
        body: JSON.stringify(data),
      });
      
      return handleResponse(response);
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const deleteRequest = async <T,>(endpoint: string): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          // In a real app, we would include authentication headers here
        },
      });
      
      return handleResponse(response);
    } catch (err) {
      setIsLoading(false);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const value = {
    apiUrl,
    isLoading,
    error,
    get,
    post,
    put,
    delete: deleteRequest,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

export function useApi() {
  const context = useContext(ApiContext);
  
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  
  return context;
}
