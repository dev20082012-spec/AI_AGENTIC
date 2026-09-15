import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { API_BASE } from "../config";

const ChatContext = createContext(null);

const STORAGE_KEYS = {
  executive: "chat_executive",
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

  const [threads, setThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);

  const fetchThreads = useCallback(async (spec = "executive") => {
    try {
      const res = await fetch(`${API_BASE}/api/threads?specialist=${spec}`);
      if (res.ok) {
        const data = await res.json();
        setThreads(data.threads || []);
      }
    } catch (e) {
      // Backend threads optional, silent fallback to local
    }
  }, []);

  useEffect(() => {
    fetchThreads("executive");
  }, [fetchThreads]);

  const addMessage = (specialist, message) => {
    setConversations((prev) => {
      const updatedList = [...(prev[specialist] || []), message];
      try {
        localStorage.setItem(STORAGE_KEYS[specialist], JSON.stringify(updatedList));
      } catch (e) {
        console.error("Failed to save to localStorage:", e);
      }

      // Proactively sync thread to server if on executive chat
      if (specialist === "executive" && updatedList.length > 0) {
        fetch(`${API_BASE}/api/threads`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            thread_id: activeThreadId,
            specialist: "executive",
            messages: updatedList,
          }),
        })
          .then((res) => res.ok ? res.json() : null)
          .then((saved) => {
            if (saved?.thread_id && !activeThreadId) {
              setActiveThreadId(saved.thread_id);
              fetchThreads("executive");
            }
          })
          .catch(() => {});
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
    setActiveThreadId(null);
  };

  const switchThread = async (threadId, specialist = "executive") => {
    try {
      const res = await fetch(`${API_BASE}/api/threads/${threadId}`);
      if (res.ok) {
        const threadData = await res.json();
        const msgs = threadData.messages || [];
        setConversations((prev) => ({
          ...prev,
          [specialist]: msgs,
        }));
        try {
          localStorage.setItem(STORAGE_KEYS[specialist], JSON.stringify(msgs));
        } catch (e) {}
        setActiveThreadId(threadId);
      }
    } catch (e) {
      console.error("Failed to switch thread:", e);
    }
  };

  const newThread = (specialist = "executive") => {
    clearHistory(specialist);
    setActiveThreadId(null);
  };

  return (
    <ChatContext.Provider
      value={{
        conversations,
        addMessage,
        clearHistory,
        threads,
        activeThreadId,
        switchThread,
        newThread,
        refreshThreads: fetchThreads,
      }}
    >
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
