# QuantumNest Capital

A futuristic fintech platform integrating AI, Blockchain, Data Science, and Automation.

## Project Overview

QuantumNest Capital is a comprehensive hedge fund platform that combines cutting-edge technologies to provide sophisticated financial services:

- **AI-Powered Analysis**: LSTM models for financial prediction, GARCH models for volatility forecasting, sentiment analysis, and portfolio optimization
- **Blockchain Integration**: Asset tokenization, secure trading, portfolio management, and DeFi yield strategies
- **Modern Frontend**: Responsive design with Next.js and Tailwind CSS
- **Robust Backend**: FastAPI with PostgreSQL database
- **Wallet Integration**: Support for MetaMask, WalletConnect, and Coinbase Wallet

## Project Structure

```
QuantumNest/
├── frontend/               # Next.js frontend application
│   ├── components/         # Reusable UI components
│   ├── pages/              # Application pages
│   ├── styles/             # CSS and styling
│   └── public/             # Static assets
├── backend/                # FastAPI backend application
│   ├── app/                # Main application package
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── db/             # Database models and connection
│   │   ├── models/         # Data models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic services
│   └── venv/               # Python virtual environment
├── blockchain/             # Blockchain integration
│   ├── contracts/          # Smart contracts
│   ├── scripts/            # Deployment scripts
│   └── test/               # Contract tests
└── docs/                   # Documentation
```

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python 3.10+
- PostgreSQL
- Ethereum wallet (MetaMask, WalletConnect, or Coinbase Wallet)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/quantumnest-capital.git
   cd quantumnest-capital
   ```

2. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Install blockchain dependencies:
   ```
   cd blockchain
   npm install
   ```

5. Set up environment variables:
   - Create `.env` files in both frontend and blockchain directories based on the provided `.env.example` files

### Running the Application

1. Start the frontend development server:
   ```
   npm run frontend:dev
   ```

2. Start the backend server:
   ```
   npm run backend:dev
   ```

3. Compile smart contracts:
   ```
   npm run blockchain:compile
   ```

4. Deploy smart contracts to Goerli testnet:
   ```
   npm run blockchain:deploy:goerli
   ```

## Features

### Frontend

- Home page with platform overview
- Portfolio management dashboard
- Market analysis with interactive charts
- AI-powered investment recommendations
- Blockchain explorer for transaction monitoring
- User dashboard with performance metrics
- Admin panel for platform management

### Backend

- User authentication with JWT
- Portfolio management APIs
- Market data integration
- AI model endpoints
- Blockchain interaction services
- Admin control APIs

### AI Models

- LSTM models for financial prediction
- GARCH models for volatility forecasting
- Sentiment analysis for market trends
- PCA for market analysis
- Portfolio optimization algorithms
- Risk profiling system
- AI recommendation engine

### Blockchain

- TokenizedAsset contract for asset tokenization
- PortfolioManager contract for on-chain portfolio management
- TradingPlatform contract for secure trading
- DeFiIntegration contract for yield strategies
- TestToken contract for testing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenZeppelin for secure smart contract libraries
- TailwindCSS for the UI framework
- FastAPI for the backend framework
- Next.js for the frontend framework