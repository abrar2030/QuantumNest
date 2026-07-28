# QuantumNest

![CI/CD Status](https://img.shields.io/github/actions/workflow/status/quantsingularity/QuantumNest/cicd.yml?branch=main&label=CI/CD&logo=github)
[![Test Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen)](https://github.com/quantsingularity/QuantumNest/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## AI-Powered Tokenized Asset Investment Platform

QuantumNest is an innovative investment platform that combines artificial intelligence, blockchain technology, and quantitative finance to provide sophisticated investment strategies for tokenized assets.

<div align="center">
  <img src="docs/images/QuantumNest_dashboard.bmp" alt="QuantumNest Dashboard" width="80%">
</div>

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation and Setup](#installation-and-setup)
- [Features](#features)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

QuantumNest revolutionizes investment management by leveraging artificial intelligence and blockchain technology to create a platform where users can invest in tokenized assets with sophisticated, AI-driven strategies. The platform combines traditional financial analysis with machine learning to optimize investment decisions while using blockchain to ensure transparency, security, and fractional ownership of high-value assets.

## Project Structure

The project is organized into several main components:

```
QuantumNest/
├── code/                   # Core backend logic, services, and shared utilities
├── docs/                   # Project documentation
├── infrastructure/         # DevOps, deployment, and infra-related code
├── mobile-frontend/        # Mobile application
├── web-frontend/           # Web dashboard
├── scripts/                # Automation, setup, and utility scripts
├── LICENSE                 # License information
└── README.md               # Project overview and instructions
```

## Key Features

### AI-Powered Investment Strategies

| Feature                    | Description                                                                        |
| :------------------------- | :--------------------------------------------------------------------------------- |
| **Predictive Analytics**   | Machine learning models for market prediction and trend analysis                   |
| **Sentiment Analysis**     | Natural language processing to analyze market sentiment from news and social media |
| **Portfolio Optimization** | Advanced algorithms for risk-adjusted portfolio construction                       |
| **Automated Rebalancing**  | Smart rebalancing based on market conditions and risk parameters                   |
| **Anomaly Detection**      | Identification of unusual market patterns and potential opportunities              |

### Tokenized Asset Management

| Feature                       | Description                                                |
| :---------------------------- | :--------------------------------------------------------- |
| **Asset Tokenization**        | Fractional ownership of traditional and alternative assets |
| **Blockchain Transparency**   | Immutable record of ownership and transactions             |
| **Smart Contract Automation** | Automated dividend distribution and governance             |
| **Cross-Chain Compatibility** | Support for multiple blockchain networks                   |
| **Regulatory Compliance**     | Built-in compliance with securities regulations            |

### Quantitative Finance Tools

| Feature                    | Description                                           |
| :------------------------- | :---------------------------------------------------- |
| **Risk Assessment**        | Sophisticated risk metrics and stress testing         |
| **Performance Analytics**  | Comprehensive performance measurement and attribution |
| **Factor Analysis**        | Multi-factor models for investment analysis           |
| **Volatility Forecasting** | GARCH models for volatility prediction                |
| **Scenario Simulation**    | Monte Carlo simulations for portfolio outcomes        |

### User Experience

| Feature                          | Description                                                |
| :------------------------------- | :--------------------------------------------------------- |
| **Intuitive Dashboard**          | Clear visualization of portfolio performance and analytics |
| **Personalized Recommendations** | AI-tailored investment suggestions                         |
| **Educational Resources**        | Learning materials on investment strategies                |
| **Mobile Accessibility**         | Full-featured mobile application                           |
| **Social Features**              | Community insights and expert commentary                   |

## Technology Stack

### Frontend

- **Framework**: Next.js with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: TailwindCSS, Styled Components
- **Data Visualization**: D3.js, Recharts, TradingView
- **Web3 Integration**: ethers.js, web3.js

### Backend

- **Language**: Python, Node.js
- **Framework**: FastAPI, Express
- **Database**: PostgreSQL, MongoDB
- **Cache**: Redis
- **Task Queue**: Celery

### AI & Machine Learning

- **Frameworks**: TensorFlow, PyTorch, scikit-learn
- **Time Series Analysis**: Prophet, statsmodels
- **NLP**: Transformers, spaCy
- **Feature Engineering**: Feature-tools, tsfresh
- **Model Serving**: MLflow, TensorFlow Serving

### Blockchain

- **Networks**: Ethereum, Polygon, Binance Smart Chain
- **Smart Contracts**: Solidity
- **Development Framework**: Hardhat, Truffle
- **Testing**: Waffle, Chai
- **Libraries**: OpenZeppelin

### DevOps

- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Infrastructure as Code**: Terraform

## Architecture

QuantumNest follows a modular architecture with the following components:

```
QuantumNest/
├── Frontend Layer
│   ├── User Interface
│   ├── Data Visualization
│   ├── Authentication
│   └── Web3 Integration
├── Backend Services
│   ├── API Gateway
│   ├── User Service
│   ├── Portfolio Service
│   ├── Market Data Service
│   └── Analytics Service
├── AI Engine
│   ├── Prediction Models
│   ├── Sentiment Analysis
│   ├── Portfolio Optimization
│   └── Risk Assessment
├── Blockchain Layer
│   ├── Asset Tokenization
│   ├── Portfolio Management
│   ├── Trading Platform
│   └── DeFi Integration
└── Data Layer
    ├── Market Data
    ├── User Data
    ├── Transaction History
    └── Model Training Data
```

## Installation and Setup

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Docker and Docker Compose
- MetaMask or compatible Ethereum wallet

### Quick Start with Setup Script

```bash
# Clone the repository
git clone https://github.com/quantsingularity/QuantumNest.git
cd QuantumNest

# Run the setup script
./setup_quantumnest_env.sh

# Start the application
./run_quantumnest.sh
```

### Manual Setup

1. Install frontend dependencies:

```bash
cd web-frontend
npm install
```

2. Install backend dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install blockchain dependencies:

```bash
cd blockchain
npm install
```

4. Set up environment variables:
   - Create `.env` files in both frontend and blockchain directories based on the provided `.env.example` files

### Running the Application

1. Start the frontend development server:

```bash
npm run frontend:dev
```

2. Start the backend server:

```bash
npm run backend:dev
```

3. Compile smart contracts:

```bash
npm run blockchain:compile
```

4. Deploy smart contracts to Goerli testnet:

```bash
npm run blockchain:deploy:goerli
```

## Features

### Web Frontend

| Feature                 | Description                                               |
| :---------------------- | :-------------------------------------------------------- |
| **Home Page**           | Platform overview with key features and benefits          |
| **Portfolio Dashboard** | Comprehensive view of investment holdings and performance |
| **Market Analysis**     | Interactive charts and visualizations of market trends    |
| **AI Recommendations**  | Personalized investment suggestions based on user profile |
| **Blockchain Explorer** | Transparent view of on-chain transactions and assets      |
| **User Dashboard**      | Performance metrics, settings, and account management     |
| **Admin Panel**         | Platform management tools for administrators              |

### Backend APIs

| Feature                     | Description                                          |
| :-------------------------- | :--------------------------------------------------- |
| **User Authentication**     | Secure JWT-based authentication system               |
| **Portfolio Management**    | APIs for creating and managing investment portfolios |
| **Market Data Integration** | Real-time and historical market data processing      |
| **AI Model Endpoints**      | API access to machine learning predictions           |
| **Blockchain Interaction**  | Services for interacting with smart contracts        |
| **Admin Controls**          | Administrative functions and platform management     |

### AI Models

| Model Type                 | Purpose                                                                              |
| :------------------------- | :----------------------------------------------------------------------------------- |
| **LSTM Models**            | Long Short-Term Memory networks for financial time series prediction                 |
| **GARCH Models**           | Generalized Autoregressive Conditional Heteroskedasticity for volatility forecasting |
| **Sentiment Analysis**     | NLP models for market sentiment analysis                                             |
| **Portfolio Optimization** | Multi-objective optimization algorithms                                              |
| **Anomaly Detection**      | Isolation forests and autoencoders for unusual pattern detection                     |

## Testing

The project maintains comprehensive test coverage across all components to ensure reliability and security.

### Test Coverage

| Component              | Coverage | Status |
| ---------------------- | -------- | ------ |
| Frontend Components    | 82%      | ✅     |
| Backend Services       | 88%      | ✅     |
| AI Models              | 85%      | ✅     |
| Blockchain Integration | 86%      | ✅     |
| Smart Contracts        | 90%      | ✅     |
| API Layer              | 80%      | ✅     |
| Overall                | 84%      | ✅     |

### Unit Tests

| Component      | Description                                         |
| :------------- | :-------------------------------------------------- |
| Frontend       | Component tests with Jest and React Testing Library |
| Backend        | Service and controller tests                        |
| Smart Contract | Function tests                                      |
| AI Model       | Validation tests                                    |

### Integration Tests

| Test Type                    | Description                                               |
| :--------------------------- | :-------------------------------------------------------- |
| API endpoint tests           | To verify correct routing and response                    |
| Service interaction tests    | To ensure seamless communication between services         |
| Blockchain integration tests | To validate interaction with smart contracts and networks |
| Data pipeline tests          | To verify data flow and transformation                    |

### End-to-End Tests

| Test Type                      | Description                                           |
| :----------------------------- | :---------------------------------------------------- |
| User journey tests             | With Cypress to cover complete user flows             |
| Portfolio management workflows | To validate core investment functionality             |
| Trading simulations            | To test strategy execution in a simulated environment |
| Authentication flows           | To ensure secure and correct login/logout processes   |

### Running Tests

```bash
# Run frontend tests
cd web-frontend
npm test

# Run backend tests
cd backend
pytest

# Run smart contract tests
cd blockchain
npx hardhat test

# Run all tests
./run_all_tests.sh
```

## CI/CD Pipeline

QuantumNest uses GitHub Actions for continuous integration and deployment:

| Stage                | Control Area                    | Institutional-Grade Detail                                                              |
| :------------------- | :------------------------------ | :-------------------------------------------------------------------------------------- |
| **Formatting Check** | Change Triggers                 | Enforced on all `push` and `pull_request` events to `main` and `develop`                |
|                      | Manual Oversight                | On-demand execution via controlled `workflow_dispatch`                                  |
|                      | Source Integrity                | Full repository checkout with complete Git history for auditability                     |
|                      | Python Runtime Standardization  | Python 3.10 with deterministic dependency caching                                       |
|                      | Backend Code Hygiene            | `autoflake` to detect unused imports/variables using non-mutating diff-based validation |
|                      | Backend Style Compliance        | `black --check` to enforce institutional formatting standards                           |
|                      | Non-Intrusive Validation        | Temporary workspace comparison to prevent unauthorized source modification              |
|                      | Node.js Runtime Control         | Node.js 18 with locked dependency installation via `npm ci`                             |
|                      | Web Frontend Formatting Control | Prettier checks for web-facing assets                                                   |
|                      | Mobile Frontend Formatting      | Prettier enforcement for mobile application codebases                                   |
|                      | Documentation Governance        | Repository-wide Markdown formatting enforcement                                         |
|                      | Infrastructure Configuration    | Prettier validation for YAML/YML infrastructure definitions                             |
|                      | Compliance Gate                 | Any formatting deviation fails the pipeline and blocks merge                            |

## Documentation

| Document                    | Path                 | Description                                                    |
| :-------------------------- | :------------------- | :------------------------------------------------------------- |
| **README**                  | `README.md`          | High-level overview, project scope, and repository entry point |
| **Installation Guide**      | `INSTALLATION.md`    | Step-by-step installation and environment setup                |
| **API Reference**           | `API.md`             | Detailed documentation for all API endpoints                   |
| **CLI Reference**           | `CLI.md`             | Command-line interface usage, commands, and examples           |
| **User Guide**              | `USAGE.md`           | Comprehensive end-user guide, workflows, and examples          |
| **Architecture Overview**   | `ARCHITECTURE.md`    | System architecture, components, and design rationale          |
| **Configuration Guide**     | `CONFIGURATION.md`   | Configuration options, environment variables, and tuning       |
| **Feature Matrix**          | `FEATURE_MATRIX.md`  | Feature coverage, capabilities, and roadmap alignment          |
| **Contributing Guidelines** | `CONTRIBUTING.md`    | Contribution workflow, coding standards, and PR requirements   |
| **Troubleshooting**         | `TROUBLESHOOTING.md` | Common issues, diagnostics, and remediation steps              |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
