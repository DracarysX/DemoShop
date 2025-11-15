import { ClothingItem } from "@/types";
import React, { createContext, useContext, useState } from "react";

interface CartContextType {
  cart: ClothingItem[];
  discountedItems: Set<string>;
  addToCart: (item: ClothingItem) => void;
  clearCart: () => void;
  addDiscountedItem: (itemName: string) => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<ClothingItem[]>([]);
  const [discountedItems, setDiscountedItems] = useState<Set<string>>(new Set());

  const addToCart = (item: ClothingItem) => {
    setCart((prev) => [...prev, item]);
  };

  const clearCart = () => {
    setCart([]);
  };

  const addDiscountedItem = (itemName: string) => {
    setDiscountedItems((prev) => new Set(prev).add(itemName));
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        discountedItems,
        addToCart,
        clearCart,
        addDiscountedItem,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}

