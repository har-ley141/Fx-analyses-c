import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import FXDashboard from "./components/FXDashboard";
import Navigation from "./components/Navigation";

function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<FXDashboard />} />
          <Route path="/dashboard" element={<FXDashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;