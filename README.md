# Currency Converter REST API

FastAPI service that converts currency amounts using **near‑real‑time FX rates derived from Binance BTC quotes**. 
Rates are refreshed at most once per hour.

---

## ✨ Features

- `GET /v1/rates/fx-rate` with query params: `ccy_from`, `ccy_to`, `quantity`
- `POST /v1/rates/fx-rate` with request body: `{
  "ccy_from": "str",
  "ccy_to": "str",
  "fx_rate": 1
}`
- `DELETE /v1/rates/fx-rate` with query params: `ccy_pair`
- Maps **USD → USDT**
- Concurrent fetching + **in‑memory cache** (TTL default: 3600s though its configurable with .env)
- User able to override the Fx Rate and clear the overrides when needed
- Price value rounded 2 decimal places

---

## 🚀 Endpoint

### `GET /v1/rates/fx-rate`

Query parameters:

- `ccy_from` — 3‑letter source currency (e.g., `USD`, `EUR`, `GBP`) *(required)*
- `ccy_to` — 3‑letter target currency (e.g., `GBP`) *(required)*
- `quantity` — positive number > 0 *(required)*

**Response (JSON):**

```json
{
  "quantity": 779.77,
  "ccy": "GBP"
}
```

> Note: Value depends on the current market price at the time of the request.

**Examples:**

```bash
# Convert 1000 USD -> GBP
curl -X 'GET' \
  'http://127.0.0.1:8000/v1/rates/fx-rate?ccy_from=USD&ccy_to=GBP&quantity=1000' \
  -H 'accept: application/json'

# Convert 200 EUR -> USD
curl -X 'GET' \
  'http://127.0.0.1:8000/v1/rates/fx-rate?ccy_from=EUR&ccy_to=USD&quantity=200' \
  -H 'accept: application/json'
```

### `POST /v1/rates/fx-rate/override`

Request Body:

- `ccy_from` — 3‑letter source currency (e.g., `USD`, `EUR`, `GBP`) *(required)*
- `ccy_to` — 3‑letter target currency (e.g., `GBP`) *(required)*
- `fx_rate` — positive float number > 0 *(required)*

**Response (JSON):**

```json
{
  "code": 200,
  "status": "Fx rate for USDEUR set to 0.543"
}
```

**Examples:**

```bash
# Override Fx Rate for USD/EUR with value 0.543
curl -X 'POST' \
  'http://127.0.0.1:8000/v1/rates/fx-rate/override' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ccy_from": "USD",
  "ccy_to": "EUR",
  "fx_rate": 0.543
}'
```

### `DELETE /v1/rates/fx-rate/clear`

Query parameters:

- `ccy_pair` — 6‑letter source/target currency (e.g., `USDEUR`, `EURGBP`) *(required)*

**Response (JSON):**

```json
{
  "code": 200,
  "status": "Fx rate set for USDEUR is cleared"
}
```

**Examples:**

```bash
# Override Fx Rate for USD/EUR with value 0.543
curl -X 'DELETE' \
  'http://127.0.0.1:8000/v1/rates/fx-rate/clear?ccy_pair=USDEUR' \
  -H 'accept: application/json'
```
---

## ⚙️ Configuration

Environment variables (via `.env`):

```
BINANCE_BASE_URL=https://api.binance.com
CACHE_TTL_SECONDS=3600
```
> Default `BINANCE_BASE_URL` and `CACHE_TTL_SECONDS` are provided in code; `.env` overrides are optional.

Currency mapping used internally:

```
USD -> USDT
EUR -> EUR
GBP -> GBP
```
Extend as needed (ensure Binance has a `BTC<QUOTE>` market).

---
## 🛠️ Setup & Run

**Requirements**: Python 3.11+ (tested with 3.12)

```
# Open terminal window -> Navigate to project root folder
# where user can find requirements.txt
pip install -r requirements.txt
uvicorn app.main:app --reload
```
---
## ✅ Run tests
This project uses pytest (with pytest-asyncio) and discovers tests 
recursively under tests/ — nested folders are fine.
```

# Open terminal window -> Navigate to project root folder
# where user can find requirements_dev.txt
pip install -r requirements_dev.txt

# run ALL tests under tests/ (recurses into nested folders)
pytest tests/

# run with coverage
pytest tests/ --cov=app --cov-branch --cov-report=term-missing
```