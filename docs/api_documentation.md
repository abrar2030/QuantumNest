# QuantumNest Capital - API Documentation

## Overview

The QuantumNest Capital API provides programmatic access to the platform's features, allowing developers to integrate with the system and build custom applications. This RESTful API uses JSON for request and response bodies and JWT for authentication.

## Base URL

```
https://api.quantumnest.capital/v1
```

## Authentication

### JWT Authentication

Most API endpoints require authentication using JSON Web Tokens (JWT).

To authenticate:

1. Obtain a JWT token by calling the `/auth/login` endpoint
2. Include the token in the Authorization header of subsequent requests:

```
Authorization: Bearer <your_jwt_token>
```

Tokens expire after 24 hours and need to be refreshed using the `/auth/refresh` endpoint.

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed in the current period
- `X-RateLimit-Remaining`: Remaining requests in the current period
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

## Endpoints

### Authentication

#### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user_id": "12345",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-04-09T12:00:00Z"
}
```

#### POST /auth/login

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "12345",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /auth/refresh

Refresh an expired JWT token.

**Request Headers:**
```
Authorization: Bearer <expired_token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### GET /auth/me

Get current authenticated user information.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "12345",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-04-09T12:00:00Z",
  "role": "user",
  "risk_profile": {
    "score": 7,
    "category": "growth"
  }
}
```

### Portfolio Management

#### GET /portfolios

Get all portfolios for the authenticated user.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Maximum number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "portfolio_123",
      "name": "Growth Portfolio",
      "description": "High-growth technology stocks",
      "created_at": "2025-03-15T10:30:00Z",
      "total_value": 15000.50,
      "performance": {
        "daily": 1.2,
        "weekly": 3.5,
        "monthly": 5.8,
        "yearly": 12.3
      },
      "risk_score": 7.5
    },
    {
      "id": "portfolio_456",
      "name": "Dividend Income",
      "description": "Stable dividend-paying stocks",
      "created_at": "2025-02-20T14:15:00Z",
      "total_value": 25000.75,
      "performance": {
        "daily": 0.5,
        "weekly": 1.2,
        "monthly": 2.8,
        "yearly": 8.5
      },
      "risk_score": 4.2
    }
  ]
}
```

#### POST /portfolios

Create a new portfolio.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Tech Growth",
  "description": "Portfolio focused on high-growth tech companies",
  "risk_tolerance": "high"
}
```

**Response:**
```json
{
  "id": "portfolio_789",
  "name": "Tech Growth",
  "description": "Portfolio focused on high-growth tech companies",
  "created_at": "2025-04-09T15:45:00Z",
  "total_value": 0,
  "performance": {
    "daily": 0,
    "weekly": 0,
    "monthly": 0,
    "yearly": 0
  },
  "risk_score": 8.0,
  "risk_tolerance": "high"
}
```

#### GET /portfolios/{portfolio_id}

Get detailed information about a specific portfolio.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "portfolio_123",
  "name": "Growth Portfolio",
  "description": "High-growth technology stocks",
  "created_at": "2025-03-15T10:30:00Z",
  "last_updated": "2025-04-08T16:20:00Z",
  "total_value": 15000.50,
  "cash_balance": 1250.75,
  "performance": {
    "daily": 1.2,
    "weekly": 3.5,
    "monthly": 5.8,
    "yearly": 12.3
  },
  "risk_score": 7.5,
  "assets": [
    {
      "id": "asset_001",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 10,
      "purchase_price": 150.25,
      "current_price": 175.50,
      "value": 1755.00,
      "allocation": 12.5,
      "gain_loss": {
        "amount": 252.50,
        "percentage": 16.8
      }
    },
    {
      "id": "asset_002",
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "quantity": 8,
      "purchase_price": 220.75,
      "current_price": 245.30,
      "value": 1962.40,
      "allocation": 14.0,
      "gain_loss": {
        "amount": 196.40,
        "percentage": 11.1
      }
    }
  ]
}
```

#### PUT /portfolios/{portfolio_id}

Update a portfolio.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Growth Portfolio",
  "description": "Updated description for growth portfolio",
  "risk_tolerance": "moderate"
}
```

**Response:**
```json
{
  "id": "portfolio_123",
  "name": "Updated Growth Portfolio",
  "description": "Updated description for growth portfolio",
  "risk_tolerance": "moderate",
  "updated_at": "2025-04-09T16:30:00Z"
}
```

#### DELETE /portfolios/{portfolio_id}

Delete a portfolio.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```
204 No Content
```

#### POST /portfolios/{portfolio_id}/assets

Add an asset to a portfolio.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "symbol": "GOOGL",
  "quantity": 5,
  "purchase_price": 2750.50
}
```

