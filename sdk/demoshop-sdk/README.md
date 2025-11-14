# DemoShop SDK

A powerful React Native SDK for tracking user behavior, generating dynamic coupons, and optimizing e-commerce revenue.

## Features

- 🎯 **Behavioral Tracking**: Track user interactions and clicks
- 🎟️ **Dynamic Coupons**: Server-generated discount codes based on behavior
- 📱 **Cross-Platform**: Works on iOS, Android, and Web
- 🔐 **ADID Support**: Real device advertising ID tracking
- 📊 **Analytics Ready**: Full purchase and conversion tracking
- ⚡ **Lightweight**: Minimal dependencies

## Installation (Local)

This SDK is installed locally in your project:

```json
{
  "dependencies": {
    "@demoshop/sdk": "file:./sdk/demoshop-sdk"
  }
}
```

## Quick Start

```typescript
import { ClickTracker } from '@demoshop/sdk';

// Configure the SDK
ClickTracker.configure({
  serverUrl: 'http://10.0.2.2:8080',
  enableLogging: true
});

// Set up offer listener
ClickTracker.setOfferListener({
  onOfferReceived: (productName, discount, couponId) => {
    console.log(`Got ${discount * 100}% off ${productName}!`);
  }
});

// Track events
ClickTracker.track('click_product_item', { productName: 'T-Shirt' });

// Get device ADID
const adid = await ClickTracker.getAdId();

// Check tracker status
const isEnabled = ClickTracker.isTrackerEnabled();

// Reset tracking
ClickTracker.reset();
```

## API Reference

### `configure(config: SDKConfig)`
Configure the SDK with custom settings.

**Parameters:**
- `serverUrl` (string): Backend server URL
- `enableLogging` (boolean, optional): Enable debug logs

### `track(eventName: string, params?: Record<string, string>)`
Track user events.

**Parameters:**
- `eventName`: Name of the event (e.g., 'click_product_item')
- `params`: Optional event parameters

### `setOfferListener(listener: OfferListener)`
Set callback for when coupons are generated.

**Parameters:**
- `listener.onOfferReceived`: Callback function with (productName, discount, couponId)

### `getAdId(): Promise<string>`
Get the device advertising ID.

**Returns:** Promise resolving to ADID string

### `setTrackerEnabled(enabled: boolean)`
Enable or disable tracking.

### `isTrackerEnabled(): boolean`
Check if tracking is enabled.

### `reset()`
Clear all tracking data and active offers.

### `hasOfferedProducts(): boolean`
Check if there are active offers.

## Server Integration

The SDK communicates with a FastAPI backend:

**POST `/coupon`**
```json
{
  "adid": "device-id",
  "productName": "T-Shirt"
}
```

**Response:**
```json
{
  "couponId": "COUPON-123",
  "discount": 0.2
}
```

## Architecture

```
User Action → SDK Track() → Server Decision → Coupon Generated → Callback
                                ↓
                         Analytics Recorded
```

## Why This SDK?

Unlike platforms like Dynamic Yield that only do product recommendations, this SDK provides:
- ✅ Dynamic discount generation
- ✅ Behavioral coupon triggers
- ✅ Full purchase attribution
- ✅ Revenue optimization analytics

## License

MIT

