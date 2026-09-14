import React, { createContext, useContext, useState, useEffect } from "react";

const ChatContext = createContext(null);

const STORAGE_KEYS = {
  finance: "chat_finance",
  ops: "chat_ops",
  marketing: "chat_marketing",
};

export function ChatProvider({ children }) {
  const [conversations, setConversations] = useState(() => {
    const initial = {};
    for (const [key, storageKey] of Object.entries(STORAGE_KEYS)) {
      try {
        const saved = localStorage.getItem(storageKey);
        initial[key] = saved ? JSON.parse(saved) : [];
      } catch (e) {
        initial[key] = [];
      }
    }
    return initial;
  });

  const addMessage = (specialist, message) => {
    setConversations((prev) => {
      const updatedList = [...(prev[specialist] || []), message];
      try {
        localStorage.setItem(STORAGE_KEYS[specialist], JSON.stringify(updatedList));
      } catch (e) {
        console.error("Failed to save to localStorage:", e);
      }
      return {
        ...prev,
        [specialist]: updatedList,
      };
    });
  };

  const clearHistory = (specialist) => {
    setConversations((prev) => {
      try {
        localStorage.removeItem(STORAGE_KEYS[specialist]);
      } catch (e) {}
      return {
        ...prev,
        [specialist]: [],
      };
    });
  };

  return (
    <ChatContext.Provider value={{ conversations, addMessage, clearHistory }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
