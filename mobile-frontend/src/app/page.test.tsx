import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import Page from './page';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

describe('Mobile Frontend Main Page', () => {
  const mockRouter = {
    push: jest.fn(),
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  test('renders welcome message', () => {
    render(<Page />);
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  test('renders navigation menu', () => {
    render(<Page />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/portfolio/i)).toBeInTheDocument();
    expect(screen.getByText(/market/i)).toBeInTheDocument();
  });

  test('navigates to dashboard', async () => {
    render(<Page />);
    const dashboardLink = screen.getByText(/dashboard/i);
    fireEvent.click(dashboardLink);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('navigates to portfolio', async () => {
    render(<Page />);
    const portfolioLink = screen.getByText(/portfolio/i);
    fireEvent.click(portfolioLink);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/portfolio');
    });
  });

  test('navigates to market analysis', async () => {
    render(<Page />);
    const marketLink = screen.getByText(/market/i);
    fireEvent.click(marketLink);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/market-analysis');
    });
  });

  test('renders user profile section', () => {
    render(<Page />);
    expect(screen.getByText(/profile/i)).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /profile/i })).toBeInTheDocument();
  });

  test('handles theme toggle', () => {
    render(<Page />);
    const themeToggle = screen.getByRole('button', { name: /theme/i });
    fireEvent.click(themeToggle);
    expect(document.documentElement).toHaveClass('dark');
  });

  test('renders notifications', () => {
    render(<Page />);
    const notificationButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(notificationButton);
    expect(screen.getByText(/notifications/i)).toBeInTheDocument();
  });

  test('handles search functionality', async () => {
    render(<Page />);
    const searchInput = screen.getByRole('searchbox');
    fireEvent.change(searchInput, { target: { value: 'bitcoin' } });
    await waitFor(() => {
      expect(screen.getByText(/search results/i)).toBeInTheDocument();
    });
  });

  test('renders market overview', () => {
    render(<Page />);
    expect(screen.getByText(/market overview/i)).toBeInTheDocument();
    expect(screen.getByText(/bitcoin/i)).toBeInTheDocument();
    expect(screen.getByText(/ethereum/i)).toBeInTheDocument();
  });

  test('handles portfolio summary', () => {
    render(<Page />);
    expect(screen.getByText(/portfolio summary/i)).toBeInTheDocument();
    expect(screen.getByText(/total value/i)).toBeInTheDocument();
    expect(screen.getByText(/24h change/i)).toBeInTheDocument();
  });
}); 