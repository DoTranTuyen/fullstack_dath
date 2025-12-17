import { createContext, useEffect, useState } from "react";
import { endSession, readSession } from "../../web_qr/services/api";

// Create a context for the socket
export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  const fetchUserProfile = async () => {
    try {
      const fetchSession = await readSession();
      return fetchSession;
    } catch (error) {
      return null;
    }
  };

  // Ends the session and redirects the user
  const asyncEndSession = async () => {
    try {
      const response = await endSession();
      if (response.status === 200) {
        console.log("✅ End session thành công");
        window.location.href = "/thank-you";
      } else {
        console.error("⚠️ End session failed:", response);
      }
    } catch (err) {
      console.error("❌ Error ending session:", err);
    }
  };

  // Initialize WebSocket connection on mount
  useEffect(() => {
    const ws = new WebSocket("ws://192.168.1.114:5001/ws/notifications/order/");

    ws.onopen = () => console.log("✅ WebSocket connected!");
    ws.onclose = (event) => console.log("❌ WebSocket disconnected!", event);
    ws.onerror = (error) => console.error("⚠️ WebSocket error:", error);

    setSocket(ws);

    // Cleanup WebSocket on unmount
    return () => {
      ws.close();
    };
  }, []);

  // Listen for messages from the WebSocket
  useEffect(() => {
    if (!socket) return;

    const handleMessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        const session = await fetchUserProfile();
        if (
          data?.type === "end_session" &&
          session?.data?.session?.session_id === data?.data?.session_id
        ) {
          asyncEndSession();
        }

        // Handle other message types here if needed
      } catch (err) {
        console.error("❌ Error parsing WebSocket message:", err);
      }
    };

    socket.addEventListener("message", handleMessage);

    socket.addEventListener("message", handleMessage);

    // Cleanup event listener on unmount or socket change
    return () => {
      socket.removeEventListener("message", handleMessage);
    };
  }, [socket]);

  return (
    <SocketContext.Provider value={socket}>{children}</SocketContext.Provider>
  );
};
