import * as Application from 'expo-application';
import { Platform } from 'react-native';

export interface OfferListener {
  onOfferReceived: (productName: string, discount: number, couponId: string) => void;
}

interface CouponResponse {
  couponId: string;
  discount: number;
}

class ClickTrackerService {
  private clickCounts: Map<string, number> = new Map();
  private offerListener: OfferListener | null = null;
  private offeredProducts: Set<string> = new Set();
  private adid: string | null = null;
  private adidPromise: Promise<string>;
  private trackerEnabled: boolean = true; // Tracking flag - can be toggled

  constructor() {
    // Get real advertising ID from device
    this.adidPromise = this.initializeAdId();
  }

  private async initializeAdId(): Promise<string> {
    try {
      if (Platform.OS === 'android') {
        // Get Android Advertising ID
        const androidId = await Application.getAndroidId();
        this.adid = androidId || 'unknown-android-id';
      } else if (Platform.OS === 'ios') {
        // Get iOS Identifier for Vendor (IDFV)
        const iosIdForVendor = await Application.getIosIdForVendorAsync();
        this.adid = iosIdForVendor || 'unknown-ios-id';
      } else {
        // Fallback for web or other platforms
        this.adid = 'web-' + Date.now();
      }
      
      return this.adid;
    } catch (error) {
      console.error('[ClickTracker] Error getting advertising ID:', error);
      this.adid = 'fallback-' + Date.now();
      return this.adid;
    }
  }

  async track(eventName: string, params?: Record<string, string>): Promise<void> {
    // Count clicks for product items
    if (eventName === "click_product_item" && params?.productName) {
      const productName = params.productName;
      const currentCount = this.clickCounts.get(productName) || 0;
      const newCount = currentCount + 1;
      this.clickCounts.set(productName, newCount);

      // Trigger offer after 3 clicks, only once per product
      if (newCount === 3 && !this.offeredProducts.has(productName)) {
        this.offeredProducts.add(productName);
        await this.requestCoupon(productName);
      }
    }
  }

  private async requestCoupon(productName: string): Promise<void> {
    try {
      // Wait for advertising ID to be initialized
      const adid = await this.adidPromise;
            
      // Use 10.0.2.2 for Android emulator, localhost for iOS/web
      const baseUrl = 'http://10.0.2.2:8080';
      
      const response = await fetch(`${baseUrl}/coupon`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          adid: adid,
          productName: productName,
        }),
      });

      if (response.ok) {
        const data: CouponResponse = await response.json();        
        if (this.offerListener) {
          this.offerListener.onOfferReceived(
            productName,
            data.discount,
            data.couponId
          );
        }
      } else {
        console.error(`[ClickTracker] Failed to get coupon: ${response.status}`);
        // Fallback to default discount if server fails
        if (this.offerListener) {
          this.offerListener.onOfferReceived(productName, 0.2, 'fallback');
        }
      }
    } catch (error) {
      console.error('[ClickTracker] Error requesting coupon:', error);
      // Fallback to default discount if request fails
      if (this.offerListener) {
        this.offerListener.onOfferReceived(productName, 0.2, 'fallback');
      }
    }
  }

  setOfferListener(listener: OfferListener): void {
    this.offerListener = listener;
  }

  async getAdId(): Promise<string> {
    return await this.adidPromise;
  }

  reset(): void {
    this.clickCounts.clear();
    this.offeredProducts.clear();
    
    // Notify listener that all discounts have been cleared
    if (this.offerListener) {
      // We could add a method to clear all discounts, but for now
      // the shop screen will handle this via focus effect
    }
  }
  
  hasOfferedProducts(): boolean {
    return this.offeredProducts.size > 0;
  }

  setTrackerEnabled(enabled: boolean): void {
    console.log(`[ClickTracker] Tracker ${enabled ? 'enabled' : 'disabled'}`);
    this.trackerEnabled = enabled;
  }

  isTrackerEnabled(): boolean {
    return this.trackerEnabled;
  }
}

export const ClickTracker = new ClickTrackerService();

