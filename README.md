# DemoShop - React Native E-Commerce App

A modern e-commerce mobile application built with React Native and Expo, featuring a clean shopping interface with dynamic discounts.

## Features

- **Product Catalog**: Browse clothing items with beautiful image cards
- **Shopping Cart**: Add items to cart and manage purchases
- **Dynamic Discounts**: Get 20% off after viewing an item 3 times
- **Discount Notifications**: Toast notifications for special offers
- **Product Details**: View detailed product information in a modal
- **Click Tracking**: Analytics tracking for user interactions

## Tech Stack

- **React Native** - Mobile framework
- **Expo** - Development platform
- **Expo Router** - File-based routing
- **TypeScript** - Type safety
- **Expo Linear Gradient** - UI gradients

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Android Studio (for Android development) or Xcode (for iOS development)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

### Running the App

#### Development Build (Recommended)

Build and run on Android:
```bash
npx expo run:android
```

Build and run on iOS (macOS only):
```bash
npx expo run:ios
```

**Expo Go (Quick testing)**

Start the development server:
```bash
npm start
```

Then scan the QR code with Expo Go app on your device.

**Note**: For Android emulator, use `10.0.2.2:8080` instead of `localhost:8080` to connect to the host machine.

### Building for Production

Using EAS Build:
```bash
# Login to Expo
eas login

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

## Project Structure

```
├── app/
│   ├── (tabs)/
│   │   ├── shop.tsx       # Main product listing screen
│   │   ├── cart.tsx       # Shopping cart screen
│   │   └── _layout.tsx    # Tab navigation layout
│   └── _layout.tsx        # Root layout
├── components/
│   ├── ProductItem.tsx           # Product card component
│   ├── ProductDetailModal.tsx    # Product details modal
│   └── DiscountToast.tsx         # Discount notification
├── services/
│   └── ClickTracker.ts    # Analytics and discount logic
├── types/
│   └── index.ts           # TypeScript types and data
└── constants/
    └── theme.ts           # App theme configuration
```

## How It Works

### Discount System with Server Integration

The app features a smart discount system that integrates with a coupon server:
1. User clicks on a product item to view details (click tracking)
2. After 3 clicks on the same product, the app requests a coupon from the server
3. **Server Request**: `POST http://localhost:8080/coupon`
   - Sends: `{ "adid": "unique-device-id", "productName": "T-Shirt" }`
   - Receives: `{ "couponId": "COUPON-ABC123", "discount": 0.2 }`
4. A toast notification appears showing the discount
5. The discount is applied to that product in both the catalog and cart
6. Coupon ID is tracked for analytics

### Navigation

- **Shop Tab**: Browse all available products
- **Cart Tab**: View and purchase items in your cart
- Products can be added to cart from both the product grid and detail modal

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