**Response:**
```json
{
  "id": "asset_003",
  "symbol": "GOOGL",
  "name": "Alphabet Inc.",
  "quantity": 5,
  "purchase_price": 2750.50,
  "current_price": 2780.25,
  "value": 13901.25,
  "allocation": 10.2,
  "gain_loss": {
    "amount": 148.75,
    "percentage": 1.1
  }
}
```

### Market Data

#### GET /market/assets

Get a list of available assets.

**Query Parameters:**
- `type` (optional): Filter by asset type (stock, bond, crypto, etc.)
- `sector` (optional): Filter by sector
- `search` (optional): Search by name or symbol
- `limit` (optional): Maximum number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "count": 100,
  "next": "/market/assets?offset=50&limit=50",
  "previous": null,
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "type": "stock",
      "sector": "Technology",
      "current_price": 175.50,
      "change": 2.35,
      "change_percent": 1.36,
      "market_cap": 2850000000000
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "type": "stock",
      "sector": "Technology",
      "current_price": 245.30,
      "change": 1.20,
      "change_percent": 0.49,
      "market_cap": 1950000000000
    }
  ]
}
```

#### GET /market/assets/{symbol}

Get detailed information about a specific asset.

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "type": "stock",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "current_price": 175.50,
  "change": 2.35,
  "change_percent": 1.36,
  "open": 173.20,
  "high": 176.40,
  "low": 172.80,
  "volume": 75000000,
  "avg_volume": 82000000,
  "market_cap": 2850000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.65,
  "52_week_high": 182.94,
  "52_week_low": 124.17,
  "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
}
```

#### GET /market/historical/{symbol}

Get historical price data for an asset.

**Query Parameters:**
- `period` (optional): Time period (1d, 5d, 1m, 3m, 6m, 1y, 5y)
- `interval` (optional): Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "period": "1m",
  "interval": "1d",
  "data": [
    {
      "date": "2025-03-10T00:00:00Z",
      "open": 170.25,
      "high": 172.40,
      "low": 169.80,
      "close": 171.50,
      "volume": 68000000
    },
    {
      "date": "2025-03-11T00:00:00Z",
      "open": 171.75,
      "high": 173.20,
      "low": 170.90,
      "close": 172.80,
      "volume": 72000000
    }
  ]
}
```

### AI Recommendations

#### GET /ai/recommendations

Get AI-generated investment recommendations.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `portfolio_id` (optional): Get recommendations for a specific portfolio
- `risk_level` (optional): Filter by risk level (low, moderate, high)
- `limit` (optional): Maximum number of results (default: 10)

**Response:**
```json
{
  "timestamp": "2025-04-09T16:45:00Z",
  "market_outlook": {
    "sentiment": "bullish",
    "confidence": 75.5,
    "key_factors": [
      "Strong earnings reports",
      "Favorable economic indicators",
      "Decreasing inflation"
    ]
  },
  "recommendations": [
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "type": "buy",
      "confidence": 85.2,
      "target_price": 950.00,
      "current_price": 875.30,
      "potential_upside": 8.5,
      "time_horizon": "medium",
      "risk_level": "moderate",
      "rationale": "Strong growth in AI chip demand and expanding data center market share."
    },
    {
      "symbol": "AMZN",
      "name": "Amazon.com Inc.",
      "type": "buy",
      "confidence": 82.7,
      "target_price": 180.00,
      "current_price": 160.25,
      "potential_upside": 12.3,
      "time_horizon": "long",
      "risk_level": "low",
      "rationale": "Continued e-commerce dominance and AWS growth acceleration."
    }
  ]
}
```

#### POST /ai/analyze

Analyze a portfolio or specific assets.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "portfolio_id": "portfolio_123",
  "analysis_type": "risk_return",
  "time_horizon": "1y"
}
```

**Response:**
```json
{
  "analysis_id": "analysis_456",
  "portfolio_id": "portfolio_123",
  "analysis_type": "risk_return",
  "timestamp": "2025-04-09T17:00:00Z",
  "results": {
    "expected_return": 12.5,
    "volatility": 18.2,
    "sharpe_ratio": 0.68,
    "var_95": 8.4,
    "max_drawdown": 15.3,
    "risk_contribution": [
      {
        "symbol": "AAPL",
        "contribution": 22.5
      },
      {
        "symbol": "MSFT",
        "contribution": 18.7
      }
    ],
    "optimization_potential": 3.2,
    "recommendations": [
      "Reduce technology sector exposure by 5%",
      "Add 3% allocation to consumer staples",
      "Consider hedging strategies to reduce downside risk"
    ]
  }
}
```

### Blockchain Integration

#### GET /blockchain/assets

