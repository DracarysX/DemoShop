import * as Application from 'expo-application';
import { Platform } from 'react-native';
import { AnalyticsEvent, CouponResponse, OfferListener, PurchaseData, SDKConfig } from './types';

class ClickTrackerService {
  private clickCounts: Map<string, number> = new Map();
  private offerListener: OfferListener | null = null;
  private requestedCoupons: Set<string> = new Set();
  private adid: string | null = null;
  private adidPromise: Promise<string>;
  private trackerEnabled: boolean = true;
  private config: SDKConfig = {
    serverUrl: 'http://10.0.2.2:8080',
    enableLogging: false
  };
  
  private analyticsQueue: AnalyticsEvent[] = [];
  private batchInterval: number | null = null;

  constructor() {
    this.adidPromise = this.initializeAdId();
    this.startBatchSender();
  }

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

  trackProduct(product: any): {
    handlePress: () => Promise<void>;
    cleanup: () => void;
    recordView: (viewDuration: number) => void;
  } {
    const productId = product.id;
    const productName = product.name;
    
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Tracking: ${productId} - ${productName}`);
    }

    const handlePress = async () => {
      const currentCount = this.clickCounts.get(productName) || 0;
      const newCount = currentCount + 1;
      this.clickCounts.set(productName, newCount);

      this.recordEvent({
        eventType: 'click',
        productId,
        productName,
        timestamp: Date.now(),
      });

      if (this.config.enableLogging) {
        console.log(`[DemoShop SDK] ${productId} - ${productName} clicked (${newCount})`);
      }

      if (newCount === 3 && !this.requestedCoupons.has(productName)) {
        this.requestedCoupons.add(productName);
        await this.requestCoupon(productName);
      }
    };

    const recordView = (viewDuration: number) => {
      this.recordEvent({
        eventType: 'view',
        productId,
        productName,
        timestamp: Date.now(),
        viewDuration,
      });
    };

    const cleanup = () => {
      if (this.config.enableLogging) {
        console.log(`[DemoShop SDK] Cleanup: ${productId} - ${productName}`);
      }
    };

    return { handlePress, cleanup, recordView };
  }

  async track(eventName: string, params?: Record<string, string>): Promise<void> {
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Event: ${eventName}`, params);
    }
  }
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

  setOfferListener(listener: OfferListener): void {
    this.offerListener = listener;
  }

  async getAdId(): Promise<string> {
    return await this.adidPromise;
  }

  reset(): void {
    this.clickCounts.clear();
    this.requestedCoupons.clear();
    if (this.config.enableLogging) {
      console.log('[DemoShop SDK] Reset');
    }
  }

  setTrackerEnabled(enabled: boolean): void {
    this.trackerEnabled = enabled;
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Tracker ${enabled ? 'ON' : 'OFF'}`);
    }
  }

  isTrackerEnabled(): boolean {
    return this.trackerEnabled;
  }

  public recordEvent(event: AnalyticsEvent): void {
    this.analyticsQueue.push(event);
    if (this.config.enableLogging) {
      console.log(`[DemoShop SDK] Event recorded:`, event);
    }
  }

  private startBatchSender(): void {
    this.batchInterval = setInterval(async () => {
      if (this.analyticsQueue.length > 0) {
        await this.sendAnalyticsBatch();
      }
    }, 5000);
  }

  private async sendAnalyticsBatch(): Promise<void> {
    if (this.analyticsQueue.length === 0) return;

    const adid = await this.adidPromise;
    const eventsToSend = [...this.analyticsQueue];
    this.analyticsQueue = [];

    try {
      const response = await fetch(`${this.config.serverUrl}/analytics-events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          adid,
          events: eventsToSend,
        }),
      });

      if (!response.ok) {
        console.error(`[DemoShop SDK] Failed to send analytics: ${response.status}`);
        this.analyticsQueue.push(...eventsToSend);
      }
    } catch (error) {
      console.error('[DemoShop SDK] Error sending analytics:', error);
      this.analyticsQueue.push(...eventsToSend);
    }
  }

  stopBatchSender(): void {
    if (this.batchInterval !== null) {
      clearInterval(this.batchInterval);
      this.batchInterval = null;
    }
  }
}

export const ClickTracker = new ClickTrackerService();

