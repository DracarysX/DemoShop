import { DiscountToast } from "@/components/DiscountToast";
import { ProductDetailModal } from "@/components/ProductDetailModal";
import { ProductItem } from "@/components/ProductItem";
import { ClothingItem, clothingItems } from "@/types";
import { ClickTracker, OfferListener } from "@demoshop/sdk";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import React, { useEffect, useState } from "react";
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function ShopScreen() {
  const [cart, setCart] = useState<ClothingItem[]>([]);
  const [discountedItems, setDiscountedItems] = useState<Set<string>>(
    new Set()
  );
  const [toastItem, setToastItem] = useState<ClothingItem | null>(null);
  const [dialogItem, setDialogItem] = useState<ClothingItem | null>(null);

  useEffect(() => {
    // Set up SDK offer listener (only once on mount)
    const offerListener: OfferListener = {
      onOfferReceived: (productName: string, discount: number, couponId: string) => {
        console.log(`[Shop] Received offer for ${productName}: ${discount * 100}% off (Coupon: ${couponId})`);
        setDiscountedItems((prev) => new Set(prev).add(productName));
        const item = clothingItems.find((item) => item.name === productName);
        if (item) {
          setToastItem(item);
        }
      },
    };
    ClickTracker.setOfferListener(offerListener);

    return () => {
      ClickTracker.setOfferListener({
        onOfferReceived: () => {},
      });
    };
  }, []);

  const handleAddToCart = (item: ClothingItem) => {
    setCart((prev) => [...prev, item]);
  };

  const renderItem = ({ item }: { item: ClothingItem }) => (
    <ProductItem
      item={item}
      onAddToCart={handleAddToCart}
      onItemClick={(item) => setDialogItem(item)}
      isDiscounted={discountedItems.has(item.name)}
    />
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>DemoShop</Text>
        <TouchableOpacity
          style={styles.cartButton}
          onPress={() => {
            router.push({
              pathname: "/(tabs)/cart",
              params: {
                cart: JSON.stringify(cart),
                discountedItems: JSON.stringify(Array.from(discountedItems)),
              },
            });
          }}
        >
          <Ionicons name="cart" size={28} color="#007AFF" />
          {cart.length > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{cart.length}</Text>
            </View>
          )}
        </TouchableOpacity>
      </View>

      <FlatList
        data={clothingItems}
        renderItem={renderItem}
        keyExtractor={(item, index) => `${item.name}-${index}`}
        contentContainerStyle={styles.list}
      />

      {toastItem && (
        <DiscountToast
          item={toastItem}
          onClick={() => {
            setDialogItem(toastItem);
            setToastItem(null);
          }}
          onDismiss={() => setToastItem(null)}
        />
      )}

      <ProductDetailModal
        item={dialogItem}
        visible={dialogItem !== null}
        onDismiss={() => setDialogItem(null)}
        onAddToCart={(item) => {
          handleAddToCart(item);
        }}
        isDiscounted={dialogItem ? discountedItems.has(dialogItem.name) : false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
  },
  cartButton: {
    position: "relative",
  },
  badge: {
    position: "absolute",
    top: -8,
    right: -8,
    backgroundColor: "#ff4444",
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  badgeText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  list: {
    padding: 8,
  },
});

