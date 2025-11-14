import { ClothingItem } from "@/types";
import { ClickTracker } from "@demoshop/sdk";
import { Ionicons } from "@expo/vector-icons";
import { router, useLocalSearchParams } from "expo-router";
import React, { useEffect, useMemo, useState } from "react";
import {
    Alert,
    FlatList,
    Image,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function CartScreen() {
  const params = useLocalSearchParams();
  
  const initialCart = useMemo(() => {
    try {
      if (params.cart && typeof params.cart === "string") {
        return JSON.parse(params.cart);
      }
    } catch (error) {
      console.error("Failed to parse cart data:", error);
    }
    return [];
  }, [params.cart]);

  const initialDiscountedItems = useMemo((): Set<string> => {
    try {
      if (params.discountedItems && typeof params.discountedItems === "string") {
        const parsed = JSON.parse(params.discountedItems);
        return new Set<string>(parsed);
      }
    } catch (error) {
      console.error("Failed to parse discounted items:", error);
    }
    return new Set<string>();
  }, [params.discountedItems]);

  const [cart, setCart] = useState<ClothingItem[]>(initialCart);
  const [discountedItems, setDiscountedItems] = useState<Set<string>>(initialDiscountedItems);

  useEffect(() => {
    setCart(initialCart);
    setDiscountedItems(initialDiscountedItems);
  }, [initialCart, initialDiscountedItems]);

  const calculateTotal = () => {
    return cart.reduce((total, item) => {
      const discount = discountedItems.has(item.name) ? 0.2 : 0;
      return total + item.price * (1 - discount);
    }, 0);
  };

  const handleBuyNow = async () => {
    const total = calculateTotal();
    
    try {
      // Calculate items with discounts
      const items = cart.map(item => ({
        name: item.name,
        price: item.price,
        discount: discountedItems.has(item.name) ? 0.2 : 0,
        finalPrice: item.price * (discountedItems.has(item.name) ? 0.8 : 1),
      }));
      
      // Track purchase via SDK (handles server communication)
      const success = await ClickTracker.trackPurchase({
        items: items,
        total: total,
      });
      
      if (success) {
        console.log('[Cart] Purchase successfully tracked');
      }
      
      // Clear local state
      setCart([]);
      setDiscountedItems(new Set());
      
      Alert.alert("Purchase Complete", `Total: $${total.toFixed(2)}\n\nYour cart has been cleared.`, [
        { text: "OK", onPress: () => router.back() },
      ]);
    } catch (error) {
      console.error('[Cart] Error during purchase:', error);
      Alert.alert("Purchase Complete", `Total: $${total.toFixed(2)}`, [
        { text: "OK" },
      ]);
    }
  };

  const renderCartItem = ({
    item,
    index,
  }: {
    item: ClothingItem;
    index: number;
  }) => {
    const isDiscounted = discountedItems.has(item.name);
    const discount = isDiscounted ? 0.2 : 0;
    const discountedPrice = item.price * (1 - discount);

    return (
      <View style={styles.cartItem}>
        <Image source={{ uri: item.imageUrl }} style={styles.itemImage} />
        <View style={styles.itemInfo}>
          <Text style={styles.itemName}>{item.name}</Text>
          {discount > 0 ? (
            <View style={styles.priceRow}>
              <Text style={styles.originalPrice}>${item.price.toFixed(2)}</Text>
              <Text style={styles.discountedPrice}>
                ${discountedPrice.toFixed(2)}
              </Text>
            </View>
          ) : (
            <Text style={styles.price}>${item.price.toFixed(2)}</Text>
          )}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => {
            router.back();
          }}
        >
          <Ionicons name="arrow-back" size={28} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Cart</Text>
        <View style={{ width: 28 }} />
      </View>

      {cart.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="cart-outline" size={80} color="#ccc" />
          <Text style={styles.emptyText}>Your cart is empty</Text>
        </View>
      ) : (
        <>
          <FlatList
            data={cart}
            renderItem={renderCartItem}
            keyExtractor={(item, index) => `${item.name}-${index}`}
            contentContainerStyle={styles.list}
          />
          <View style={styles.footer}>
            <Text style={styles.totalText}>
              Total: ${calculateTotal().toFixed(2)}
            </Text>
            <TouchableOpacity style={styles.buyButton} onPress={handleBuyNow}>
              <Text style={styles.buyButtonText}>Buy Now</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
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
  backButton: {
    padding: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: 18,
    color: "#999",
    marginTop: 16,
  },
  list: {
    padding: 16,
  },
  cartItem: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  itemImage: {
    width: 64,
    height: 64,
    borderRadius: 32,
  },
  itemInfo: {
    marginLeft: 16,
    flex: 1,
    justifyContent: "center",
  },
  itemName: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 4,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  price: {
    fontSize: 14,
    color: "#666",
  },
  originalPrice: {
    fontSize: 14,
    color: "#999",
    textDecorationLine: "line-through",
  },
  discountedPrice: {
    fontSize: 14,
    color: "#ff4444",
    fontWeight: "600",
  },
  footer: {
    backgroundColor: "#fff",
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#e0e0e0",
  },
  totalText: {
    fontSize: 24,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 16,
  },
  buyButton: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  buyButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
});

