import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import Settings from './page';

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the settings data
jest.mock('@/lib/settings', () => ({
  getSettings: jest.fn().mockResolvedValue({
    theme: 'dark',
    language: 'en',
    notifications: {
      email: true,
      push: true,
      priceAlerts: true,
    },
    security: {
      twoFactorEnabled: true,
      lastPasswordChange: '2024-01-01',
    },
  }),
  updateSettings: jest.fn().mockResolvedValue(true),
  validateSettings: jest.fn().mockResolvedValue(true),
}));

describe('Settings Page', () => {
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

  test('renders settings title', () => {
    render(<Settings />);
    expect(screen.getByText(/settings/i)).toBeInTheDocument();
  });

  test('renders loading state', () => {
    render(<Settings />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders theme settings', async () => {
    render(<Settings />);
    await waitFor(() => {
      expect(screen.getByText(/theme/i)).toBeInTheDocument();
      expect(screen.getByText(/dark/i)).toBeInTheDocument();
    });
  });

  test('handles theme change', async () => {
    render(<Settings />);
    const themeSelect = screen.getByRole('combobox', { name: /theme/i });
    fireEvent.change(themeSelect, { target: { value: 'light' } });
    await waitFor(() => {
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });
  });

  test('renders language settings', async () => {
    render(<Settings />);
    await waitFor(() => {
      expect(screen.getByText(/language/i)).toBeInTheDocument();
      expect(screen.getByText(/english/i)).toBeInTheDocument();
    });
  });

  test('handles language change', async () => {
    render(<Settings />);
    const languageSelect = screen.getByRole('combobox', { name: /language/i });
    fireEvent.change(languageSelect, { target: { value: 'es' } });
    await waitFor(() => {
      expect(screen.getByText(/spanish/i)).toBeInTheDocument();
    });
  });

  test('renders notification settings', async () => {
    render(<Settings />);
    await waitFor(() => {
      expect(screen.getByText(/notifications/i)).toBeInTheDocument();
      expect(screen.getByText(/email/i)).toBeInTheDocument();
      expect(screen.getByText(/push/i)).toBeInTheDocument();
    });
  });

  test('handles notification toggle', async () => {
    render(<Settings />);
    const emailToggle = screen.getByRole('checkbox', { name: /email/i });
    fireEvent.click(emailToggle);
    await waitFor(() => {
      expect(emailToggle).not.toBeChecked();
    });
  });

  test('renders security settings', async () => {
    render(<Settings />);
    await waitFor(() => {
      expect(screen.getByText(/security/i)).toBeInTheDocument();
      expect(screen.getByText(/two-factor/i)).toBeInTheDocument();
    });
  });

  test('handles two-factor toggle', async () => {
    render(<Settings />);
    const twoFactorToggle = screen.getByRole('checkbox', { name: /two-factor/i });
    fireEvent.click(twoFactorToggle);
    await waitFor(() => {
      expect(twoFactorToggle).not.toBeChecked();
    });
  });

  test('handles password change', async () => {
    render(<Settings />);
    const changePasswordButton = screen.getByRole('button', { name: /change password/i });
    fireEvent.click(changePasswordButton);
    await waitFor(() => {
      expect(screen.getByText(/change password/i)).toBeInTheDocument();
    });
  });

  test('handles save settings', async () => {
    render(<Settings />);
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);
    await waitFor(() => {
      expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
    });
  });

  test('handles cancel', async () => {
    render(<Settings />);
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('handles settings validation', async () => {
    jest.spyOn(require('@/lib/settings'), 'validateSettings').mockResolvedValueOnce(false);
    
    render(<Settings />);
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);
    await waitFor(() => {
      expect(screen.getByText(/invalid settings/i)).toBeInTheDocument();
    });
  });

  test('handles settings error', async () => {
    const mockError = new Error('Failed to load settings');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/settings'), 'getSettings').mockRejectedValueOnce(mockError);
    
    render(<Settings />);
    await waitFor(() => {
      expect(screen.getByText(/error loading settings/i)).toBeInTheDocument();
    });
  });

  test('handles update error', async () => {
    const mockError = new Error('Failed to update settings');
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(require('@/lib/settings'), 'updateSettings').mockRejectedValueOnce(mockError);
    
    render(<Settings />);
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);
    await waitFor(() => {
      expect(screen.getByText(/error saving settings/i)).toBeInTheDocument();
    });
  });
}); 