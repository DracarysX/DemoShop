# Analytics Dashboard - New Features

## Overview
The analytics dashboard now provides comprehensive insights into purchases, revenue, and tracker performance with advanced projections.

## New Features Implemented

### 1. Tracker Flag System
- **Client-side tracking flag** that can be toggled on/off
- Default state: `ON` (enabled)
- Automatically sent with every purchase to the server

**Usage:**
```typescript
import { ClickTracker } from '@/services/ClickTracker';

// Enable/disable tracker
ClickTracker.setTrackerEnabled(true);  // or false

// Check status
const isEnabled = ClickTracker.isTrackerEnabled();
```

### 2. Purchases Split by Coupon Usage
The dashboard now distinguishes between:
- **Purchases WITH coupons** (discount > 0)
- **Purchases WITHOUT coupons** (discount = 0)

**Stats Displayed:**
- Count of purchases with/without coupons
- Revenue from purchases with/without coupons

### 3. Enhanced ADID Table
Now shows per advertising ID:
- Tracker status (🟢 ON / 🔴 OFF)
- Total purchases
- Revenue WITH coupons
- Revenue WITHOUT coupons
- Total revenue
- Total savings

### 4. Advanced Product Performance Table
Three-level breakdown per product:
- **Tracker ON + WITH Coupon**: Qty, Revenue, Savings
- **Tracker ON + WITHOUT Coupon**: Qty, Revenue
- **Tracker OFF (all purchases)**: Qty, Revenue, Savings
- **Total Revenue** per product

### 5. 100% Tracker Adoption Projection
New highlight section showing:
- **Current Revenue**: Total revenue from all purchases
- **Projected Revenue**: What revenue would be if 100% of users had tracker enabled
- **Additional Revenue**: How much more money would be made ($)
- **Percentage Increase**: Growth percentage (%)

**Calculation Method:**
1. Calculate average revenue per ADID with tracker ON
2. Project this average across ALL unique ADIDs
3. Compare with current total to show potential gains

### 6. Tracker Statistics
Summary metrics:
- Percentage of ADIDs with tracker enabled
- Count breakdown: Tracker ON vs OFF
- Revenue comparison: Tracker ON vs OFF

## Dashboard Layout

```
📊 DemoShop Analytics
├── 📈 Basic Stats (4 cards)
│   ├── Total Customers
│   ├── Total Purchases
│   ├── Total Revenue
│   └── Total Discounts Given
│
├── 🎯 Coupon Usage Stats (4 cards)
│   ├── Purchases WITH Coupons
│   ├── Revenue WITH Coupons
│   ├── Purchases WITHOUT Coupons
│   └── Revenue WITHOUT Coupons
│
├── 🔍 Tracker Stats (4 cards)
│   ├── ADIDs with Tracker ON (%)
│   ├── Tracker ON / OFF Count
│   ├── Revenue (Tracker ON)
│   └── Revenue (Tracker OFF)
│
├── 💰 100% Tracker Adoption Projection (highlight box)
│   ├── Current Revenue
│   ├── Projected Revenue (if 100% had tracker)
│   ├── Additional Revenue ($)
│   └── Percentage Increase (%)
│
├── 📊 Revenue by ADID Table
│   └── Shows revenue split by coupon usage per ADID
│
└── 📦 Product Performance Table
    └── Shows product sales with 3-way split:
        - Tracker ON (with coupon)
        - Tracker ON (without coupon)
        - Tracker OFF (all)
```

## Key Insights

The dashboard now answers:
1. **How many purchases use coupons?** (With/without coupon metrics)
2. **What's the tracker adoption rate?** (Percentage + counts)
3. **How does tracker affect revenue?** (Tracker ON vs OFF comparison)
4. **What's the revenue potential?** (100% adoption projection)
5. **Which products benefit most from coupons?** (Product table breakdown)

## Data Processing

### Purchase Recording
All purchases are now tracked with:
- ADID (advertising ID)
- Items with discount information
- Total amount
- **Tracker flag** (new!)

### Analytics Calculation
- Processes ALL purchases (with or without coupons)
- Calculates separate metrics for:
  - Items bought with coupons (discount > 0)
  - Items bought without coupons (discount = 0)
- Groups by tracker status (ON/OFF)
- Projects revenue based on tracker ON performance

## Auto-Refresh
Dashboard automatically refreshes every 10 seconds to show real-time data.

## Color Coding
- 🟢 **Green** = Tracker ON
- 🔴 **Red** = Tracker OFF
- **Pink gradients** = Coupon-related metrics
- **Blue gradients** = Tracker ON metrics
- **Green gradients** = Tracker OFF metrics
- **Gold border** = Projection highlight

## Access
Visit: `http://localhost:8080/analytics`

