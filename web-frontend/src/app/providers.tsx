'use client';

import React from 'react';
import { ApiProvider } from '@/lib/api';
import { BlockchainProvider } from '@/lib/blockchain';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ApiProvider>
      <BlockchainProvider>
        {children}
      </BlockchainProvider>
    </ApiProvider>
  );
}
