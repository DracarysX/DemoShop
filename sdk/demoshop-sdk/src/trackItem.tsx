import React, { ComponentType, useEffect, useRef } from 'react';
import { PressableProps, Pressable as RNPressable } from 'react-native';
import { ClickTracker } from './ClickTracker';

export function trackItem(
  product: { name: string; [key: string]: any }
): ComponentType<PressableProps> {
  const trackerRef = useRef<ReturnType<typeof ClickTracker.trackProduct> | null>(null);

  useEffect(() => {
    trackerRef.current = ClickTracker.trackProduct(product);
    return () => {
      trackerRef.current?.cleanup();
    };
  }, [product]);

  return (props: PressableProps) => {
    const { onPress: developerOnPress, ...otherProps } = props;

    const handlePress = async (event: any) => {
      await trackerRef.current?.handlePress();
      if (developerOnPress) {
        developerOnPress(event);
      }
    };

    return <RNPressable {...otherProps} onPress={handlePress} />;
  };
}

