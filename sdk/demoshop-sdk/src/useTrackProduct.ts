import { useEffect, useRef } from 'react';
import { ClickTracker } from './ClickTracker';

/**
 * React hook to automatically track a product
 * Just call once - SDK handles view tracking, click tracking, and cleanup automatically
 * 
 * @param productName - Name of the product to track
 * @param onPress - Your onPress handler (SDK wraps it with tracking)
 * @returns Object with onPress handler and trackClick for nested interactions
 * 
 * @example
 * const { onPress, trackClick } = useTrackProduct(item.name, onItemClick);
 * <Pressable onPress={onPress}>
 *   <Button onPress={(e) => { e.stopPropagation(); trackClick(); doSomething(); }}>
 * </Pressable>
 */
export function useTrackProduct(
  productName: string,
  onPress?: () => void
): { 
  onPress: () => Promise<void>;
  trackClick: () => Promise<void>;
} {
  const trackerRef = useRef<ReturnType<typeof ClickTracker.trackProduct> | null>(null);

  useEffect(() => {
    // Initialize tracker for this product (auto-tracks view on mount)
    trackerRef.current = ClickTracker.trackProduct(productName);

    // Cleanup on unmount (auto-tracks view end)
    return () => {
      trackerRef.current?.cleanup();
    };
  }, [productName]);

  // Tracking function (for nested interactions like Add to Cart)
  const trackClick = async () => {
    await trackerRef.current?.handlePress();
  };

  // Main onPress that combines tracking + user callback
  const wrappedOnPress = async () => {
    await trackClick();
    onPress?.();
  };

  return { 
    onPress: wrappedOnPress,
    trackClick 
  };
}

