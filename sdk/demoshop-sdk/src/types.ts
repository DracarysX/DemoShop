/**
 * DemoShop SDK Types
 */

export interface OfferListener {
  onOfferReceived: (productName: string, discount: number, couponId: string) => void;
}

export interface CouponResponse {
  couponId: string;
  discount: number;
}

export interface SDKConfig {
  serverUrl: string;
  enableLogging?: boolean;
}

export interface TrackingEvent {
  eventName: string;
  params?: Record<string, string>;
}

export interface ProductTracker {
  trackClick: () => void;
  trackView: () => void;
  detach: () => void;
}

export interface PurchaseItem {
  id: string;
  name: string;
  price: number;
  discount: number;
  finalPrice: number;
}

export interface PurchaseData {
  items: PurchaseItem[];
  total: number;
  trackerEnabled?: boolean;
}

export interface AnalyticsEvent {
  eventType: 'click' | 'view';
  productId: string;
  productName: string;
  timestamp: number;
  viewDuration?: number;
}

export interface AnalyticsBatch {
  adid: string;
  events: AnalyticsEvent[];
}

