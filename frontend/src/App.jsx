import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ChatProvider } from "./context/ChatContext";
import LandingPage from "./pages/LandingPage";
import ChatPage from "./pages/ChatPage";
import BriefingPage from "./pages/BriefingPage";

export default function App() {
  return (
    <ChatProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat/:specialist" element={<ChatPage />} />
          <Route path="/briefing" element={<BriefingPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ChatProvider>
  );
}
