import { ClothingItem } from "@/types";
import { useTrackProduct } from "@demoshop/sdk";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import React from "react";
import {
    Image,
    Pressable,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from "react-native";

interface ProductItemProps {
  item: ClothingItem;
  onAddToCart: (item: ClothingItem) => void;
  onItemClick: () => void;
  isDiscounted: boolean;
}

export function ProductItem({
  item,
  onAddToCart,
  onItemClick,
  isDiscounted,
}: ProductItemProps) {
  const discount = isDiscounted ? 0.2 : 0;
  const discountedPrice = item.price * (1 - discount);
  
  // SDK observes this product - tracks views, clicks, and coupons automatically
  const { onPress, trackClick } = useTrackProduct(item.name, onItemClick);

  return (
    <Pressable onPress={onPress} style={styles.card}>
      <View style={styles.imageContainer}>
        <Image source={{ uri: item.imageUrl }} style={styles.image} />

        <LinearGradient
          colors={["transparent", "rgba(0,0,0,0.8)"]}
          style={styles.gradient}
        />

        <View style={styles.priceContainer}>
          {discount > 0 ? (
            <View style={styles.priceRow}>
              <Text style={styles.originalPrice}>
                ${item.price.toFixed(2)}
              </Text>
              <Text style={styles.discountedPrice}>
                ${discountedPrice.toFixed(2)}
              </Text>
            </View>
          ) : (
            <Text style={styles.price}>${item.price.toFixed(2)}</Text>
          )}
        </View>

        <View style={styles.nameContainer}>
          <Text style={styles.name}>{item.name}</Text>
        </View>

        <TouchableOpacity
          style={styles.addButton}
          onPress={async (e) => {
            e.stopPropagation();
            await trackClick();  // SDK tracks this interaction too
            onAddToCart(item);
          }}
        >
          <Ionicons name="cart" size={24} color="#fff" />
        </TouchableOpacity>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    margin: 8,
    borderRadius: 12,
    overflow: "hidden",
    backgroundColor: "#fff",
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  imageContainer: {
    height: 300,
    position: "relative",
  },
  image: {
    width: "100%",
    height: "100%",
  },
  gradient: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    height: "50%",
  },
  priceContainer: {
    position: "absolute",
    top: 12,
    right: 12,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  price: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  originalPrice: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
    textDecorationLine: "line-through",
  },
  discountedPrice: {
    color: "#ff4444",
    fontSize: 18,
    fontWeight: "bold",
  },
  nameContainer: {
    position: "absolute",
    bottom: 12,
    left: 12,
  },
  name: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "bold",
  },
  addButton: {
    position: "absolute",
    bottom: 12,
    right: 12,
    backgroundColor: "#007AFF",
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
  },
});

