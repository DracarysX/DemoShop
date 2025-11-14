import * as Application from 'expo-application';
import { Platform } from 'react-native';
import { CouponResponse, OfferListener, PurchaseData, SDKConfig } from './types';

class ClickTrackerService {
  private clickCounts: Map<string, number> = new Map();
  private offerListener: OfferListener | null = null;
  private requestedCoupons: Set<string> = new Set(); // Track which products already had coupon requested (prevent duplicate requests)
  private adid: string | null = null;
  private adidPromise: Promise<string>;
  private trackerEnabled: boolean = true;
  private productClickHandler: ((product: any) => void) | null = null; // Global click handler - receives full product object
  private config: SDKConfig = {
    serverUrl: 'http://10.0.2.2:8080',
    enableLogging: false
  };

  constructor() {
    this.adidPromise = this.initializeAdId();
  }

  /**
   * Configure the SDK
   * @param config - SDK configuration
   */
  configure(config: Partial<SDKConfig>): void {
    this.config = { ...this.config, ...config };
    if (this.config.enableLogging) {
      console.log('[DemoShop SDK] Configured with:', this.config);
    }
  }

  private async initializeAdId(): Promise<string> {
    try {
      if (Platform.OS === 'android') {
        const androidId = await Application.getAndroidId();
        this.adid = androidId || 'unknown-android-id';
      } else if (Platform.OS === 'ios') {
        const iosIdForVendor = await Application.getIosIdForVendorAsync();
        this.adid = iosIdForVendor || 'unknown-ios-id';
      } else {
        this.adid = 'web-' + Date.now();
      }
      
      if (this.config.enableLogging) {
        console.log('[DemoShop SDK] Initialized with ADID:', this.adid);
      }
      
      return this.adid;
    } catch (error) {
      console.error('[DemoShop SDK] Error getting advertising ID:', error);
      this.adid = 'fallback-' + Date.now();
      return this.adid;
    }
  }

  /**
   * Track a product automatically (view on mount, click handler, cleanup on unmount)
   * This is the simplest way to track a product - just call once
   * @param product - Full product object (must have a 'name' property)
   * @returns Object with handlePress function and cleanup
   * 
   * @example
   * const { handlePress } = ClickTracker.trackProduct(item);
   */
  trackProduct(product: any): {
    handlePress: () => Promise<void>;
    cleanup: () => void;
  } {
    const productName = product.name;
    
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Tracking product: ${productName}`);
    }

    // Automatically track view when product is attached
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] ${productName} viewed`);
    }

    // Create press handler that tracks AND calls global click handler
    const handlePress = async () => {
      const currentCount = this.clickCounts.get(productName) || 0;
      const newCount = currentCount + 1;
      this.clickCounts.set(productName, newCount);

      if (this.config.enableLogging) {
        console.log(`[DemoShop SDK] ${productName} clicked (${newCount} times)`);
      }

      // Request coupon at 3 clicks, but only once per product
      if (newCount === 3 && !this.requestedCoupons.has(productName)) {
        this.requestedCoupons.add(productName);
        await this.requestCoupon(productName);
      }

      // Call global click handler with FULL product object (not just name)
      if (this.productClickHandler) {
        this.productClickHandler(product);
      }
    };

    // Cleanup function
    const cleanup = () => {
      if (this.config.enableLogging) {
        console.log(`[DemoShop SDK] Stopped tracking: ${productName}`);
      }
      // Cleanup logic if needed
    };

    return { handlePress, cleanup };
  }

  /**
   * Track generic events (legacy support)
   * @param eventName - Name of the event
   * @param params - Optional event parameters
   */
  async track(eventName: string, params?: Record<string, string>): Promise<void> {
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Track event: ${eventName}`, params);
    }
    // Generic event tracking (for analytics, logging, etc.)
  }

  /**
   * Track a purchase and send to server
   * @param purchaseData - Purchase details (items, total)
   * @returns Promise<boolean> - True if successfully sent to server
   */
  async trackPurchase(purchaseData: PurchaseData): Promise<boolean> {
    try {
      const adid = await this.adidPromise;
      
      const payload = {
        adid: adid,
        items: purchaseData.items,
        total: purchaseData.total,
        trackerEnabled: purchaseData.trackerEnabled ?? this.trackerEnabled,
      };

      if (this.config.enableLogging) {
        console.log('[DemoShop SDK] Tracking purchase:', payload);
      }

      const response = await fetch(`${this.config.serverUrl}/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (this.config.enableLogging) {
          console.log('[DemoShop SDK] Purchase recorded:', data);
        }
        
        return true;
      } else {
        console.error(`[DemoShop SDK] Failed to record purchase: ${response.status}`);
        return false;
      }
    } catch (error) {
      console.error('[DemoShop SDK] Error tracking purchase:', error);
      return false;
    }
  }

  private async requestCoupon(productName: string): Promise<void> {
    try {
      const adid = await this.adidPromise;
      
      const response = await fetch(`${this.config.serverUrl}/coupon`, {
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
        
        if (this.config.enableLogging) {
          console.log('[DemoShop SDK] Coupon received:', data);
        }
        
        if (this.offerListener) {
          this.offerListener.onOfferReceived(
            productName,
            data.discount,
            data.couponId
          );
        }
      } else {
        console.error(`[DemoShop SDK] Failed to get coupon: ${response.status}`);
        if (this.offerListener) {
          this.offerListener.onOfferReceived(productName, 0.2, 'fallback');
        }
      }
    } catch (error) {
      console.error('[DemoShop SDK] Error requesting coupon:', error);
      if (this.offerListener) {
        this.offerListener.onOfferReceived(productName, 0.2, 'fallback');
      }
    }
  }

  /**
   * Set offer listener callback
   * @param listener - Callback for when offers are received
   */
  setOfferListener(listener: OfferListener): void {
    this.offerListener = listener;
  }

  /**
   * Set global product click handler - called whenever ANY product is clicked
   * Receives the FULL product object, not just the name
   * @param handler - Callback function receiving the complete product object
   * 
   * @example
   * ClickTracker.setProductClickHandler(setDialogItem);
   */
  setProductClickHandler(handler: (product: any) => void): void {
    this.productClickHandler = handler;
    if (this.config.enableLogging) {
      console.log('[DemoShop SDK] Product click handler registered');
    }
  }

  /**
   * Get the device advertising ID
   * @returns Promise resolving to ADID
   */
  async getAdId(): Promise<string> {
    return await this.adidPromise;
  }

  /**
   * Reset all tracking data (click counts and coupon request history)
   * Note: This does NOT clear discount state in the UI - that's managed by the UI layer
   */
  reset(): void {
    this.clickCounts.clear();
    this.requestedCoupons.clear();
    
    if (this.config.enableLogging) {
      console.log('[DemoShop SDK] Reset all tracking data');
    }
  }

  /**
   * Enable or disable tracking
   * @param enabled - Whether tracking should be enabled
   */
  setTrackerEnabled(enabled: boolean): void {
    this.trackerEnabled = enabled;
    
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Tracker ${enabled ? 'enabled' : 'disabled'}`);
    }
  }

  /**
   * Check if tracking is enabled
   * @returns True if tracking is enabled
   */
  isTrackerEnabled(): boolean {
    return this.trackerEnabled;
  }
}

export const ClickTracker = new ClickTrackerService();

