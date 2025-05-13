import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import Portfolio from './page';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the portfolio data
jest.mock('@/lib/portfolio', () => ({
  getPortfolioData: jest.fn().mockResolvedValue({
    totalValue: 100000,
    assets: [
      {
        id: 'bitcoin',
        name: 'Bitcoin',
        symbol: 'BTC',
        amount: 1.5,
        value: 75000,
        change24h: 5.2,
      },
    ],
    transactions: [
      {
        id: '1',
        type: 'buy',
        asset: 'Bitcoin',
        amount: 1.5,
        price: 50000,
        date: '2024-01-01',
      },
    ],
    history: [
      {
        date: '2024-01-01',
        value: 100000,
        change: 5.2,
      },
    ],
  }),
}));

describe('Portfolio Page', () => {
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

  test('renders portfolio title', () => {
    render(<Portfolio />);
    expect(screen.getByText(/portfolio/i)).toBeInTheDocument();
  });

  test('renders loading state', () => {
    render(<Portfolio />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders portfolio summary', async () => {
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/total value/i)).toBeInTheDocument();
      expect(screen.getByText(/\$100,000/i)).toBeInTheDocument();
    });
  });

  test('renders assets list', async () => {
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
      expect(screen.getByText(/1.5 btc/i)).toBeInTheDocument();
      expect(screen.getByText(/\$75,000/i)).toBeInTheDocument();
    });
  });

  test('renders transactions list', async () => {
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/transactions/i)).toBeInTheDocument();
      expect(screen.getByText(/buy/i)).toBeInTheDocument();
      expect(screen.getByText(/1.5 btc/i)).toBeInTheDocument();
    });
  });

  test('renders portfolio history', async () => {
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/portfolio history/i)).toBeInTheDocument();
      expect(screen.getByText(/2024-01-01/i)).toBeInTheDocument();
      expect(screen.getByText(/\$100,000/i)).toBeInTheDocument();
    });
  });

  test('handles asset search', async () => {
    render(<Portfolio />);
    const searchInput = screen.getByRole('textbox', { name: /search assets/i });
    fireEvent.change(searchInput, { target: { value: 'bitcoin' } });
    await waitFor(() => {
      expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
    });
  });

  test('handles transaction search', async () => {
    render(<Portfolio />);
    const searchInput = screen.getByRole('textbox', { name: /search transactions/i });
    fireEvent.change(searchInput, { target: { value: 'buy' } });
    await waitFor(() => {
      expect(screen.getByText(/buy/i)).toBeInTheDocument();
    });
  });

  test('handles sort by value', async () => {
    render(<Portfolio />);
    const valueHeader = screen.getByRole('columnheader', { name: /value/i });
    fireEvent.click(valueHeader);
    await waitFor(() => {
      expect(screen.getByText(/sorted by value/i)).toBeInTheDocument();
    });
  });

  test('handles sort by change', async () => {
    render(<Portfolio />);
    const changeHeader = screen.getByRole('columnheader', { name: /24h change/i });
    fireEvent.click(changeHeader);
    await waitFor(() => {
      expect(screen.getByText(/sorted by change/i)).toBeInTheDocument();
    });
  });

  test('handles time period selection', async () => {
    render(<Portfolio />);
    const timeSelect = screen.getByRole('combobox', { name: /time period/i });
    fireEvent.change(timeSelect, { target: { value: '1m' } });
    await waitFor(() => {
      expect(screen.getByText(/1 month/i)).toBeInTheDocument();
    });
  });

  test('handles refresh', async () => {
    render(<Portfolio />);
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);
    await waitFor(() => {
      expect(screen.getByText(/refreshing/i)).toBeInTheDocument();
    });
  });

  test('handles add asset', async () => {
    render(<Portfolio />);
    const addButton = screen.getByRole('button', { name: /add asset/i });
    fireEvent.click(addButton);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/market-analysis');
    });
  });

  test('handles asset details', async () => {
    render(<Portfolio />);
    const assetRow = screen.getByText(/bitcoin/i).closest('tr');
    fireEvent.click(assetRow!);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/portfolio/bitcoin');
    });
  });

  test('handles portfolio data error', async () => {
    const mockError = new Error('Failed to load portfolio data');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/portfolio'), 'getPortfolioData').mockRejectedValueOnce(mockError);
    
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/error loading portfolio data/i)).toBeInTheDocument();
    });
  });

  test('handles empty portfolio', async () => {
    jest.spyOn(require('@/lib/portfolio'), 'getPortfolioData').mockResolvedValueOnce({
      totalValue: 0,
      assets: [],
      transactions: [],
      history: [],
    });
    
    render(<Portfolio />);
    await waitFor(() => {
      expect(screen.getByText(/no assets in portfolio/i)).toBeInTheDocument();
    });
  });
}); 