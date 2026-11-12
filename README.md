# TradeBot 1.0 — Automated NSE Nifty Options Trading Bot

An institutional-grade, rule-based algorithmic trading platform engineered for NSE Nifty index options with dynamic parallel CE/PE condition tracking, dynamic exchange-side trailing stop-loss, a high-performance **React 19 + Vite** frontend, and **Angel One SmartAPI** as the primary broker.

---

## 1. High-Performance React 19 Frontend Architecture

The frontend is a dedicated, ultra-responsive Single Page Application (SPA) built with:
- **Core**: React 19 + TypeScript + Vite 8
- **Styling**: Tailwind CSS + Lucide Icons
- **Charting**: Recharts (Cumulative Equity Growth Area Chart)
- **Networking**: Real-Time Native WebSocket (`/ws`) with automatic reconnect + fallback polling
- **Zero-Latency Navigation**: Sub-millisecond tab switching between:
  1. **⚡ Live Cockpit**: State machine pill, Spot LTP, Bias with rationale, Position card with live Unrealized P&L, Dynamic Trailing SL card, and the Parallel CE/PE Condition Matrix with real-time tick counters and trigger winner badges.
  2. **📋 Orders & Positions**: Live order book with Angel One order IDs, Limit/SL-L types, execution fills, closed trades, charges, and gross/net P&L.
  3. **⚙️ Daily Parameters (07:30–08:00 AM IST)**: Parameter form for Spot reference level, CE average, PE average, lots, stop-loss points, and target points. Includes countdown indicator and dev override.
  4. **📊 Performance Reports**: Win Rate %, Profit Factor, Net P&L, Max Drawdown cards, Recharts interactive equity curve, and instant CSV trade history export.
  5. **📜 Decision Journal & Audit Log**: Chronological ledger of every single bot evaluation, tick arrival, condition qualification, order placement, and dynamic trailing SL ratchet.

### Real-Time Controls
- **🛑 Emergency Kill Switch**: Prompts modal confirmation, instantly cancels pending orders, and squares off open positions on Angel One.
- **⏸️ Pause / ▶️ Resume Bot**: Halts or resumes condition evaluation in real time.
- **⚡ Manual Square Off**: Immediately exits the active position at market price.

---

## 2. Supported Brokers

| Broker | Adapter Class | Status | Auth Mechanism |
|---|---|---|---|
| **Angel One (SmartAPI)** | `AngelOneBrokerAdapter` | **Active / Default** | Headless TOTP (Base32 secret) + MPIN/Password session generation |
| **Zerodha (Kite Connect)**| `KiteBrokerAdapter` | Available | Headless TOTP login / manual session |
| **Paper Engine** | `PaperBrokerAdapter` | Built-in Default | Realistic fill simulator with slippage & exchange charges |

---

## 3. How to Run the System

### Option A: Complete All-in-One Production Mode (FastAPI serves React SPA)
1. Start the backend:
   ```powershell
   D:\tradebot_venv\Scripts\python.exe src/main.py
   ```
2. Open your browser:
   ```text
   http://localhost:8000
   ```
   The compiled React frontend is served directly with sub-millisecond WebSocket updates.

### Option B: Frontend Hot-Reload Development Mode (Vite)
If you wish to modify the React frontend with instant Hot-Module-Reloading:
1. In terminal 1, start the Python backend:
   ```powershell
   D:\tradebot_venv\Scripts\python.exe src/main.py
   ```
2. In terminal 2, start the Vite dev server:
   ```powershell
   cd frontend
   pnpm dev
   ```
3. Open `http://localhost:5173`. Vite automatically proxies `/api` and `/ws` to port 8000.

---

## 4. Angel One SmartAPI Setup

### Step 1: Create an Angel One SmartAPI App
1. Go to [https://smartapi.angelbroking.com/](https://smartapi.angelbroking.com/) and register or log in.
2. Click **Create an App** and copy your **API Key**.

### Step 2: Enable TOTP on Angel One
1. Go to [https://smartapi.angelbroking.com/enable-totp](https://smartapi.angelbroking.com/enable-totp).
2. Enter your Client ID and Password/MPIN, then verify the OTP.
3. Copy the **text Secret Key (Base32 string)** shown below the QR code.

### Step 3: Configure `.env`
```bash
TRADE_MODE=PAPER                     # Set to LIVE when ready
BROKER_TYPE=ANGELONE                 # ANGELONE | KITE | PAPER

ANGELONE_API_KEY=your_smartapi_api_key
ANGELONE_CLIENT_ID=your_angel_one_client_id
ANGELONE_PASSWORD=your_password_or_mpin
ANGELONE_TOTP_SECRET=your_base32_totp_secret

TIMEZONE=Asia/Kolkata
DATABASE_URL=sqlite+aiosqlite:///data/tradebot.db
API_SECRET_KEY=tradebot_dev_secret_key_1234567890
```

---

## 5. Automated Verification

All 17 unit tests run in under 1 second:

```powershell
D:\tradebot_venv\Scripts\pytest.exe -v -p no:asyncio -p no:anyio tests/unit/
```

Verified test coverage includes:
- Angel One TOTP generation & order type mappings (`test_angelone_adapter.py`)
- Market bias detection (`test_bias.py`)
- 2-tick confirmation filter and opposite setup skipping (`test_conditions.py`)
- Atomic single-winner race arbiter & window sealing (`test_race_arbiter.py`)
- Dynamic trailing stop-loss ratcheting (`test_risk.py`)
- ATM strike calculation & weekly contract resolution (`test_strike_resolver.py`)
- Finite state machine lifecycle transitions (`test_fsm.py`)
- Time boundaries with simulated clock (`test_window.py`)
