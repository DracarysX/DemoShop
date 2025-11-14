export interface ClothingItem {
  name: string;
  price: number;
  imageUrl: string;
  description: string;
}

export const clothingItems: ClothingItem[] = [
  {
    name: "T-Shirt",
    price: 19.99,
    imageUrl:
      "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=3164&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "A classic cotton t-shirt for everyday wear.",
  },
  {
    name: "Jeans",
    price: 49.99,
    imageUrl:
      "https://images.unsplash.com/photo-1602293589930-45aad59ba3ab?q=80&w=3164&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "Stylish and comfortable denim jeans.",
  },
  {
    name: "Jacket",
    price: 79.99,
    imageUrl:
      "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=3174&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "A fashionable jacket to complete your look.",
  },
  {
    name: "Sweater",
    price: 59.99,
    imageUrl:
      "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?q=80&w=3164&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "A stylish sweater to keep you warm.",
  },
  {
    name: "Shorts",
    price: 29.99,
    imageUrl:
      "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?q=80&w=3174&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "Casual shorts for a relaxed day out.",
  },
  {
    name: "Boots",
    price: 99.99,
    imageUrl:
      "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=3224&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    description: "Durable and stylish boots for any occasion.",
  },
];

