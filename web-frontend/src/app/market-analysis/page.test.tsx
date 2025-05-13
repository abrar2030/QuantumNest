import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import MarketAnalysis from './page';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the market data
jest.mock('@/lib/market', () => ({
  getMarketData: jest.fn().mockResolvedValue({
    data: [
      {
        id: 'bitcoin',
        name: 'Bitcoin',
        symbol: 'BTC',
        price: 50000,
        change24h: 5.2,
        marketCap: 1000000000,
        volume24h: 500000000,
      },
    ],
    total: 100,
    page: 1,
    pageSize: 10,
  }),
}));

describe('Market Analysis Page', () => {
  const mockRouter = {
    push: jest.fn(),
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  afterEach(() => {
    cleanup();
    jest.clearAllMocks();
  });

  test('renders market analysis title', () => {
    render(<MarketAnalysis />);
    expect(screen.getByText(/market analysis/i)).toBeInTheDocument();
  });

  test('renders loading state', () => {
    render(<MarketAnalysis />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders market data table', async () => {
    render(<MarketAnalysis />);
    await waitFor(() => {
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
      expect(screen.getByText(/btc/i)).toBeInTheDocument();
    });
  });

  test('handles search filtering', async () => {
    render(<MarketAnalysis />);
    const searchInput = screen.getByRole('textbox', { name: /search/i });
    fireEvent.change(searchInput, { target: { value: 'bitcoin' } });
    await waitFor(() => {
      expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
    });
  });

  test('handles sort by price', async () => {
    render(<MarketAnalysis />);
    const priceHeader = screen.getByRole('columnheader', { name: /price/i });
    fireEvent.click(priceHeader);
    await waitFor(() => {
      expect(screen.getByText(/sorted by price/i)).toBeInTheDocument();
    });
  });

  test('handles sort by market cap', async () => {
    render(<MarketAnalysis />);
    const marketCapHeader = screen.getByRole('columnheader', { name: /market cap/i });
    fireEvent.click(marketCapHeader);
    await waitFor(() => {
      expect(screen.getByText(/sorted by market cap/i)).toBeInTheDocument();
    });
  });

  test('handles sort by volume', async () => {
    render(<MarketAnalysis />);
    const volumeHeader = screen.getByRole('columnheader', { name: /volume/i });
    fireEvent.click(volumeHeader);
    await waitFor(() => {
      expect(screen.getByText(/sorted by volume/i)).toBeInTheDocument();
    });
  });

  test('handles time period selection', async () => {
    render(<MarketAnalysis />);
    const timeSelect = screen.getByRole('combobox', { name: /time period/i });
    fireEvent.change(timeSelect, { target: { value: '1d' } });
    await waitFor(() => {
      expect(screen.getByText(/24 hours/i)).toBeInTheDocument();
    });
  });

  test('handles market cap filter', async () => {
    render(<MarketAnalysis />);
    const marketCapFilter = screen.getByRole('combobox', { name: /market cap/i });
    fireEvent.change(marketCapFilter, { target: { value: 'large' } });
    await waitFor(() => {
      expect(screen.getByText(/large cap/i)).toBeInTheDocument();
    });
  });

  test('handles volume filter', async () => {
    render(<MarketAnalysis />);
    const volumeFilter = screen.getByRole('combobox', { name: /volume/i });
    fireEvent.change(volumeFilter, { target: { value: 'high' } });
    await waitFor(() => {
      expect(screen.getByText(/high volume/i)).toBeInTheDocument();
    });
  });

  test('handles price change filter', async () => {
    render(<MarketAnalysis />);
    const changeFilter = screen.getByRole('combobox', { name: /price change/i });
    fireEvent.change(changeFilter, { target: { value: 'gainers' } });
    await waitFor(() => {
      expect(screen.getByText(/top gainers/i)).toBeInTheDocument();
    });
  });

  test('handles refresh', async () => {
    render(<MarketAnalysis />);
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);
    await waitFor(() => {
      expect(screen.getByText(/refreshing/i)).toBeInTheDocument();
    });
  });

  test('handles asset selection', async () => {
    render(<MarketAnalysis />);
    const assetRow = screen.getByText(/bitcoin/i).closest('tr');
    fireEvent.click(assetRow!);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/market-analysis/bitcoin');
    });
  });

  test('handles pagination', async () => {
    render(<MarketAnalysis />);
    await waitFor(() => {
      expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument();
    });

    const nextPageButton = screen.getByRole('button', { name: /next page/i });
    fireEvent.click(nextPageButton);
    await waitFor(() => {
      expect(screen.getByText(/page 2 of 10/i)).toBeInTheDocument();
    });
  });

  test('handles market data error', async () => {
    const mockError = new Error('Failed to load market data');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/market'), 'getMarketData').mockRejectedValueOnce(mockError);
    
    render(<MarketAnalysis />);
    await waitFor(() => {
      expect(screen.getByText(/error loading market data/i)).toBeInTheDocument();
    });
  });

  test('handles empty market data', async () => {
    jest.spyOn(require('@/lib/market'), 'getMarketData').mockResolvedValueOnce({
      data: [],
      total: 0,
      page: 1,
      pageSize: 10,
    });
    
    render(<MarketAnalysis />);
    await waitFor(() => {
      expect(screen.getByText(/no market data available/i)).toBeInTheDocument();
    });
  });
}); 