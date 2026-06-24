import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import UploadAnalyze from './pages/UploadAnalyze';
import AnalysisResult from './pages/AnalysisResult';
import InterviewPrep from './pages/InterviewPrep';
import Chatbot from './pages/Chatbot';
import './App.css';

// Guard component for authenticated routes
const PrivateRoute = ({ children }) => {
    const { token, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-400 text-sm font-medium">Synchronizing secure session...</p>
                </div>
            </div>
        );
    }

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1 pb-16">
                {children}
            </main>
        </div>
    );
};

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public Routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />

                    {/* Protected Routes */}
                    <Route path="/" element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    } />
                    <Route path="/analyze" element={
                        <PrivateRoute>
                            <UploadAnalyze />
                        </PrivateRoute>
                    } />
                    <Route path="/analysis/:id" element={
                        <PrivateRoute>
                            <AnalysisResult />
                        </PrivateRoute>
                    } />
                    <Route path="/analysis/:id/prep" element={
                        <PrivateRoute>
                            <InterviewPrep />
                        </PrivateRoute>
                    } />
                    <Route path="/chat" element={
                        <PrivateRoute>
                            <Chatbot />
                        </PrivateRoute>
                    } />
                    <Route path="/chat/:analysisId" element={
                        <PrivateRoute>
                            <Chatbot />
                        </PrivateRoute>
                    } />

                    {/* Redirect Fallbacks */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
