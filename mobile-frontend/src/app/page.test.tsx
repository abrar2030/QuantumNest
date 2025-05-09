import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import Page from './page';

test('renders welcome message', () => {
  render(<Page />);
  expect(screen.getByText(/welcome/i)).toBeInTheDocument();
});

test('renders additional content', () => {
  render(<Page />);
  expect(screen.getByText(/additional content/i)).toBeInTheDocument();
});

test('interacts with a button', () => {
  render(<Page />);
  const button = screen.getByRole('button', { name: /click me/i });
  fireEvent.click(button);
  expect(screen.getByText(/button clicked/i)).toBeInTheDocument();
}); 