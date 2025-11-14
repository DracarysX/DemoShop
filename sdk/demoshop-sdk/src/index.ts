/**
 * DemoShop SDK - Local Package
 * 
 * A powerful SDK for tracking user behavior, generating dynamic coupons,
 * and optimizing e-commerce revenue.
 * 
 * @packageDocumentation
 */

export { ClickTracker } from './ClickTracker';
export type {
    CouponResponse,
    OfferListener,
    ProductTracker,
    PurchaseData,
    PurchaseItem,
    SDKConfig,
    TrackingEvent
} from './types';
export { useTrackProduct } from './useTrackProduct';

/**
 * SDK Version
 */
export const VERSION = '1.0.0';

/**
 * Initialize the SDK with configuration
 * 
 * @example
 * ```typescript
 * import { initSDK } from '@demoshop/sdk';
 * 
 * initSDK({
 *   serverUrl: 'http://10.0.2.2:8080',
 *   enableLogging: true
 * });
 * ```
 */
export { ClickTracker as initSDK } from './ClickTracker';

