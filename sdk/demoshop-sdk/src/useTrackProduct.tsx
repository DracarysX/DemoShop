import React, { ComponentType, useEffect, useRef } from 'react';
import { PressableProps, Pressable as RNPressable } from 'react-native';
import { ClickTracker } from './ClickTracker';

/**
 * React hook to automatically track a product
 * SDK acts as middleware - intercepts clicks, tracks them, then calls your handler
 * 
 * @param product - Product object with at least a 'name' property
 * @param onItemClick - Developer's click handler (SDK calls this AFTER tracking)
 * @returns TrackedItem component with automatic view, click tracking, and coupon handling
 * 
 * @example
 * const TrackedItem = useTrackProduct(item, (product) => setDialogItem(product));
 * <TrackedItem style={styles.card}>
 *   <Text>{item.name}</Text>
 * </TrackedItem>
 */
export function useTrackProduct(
  product: { name: string; [key: string]: any },
  onItemClick?: (product: any) => void
): ComponentType<PressableProps> {
  const trackerRef = useRef<ReturnType<typeof ClickTracker.trackProduct> | null>(null);

  useEffect(() => {
    // Initialize tracker for this product (auto-tracks view on mount)
    trackerRef.current = ClickTracker.trackProduct(product);

    // Cleanup on unmount (auto-tracks view end)
    return () => {
      trackerRef.current?.cleanup();
    };
  }, [product]);

  // Return a tracked component - SDK intercepts clicks as middleware
  return (props: PressableProps) => {
    const handlePress = async () => {
      // SDK middleware: Track FIRST
      // 1. Tracks the click count
      // 2. Requests coupon if needed (3 clicks)
      await trackerRef.current?.handlePress();
      
      // THEN call developer's click handler
      if (onItemClick) {
        onItemClick(product);
      }
    };

    return <RNPressable {...props} onPress={handlePress} />;
  };
}

