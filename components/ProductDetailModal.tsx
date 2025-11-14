import { ClothingItem } from "@/types";
import React from "react";
import {
    Image,
    Modal,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from "react-native";

interface ProductDetailModalProps {
  item: ClothingItem | null;
  visible: boolean;
  onDismiss: () => void;
  onAddToCart: (item: ClothingItem) => void;
  isDiscounted: boolean;
}

export function ProductDetailModal({
  item,
  visible,
  onDismiss,
  onAddToCart,
  isDiscounted,
}: ProductDetailModalProps) {
  if (!item) return null;

  const discount = isDiscounted ? 0.2 : 0;
  const discountedPrice = item.price * (1 - discount);

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onDismiss}
    >
      <View style={styles.overlay}>
        <View style={styles.dialog}>
          <ScrollView>
            <Image source={{ uri: item.imageUrl }} style={styles.image} />

            <View style={styles.content}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.description}>{item.description}</Text>

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

              <TouchableOpacity
                style={styles.addButton}
                onPress={() => {
                  onAddToCart(item);
                  onDismiss();
                }}
              >
                <Text style={styles.addButtonText}>Add to Cart</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.cancelButton} onPress={onDismiss}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  dialog: {
    backgroundColor: "#fff",
    borderRadius: 16,
    maxWidth: 500,
    width: "100%",
    maxHeight: "80%",
    overflow: "hidden",
  },
  image: {
    width: "100%",
    height: 200,
  },
  content: {
    padding: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: "#666",
    marginBottom: 16,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 16,
  },
  price: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#007AFF",
    marginBottom: 16,
  },
  originalPrice: {
    fontSize: 28,
    fontWeight: "bold",
    textDecorationLine: "line-through",
    color: "#999",
  },
  discountedPrice: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#ff4444",
  },
  addButton: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 8,
  },
  addButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  cancelButton: {
    padding: 16,
    alignItems: "center",
  },
  cancelButtonText: {
    color: "#007AFF",
    fontSize: 16,
  },
});

