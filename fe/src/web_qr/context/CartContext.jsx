import { createContext, useContext, useState, useEffect } from "react";
import { readCart, updateCart, updateQuantityCart } from "../services/api";

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({ items: [] });
  const [loading, setLoading] = useState(false);

  // Fetch cart data from API
  const fetchCart = async () => {
    setLoading(true);
    try {
      const response = await readCart();
      setCart(response.data);
    } catch (error) {
      console.error("Error fetching cart:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  // Add item to cart
  const addItem = async (product_id, quantity) => {
    try {
      const response = await updateCart({ product_id, quantity });
      setCart(prevCart => ({
        ...prevCart,
        items: response.data.items || prevCart.items,
      }));
    } catch (error) {
      console.error("Error adding item:", error);
    }
  };

  // Update item quantity in cart
  const updateItem = async (product_id, quantity) => {
    try {
      const response = await updateQuantityCart({ product_id, quantity });
      setCart(prevCart => ({
        ...prevCart,
        items: response.data.items,
      }));
    } catch (error) {
      console.error("Error updating item:", error);
    }
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        addItem,
        updateItem,
        fetchCart,
        setCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