Get tokenized assets available on the blockchain.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
      "symbol": "qAAPL",
      "name": "QuantumNest Apple Stock Token",
      "asset_type": "stock",
      "underlying_symbol": "AAPL",
      "current_value": 175.50,
      "total_supply": 1000000,
      "market_cap": 175500000,
      "trading_volume_24h": 2500000,
      "trading_enabled": true
    },
    {
      "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
      "symbol": "qGOLD",
      "name": "QuantumNest Gold Token",
      "asset_type": "commodity",
      "underlying_symbol": "XAU",
      "current_value": 2150.75,
      "total_supply": 500000,
      "market_cap": 1075375000,
      "trading_volume_24h": 1200000,
      "trading_enabled": true
    }
  ]
}
```

#### GET /blockchain/portfolio

Get on-chain portfolio information.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "wallet_address": "0x9876543210fedcba9876543210fedcba98765432",
  "portfolios": [
    {
      "portfolio_id": 1,
      "name": "Growth Portfolio",
      "creation_date": "2025-03-15T10:30:00Z",
      "assets": [
        {
          "token_address": "0x1234567890abcdef1234567890abcdef12345678",
          "symbol": "qAAPL",
          "name": "QuantumNest Apple Stock Token",
          "balance": 100,
          "value": 17550.00,
          "allocation": 45.2
        },
        {
          "token_address": "0xabcdef1234567890abcdef1234567890abcdef12",
          "symbol": "qGOLD",
          "name": "QuantumNest Gold Token",
          "balance": 10,
          "value": 21507.50,
          "allocation": 54.8
        }
      ],
      "total_value": 39057.50
    }
  ]
}
```

#### POST /blockchain/trade

Execute a trade on the blockchain.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "token_address": "0x1234567890abcdef1234567890abcdef12345678",
  "type": "buy",
  "amount": 10,
  "price_limit": 180.00
}
```

**Response:**
```json
{
  "transaction_hash": "0xabc123def456789012345678901234567890123456789012345678901234567890",
  "status": "pending",
  "token_address": "0x1234567890abcdef1234567890abcdef12345678",
  "symbol": "qAAPL",
  "type": "buy",
  "amount": 10,
  "price": 175.50,
  "total_value": 1755.00,
  "gas_fee": 0.005,
  "timestamp": "2025-04-09T17:15:00Z",
  "estimated_confirmation_time": "2025-04-09T17:20:00Z"
}
```

### Admin Endpoints

#### GET /admin/users

Get a list of all users (admin only).

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 100,
  "next": "/admin/users?offset=50&limit=50",
  "previous": null,
  "results": [
    {
      "user_id": "12345",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2025-03-15T10:30:00Z",
      "last_login": "2025-04-09T15:45:00Z",
      "status": "active",
      "role": "user"
    }
  ]
}
```

#### GET /admin/dashboard

Get admin dashboard data (admin only).

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_stats": {
    "total_users": 1250,
    "active_users": 875,
    "new_users_today": 15,
    "new_users_this_week": 85
  },
  "portfolio_stats": {
    "total_portfolios": 1850,
    "average_portfolio_value": 25000.50,
    "total_assets_under_management": 46250925.00
  },
  "transaction_stats": {
    "transactions_today": 350,
    "transactions_this_week": 2250,
    "average_transaction_value": 5000.75
  },
  "blockchain_stats": {
    "total_tokenized_assets": 25,
    "total_smart_contracts": 45,
    "total_on_chain_transactions": 12500
  },
  "system_health": {
    "api_uptime": 99.98,
    "database_performance": "optimal",
    "blockchain_node_status": "connected"
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Request succeeded with no response body
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses follow this format:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request was invalid",
    "details": [
      "Field 'email' is required",
      "Password must be at least 8 characters"
    ]
  }
}
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

- `limit`: Number of results to return (default varies by endpoint)
- `offset`: Number of results to skip (default: 0)

Paginated responses include:

- `count`: Total number of results
- `next`: URL for the next page (null if no more results)
- `previous`: URL for the previous page (null if on first page)
- `results`: Array of items for the current page

## Versioning

The API is versioned in the URL path (e.g., `/v1/portfolios`). When breaking changes are introduced, a new version will be released while maintaining support for previous versions for a deprecation period.

## Webhooks

QuantumNest Capital supports webhooks for real-time notifications. To set up webhooks:

1. Register a webhook URL in your account settings
2. Select the events you want to receive
3. We'll send HTTP POST requests to your URL when events occur

Webhook payloads include:

- `event_type`: Type of event (e.g., "portfolio.updated", "trade.executed")
- `timestamp`: When the event occurred
- `data`: Event-specific data
- `signature`: HMAC signature for verification

## SDKs and Client Libraries

Official client libraries are available for:

- JavaScript/TypeScript
- Python
- Java
- Ruby

Visit our [GitHub repository](https://github.com/quantumnest/api-clients) for documentation and examples.
