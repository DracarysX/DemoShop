import React, { ComponentType, useEffect, useRef } from 'react';
import { Dimensions, findNodeHandle, PressableProps, Pressable as RNPressable, UIManager } from 'react-native';
import { ClickTracker } from './ClickTracker';

export function trackItem(
  product: { name: string; [key: string]: any }
): ComponentType<PressableProps> {
  const trackerRef = useRef<ReturnType<typeof ClickTracker.trackProduct> | null>(null);
  const pressableRef = useRef<any>(null);

  useEffect(() => {
    trackerRef.current = ClickTracker.trackProduct(product);
    return () => {
      trackerRef.current?.cleanup();
    };
  }, [product]);

  // Track view events every 10 seconds of continuous visibility
  useEffect(() => {
    let visibleTimeMs = 0;
    let lastViewEventMs = 0;
    
    const interval = setInterval(() => {
      if (pressableRef.current) {
        const handle = findNodeHandle(pressableRef.current);
        if (handle) {
          const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
          UIManager.measureInWindow(handle, (x, y, width, height) => {
            const leftX = x;
            const rightX = x + width;
            const topY = y;
            const bottomY = y + height;
            
            // Check if item is visible in viewport (overlaps with screen bounds)
            const isVisibleX = leftX < screenWidth && rightX > 0;
            const isVisibleY = topY < screenHeight && bottomY > 0;
            const isVisible = isVisibleX && isVisibleY;
            
            if (isVisible) {
              visibleTimeMs += 1000; // Add 1 second
              
              if (visibleTimeMs - lastViewEventMs >= 5000) {
                trackerRef.current?.recordView(5000);
                lastViewEventMs = visibleTimeMs;
              }
            } else {
              // Reset when not visible
              visibleTimeMs = 0;
              lastViewEventMs = 0;
            }
          });
        }
      }
    }, 1000); // Check every second

    return () => clearInterval(interval);
  }, [product.name]);

  return (props: PressableProps) => {
    const { onPress: developerOnPress, ...otherProps } = props;

    const handlePress = async (event: any) => {
      await trackerRef.current?.handlePress();
      if (developerOnPress) {
        developerOnPress(event);
      }
    };

    return <RNPressable ref={pressableRef} {...otherProps} onPress={handlePress} />;
  };
}

