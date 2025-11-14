# DemoShop Coupon Server

FastAPI server for handling coupon requests from the DemoShop mobile app.

## Setup

1. Create and activate virtual environment:
```bash
# Create venv (already created)
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
# Make sure venv is activated first
source venv/bin/activate

# Run the server
uvicorn main:app --reload --port 8080
```

Or:
```bash
python main.py
```

The server will start on `http://localhost:8080`

To deactivate the virtual environment:
```bash
deactivate
```

## API Endpoints

### POST /coupon
Request a discount coupon for a product.

**Request:**
```json
{
  "adid": "real-device-advertising-id",
  "productName": "T-Shirt"
}
```

**Response:**
```json
{
  "couponId": "COUPON-1731234567-ABC123",
  "discount": 0.2
}
```

### POST /purchase
Record a purchase transaction.

**Request:**
```json
{
  "adid": "real-device-advertising-id",
  "items": [
    {
      "name": "T-Shirt",
      "price": 19.99,
      "discount": 0.2,
      "finalPrice": 15.99
    }
  ],
  "total": 15.99,
  "trackerEnabled": true
}
```

**Parameters:**
- `adid` (string): Device advertising ID
- `items` (array): List of purchased items with discount information
- `total` (float): Total purchase amount
- `trackerEnabled` (boolean, optional): Whether the tracker was enabled during purchase (default: true)

**Response:**
```json
{
  "success": true,
  "purchaseId": "PURCHASE-1731234567-1234",
  "timestamp": "2024-11-14T10:30:00"
}
```

### GET /analytics
View the analytics dashboard in your browser.

**Features:**
- 📊 Summary stats (total customers, purchases, revenue, discounts)
- 🎯 Tracker analytics:
  - Percentage of ADIDs with tracker enabled
  - Revenue comparison: Tracker ON vs OFF
  - Count of ADIDs by tracker status
- 📈 ADID Revenue Table:
  - Advertising ID
  - Tracker status (🟢 ON / 🔴 OFF)
  - Number of purchases
  - Items purchased
  - Revenue generated
  - Discounts used
  - Net revenue
- 📦 Product Performance Table:
  - Product name
  - Quantity, revenue, and savings split by tracker ON/OFF
  - Total revenue per product
  - Grand totals row
- 🔄 Auto-refreshes every 10 seconds
- 💰 Beautiful, responsive design with gradient styling

**URL:** http://localhost:8080/analytics

### GET /coupons
Get all issued coupons (for debugging).

### GET /health
Health check endpoint.

## Tracker Flag

The tracker flag indicates whether click tracking is enabled in the app. By default, it's set to `true`.

### Controlling the Tracker (in app code)

```typescript
import { ClickTracker } from '@/services/ClickTracker';

// Enable tracker (default)
ClickTracker.setTrackerEnabled(true);

// Disable tracker
ClickTracker.setTrackerEnabled(false);

// Check current status
const isEnabled = ClickTracker.isTrackerEnabled();
```

When a purchase is made, the current tracker status is automatically sent to the server and used in analytics to compare performance between tracked and untracked sessions.

## Testing

```bash
curl -X POST http://localhost:8080/coupon \
  -H "Content-Type: application/json" \
  -d '{"adid":"test-adid-123","productName":"T-Shirt"}'
```

## Interactive API Docs

Once the server is running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

