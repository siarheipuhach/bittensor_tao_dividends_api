# 🧠 Bittensor Sentiment Staking API

A FastAPI-based service that queries the Bittensor blockchain to retrieve TAO dividend data, performs sentiment analysis on related Twitter content, and automatically triggers stake/unstake operations based on the sentiment score.

## 🚀 Features

- **/api/v1/tao_dividends** endpoint
  - Query Bittensor TaoDividends by `netuid` and/or `hotkey`
  - Optional `trade=true` triggers sentiment analysis + stake adjustment
- **Redis Caching** to reduce blockchain calls
- **Chutes AI** for LLM-based sentiment analysis
- **Datura API** for relevant tweet discovery
- **AsyncSubtensor** + **btwallet** for testnet extrinsics
- **Dockerized** for easy local/dev deployment
- **Celery** background tasks for non-blocking staking

---

## 🐳 Run with Docker

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone https://github.com/siarheipuhach/bittensor_tao_dividends_api.git
cd bittensor_tao_dividends_api
```

### 2. Add `.env`

Create a `.env` file in the root of the project with:

```env
REDIS_URL=redis://redis:6379
AUTH_TOKEN=your_auth_token_here
CHUTES_API_KEY=your_chutes_api_key
DATURA_API_KEY=your_datura_api_key
```

> Replace the API keys with your actual credentials.

### 3. Build and Run

```bash
docker compose up --build
```

- API runs at: [http://localhost:8000](http://localhost:8000)
- Redis runs in the background
- Celery worker runs with access to the API and Redis

---

## 📬 Example Request

```http
GET /api/v1/tao_dividends?netuid=18&hotkey=5FFApa...&trade=true
Authorization: Bearer your_auth_token_here
```

Response:

```json
{
  "netuid": 18,
  "hotkey": "5FFApa...",
  "dividend": 1234567,
  "cached": false,
  "stake_tx_triggered": true
}
```

---

## ⚙️ How It Works

- If `trade=true`, the endpoint:
  1. Queries Datura for recent tweets about Bittensor subnet
  2. Sends tweets to Chutes LLM to extract sentiment score (-100 to +100)
  3. Uses `btwallet` + `AsyncSubtensor` to submit `add_stake` or `unstake` on the testnet

---

## 🧪 Running Tests

```bash
docker compose exec api pytest
```

---

## 🛠 Tech Stack

- Python 3.11
- FastAPI
- Celery
- Redis
- Docker
- AsyncSubtensor / Bittensor
- btWallet SDK
- Chutes.ai & Datura.ai APIs

---

## 🧼 TODO

- Logging
- Unit tests for staking logic
- Better error handling for wallet password prompts
