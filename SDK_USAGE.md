# DemoShop SDK - Local Installation Guide

## ✅ What You've Created

You now have a **local React Native SDK** that can be imported into your app without publishing to npm!

## 📁 Project Structure

```
DemoShopExpo/
├── sdk/
│   └── demoshop-sdk/          # Your SDK package
│       ├── src/
│       │   ├── index.ts       # Main export
│       │   ├── ClickTracker.ts # Tracker service
│       │   └── types.ts       # TypeScript types
│       ├── package.json
│       └── README.md
├── app/                        # Your React Native app
│   └── (tabs)/
│       ├── index.tsx          # Now imports from @demoshop/sdk
│       └── cart.tsx           # Now imports from @demoshop/sdk
└── package.json               # Links to local SDK
```

## 🚀 How It Works

### 1. Local Package Reference
Your `package.json` now includes:
```json
{
  "dependencies": {
    "@demoshop/sdk": "file:./sdk/demoshop-sdk"
  }
}
```

This tells npm to use the local SDK folder instead of downloading from npm.

### 2. Import in Your App
```typescript
// Old way (before SDK)
import { ClickTracker } from "@/services/ClickTracker";

// New way (with SDK)
import { ClickTracker } from "@demoshop/sdk";
```

### 3. Auto-completion Works!
TypeScript knows about your SDK types, so you get full IntelliSense.

## 📦 SDK Features

### Initialize & Configure
```typescript
import { ClickTracker } from '@demoshop/sdk';

// Optional: Configure the SDK
ClickTracker.configure({
  serverUrl: 'http://10.0.2.2:8080',
  enableLogging: true  // See debug logs
});
```

### Track Events
```typescript
// Track product clicks
ClickTracker.track('click_product_item', { 
  productName: 'T-Shirt' 
});

// Track custom events
ClickTracker.track('custom_event', { 
  key: 'value' 
});
```

### Listen for Offers
```typescript
ClickTracker.setOfferListener({
  onOfferReceived: (productName, discount, couponId) => {
    console.log(`🎉 ${discount * 100}% off ${productName}!`);
    console.log(`Coupon: ${couponId}`);
  }
});
```

### Get Device ID
```typescript
const adid = await ClickTracker.getAdId();
console.log('Device ADID:', adid);
```

### Control Tracking
```typescript
// Disable tracking
ClickTracker.setTrackerEnabled(false);

// Check status
const isEnabled = ClickTracker.isTrackerEnabled();

// Reset all data
ClickTracker.reset();

// Check for active offers
const hasOffers = ClickTracker.hasOfferedProducts();
```

## 🔧 Modifying the SDK

Since the SDK is local, you can modify it anytime:

1. **Edit SDK files** in `sdk/demoshop-sdk/src/`
2. **Changes apply immediately** (no need to reinstall)
3. **Add new features** as needed

### Example: Add New Method
```typescript
// sdk/demoshop-sdk/src/ClickTracker.ts

/**
 * Get click count for a product
 */
getClickCount(productName: string): number {
  return this.clickCounts.get(productName) || 0;
}
```

Then use it:
```typescript
import { ClickTracker } from '@demoshop/sdk';

const clicks = ClickTracker.getClickCount('T-Shirt');
```

## 🔄 Updating After Changes

After modifying SDK files:
```bash
# No reinstall needed for code changes
# Just reload your app (Cmd+R in Metro)

# Only reinstall if you change package.json
npm install
```

## 📤 Future: Publishing to npm

When ready to publish:

1. **Create npm account**
2. **Update package.json** in `sdk/demoshop-sdk/`:
   ```json
   {
     "name": "@yourusername/demoshop-sdk",
     "version": "1.0.0"
   }
   ```
3. **Build (if using TypeScript compilation)**:
   ```bash
   cd sdk/demoshop-sdk
   npm run build
   ```
4. **Publish**:
   ```bash
   npm publish --access public
   ```
5. **Update main app**:
   ```json
   {
     "dependencies": {
       "@yourusername/demoshop-sdk": "^1.0.0"
     }
   }
   ```

## 🎯 Advantages of Local SDK

✅ **No publishing needed** - Develop and test locally  
✅ **Instant updates** - Changes apply immediately  
✅ **Version control** - SDK is part of your repo  
✅ **Easy debugging** - Full source access  
✅ **Type safety** - Full TypeScript support  
✅ **Reusable** - Can share across multiple apps  

## 🔗 Using in Multiple Apps

To use this SDK in another app:

1. **Copy the SDK folder**:
   ```bash
   cp -r DemoShopExpo/sdk/demoshop-sdk OtherApp/sdk/
   ```

2. **Add to other app's package.json**:
   ```json
   {
     "dependencies": {
       "@demoshop/sdk": "file:./sdk/demoshop-sdk"
     }
   }
   ```

3. **Install**:
   ```bash
   cd OtherApp
   npm install
   ```

## 🧪 Testing the SDK

Test your SDK integration:

```typescript
import { ClickTracker } from '@demoshop/sdk';

// Test configuration
ClickTracker.configure({
  serverUrl: 'http://10.0.2.2:8080',
  enableLogging: true
});

// Test tracking
console.log('Testing SDK...');
await ClickTracker.track('test_event', { test: 'value' });

// Test ADID
const adid = await ClickTracker.getAdId();
console.log('ADID:', adid);

// Test toggle
ClickTracker.setTrackerEnabled(false);
console.log('Enabled:', ClickTracker.isTrackerEnabled());
```

## 📚 Next Steps

- ✅ SDK is installed and working
- ✅ Your app imports from `@demoshop/sdk`
- ✅ Full TypeScript support enabled
- 🎯 Add more SDK features as needed
- 🚀 Optionally publish to npm later

## 🆚 Your SDK vs Dynamic Yield

Your SDK now has:
- ✅ Better discount management
- ✅ Real-time coupon generation
- ✅ Full purchase attribution
- ✅ Revenue optimization
- ✅ Local development
- ✅ Easy customization

You've built something more powerful! 💪

