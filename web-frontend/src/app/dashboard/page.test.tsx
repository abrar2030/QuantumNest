import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import Dashboard from './page';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the chart data
jest.mock('@/lib/charts', () => ({
  getPortfolioChartData: jest.fn().mockResolvedValue({
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{ data: [100, 200, 300] }]
  }),
  getMarketChartData: jest.fn().mockResolvedValue({
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{ data: [1000, 2000, 3000] }]
  })
}));

describe('Dashboard Page', () => {
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

  test('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  test('renders loading state', () => {
    render(<Dashboard />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders portfolio summary', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/portfolio value/i)).toBeInTheDocument();
      expect(screen.getByText(/24h change/i)).toBeInTheDocument();
      expect(screen.getByText(/total assets/i)).toBeInTheDocument();
    });
  });

  test('renders market overview', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/market overview/i)).toBeInTheDocument();
      expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
      expect(screen.getByText(/ethereum/i)).toBeInTheDocument();
    });
  });

  test('renders portfolio chart', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/portfolio performance/i)).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /portfolio chart/i })).toBeInTheDocument();
    });
  });

  test('renders market chart', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/market trends/i)).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /market chart/i })).toBeInTheDocument();
    });
  });

  test('handles time period selection', async () => {
    render(<Dashboard />);
    const timeSelect = screen.getByRole('combobox', { name: /time period/i });
    fireEvent.change(timeSelect, { target: { value: '1m' } });
    await waitFor(() => {
      expect(screen.getByText(/1 month/i)).toBeInTheDocument();
    });
  });

  test('handles portfolio refresh', async () => {
    render(<Dashboard />);
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);
    await waitFor(() => {
      expect(screen.getByText(/refreshing/i)).toBeInTheDocument();
    });
  });

  test('renders recent transactions', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/recent transactions/i)).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
  });

  test('handles transaction filtering', async () => {
    render(<Dashboard />);
    const filterInput = screen.getByRole('textbox', { name: /filter transactions/i });
    fireEvent.change(filterInput, { target: { value: 'bitcoin' } });
    await waitFor(() => {
      expect(screen.getByText(/filtered results/i)).toBeInTheDocument();
    });
  });

  test('renders notifications', async () => {
    render(<Dashboard />);
    const notificationButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(notificationButton);
    await waitFor(() => {
      expect(screen.getByText(/notifications/i)).toBeInTheDocument();
    });
  });

  test('handles quick actions', async () => {
    render(<Dashboard />);
    const buyButton = screen.getByRole('button', { name: /buy/i });
    fireEvent.click(buyButton);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/market-analysis');
    });
  });

  test('handles chart data error', async () => {
    const mockError = new Error('Failed to load chart data');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/charts'), 'getPortfolioChartData').mockRejectedValueOnce(mockError);
    
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/error loading chart data/i)).toBeInTheDocument();
    });
  });

  test('handles market data error', async () => {
    const mockError = new Error('Failed to load market data');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/charts'), 'getMarketChartData').mockRejectedValueOnce(mockError);
    
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/error loading market data/i)).toBeInTheDocument();
    });
  });
}); 