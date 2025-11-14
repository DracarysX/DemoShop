import React, { ComponentType, useEffect, useRef } from 'react';
import { PressableProps, Pressable as RNPressable } from 'react-native';
import { ClickTracker } from './ClickTracker';

/**
 * React hook to automatically track a product
 * Returns a tracked item component that handles ALL interactions automatically
 * 
 * @param product - Product object with at least a 'name' property
 * @returns TrackedItem component with automatic view, click tracking, and coupon handling
 * 
 * @example
 * const TrackedItem = useTrackProduct(item);
 * <TrackedItem style={styles.card}>
 *   <Text>{item.name}</Text>
 * </TrackedItem>
 */
export function useTrackProduct(
  product: { name: string; [key: string]: any }
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

  // Return a tracked component - SDK handles EVERYTHING
  return (props: PressableProps) => {
    const handlePress = async () => {
      // SDK automatically:
      // 1. Tracks the click
      // 2. Requests coupon if needed (3 clicks)
      // 3. Calls global click handler (opens modal, etc.)
      await trackerRef.current?.handlePress();
    };

    return <RNPressable {...props} onPress={handlePress} />;
  };
}

