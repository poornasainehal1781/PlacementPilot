import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

// Configure backend base URL
const API_URL = 'http://localhost:5000/api';
axios.defaults.baseURL = API_URL;

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);

    // Sync token with axios headers and fetch profile if token exists
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
            fetchProfile();
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
            setUser(null);
            setLoading(false);
        }
    }, [token]);

    const fetchProfile = async () => {
        try {
            const response = await axios.get('/auth/me');
            setUser(response.data.user);
        } catch (error) {
            console.error('Error fetching profile:', error);
            // Only force logout if it's an authorization failure (401 / 403)
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                logout();
            }
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await axios.post('/auth/login', { email, password });
            const { access_token, user: userData } = response.data;
            setToken(access_token);
            setUser(userData);
            return { success: true };
        } catch (error) {
            const errorMsg = error.response?.data?.error || 'Login failed. Please try again.';
            return { success: false, error: errorMsg };
        }
    };

    const register = async (username, email, password) => {
        try {
            await axios.post('/auth/register', { username, email, password });
            return { success: true };
        } catch (error) {
            const errorMsg = error.response?.data?.error || 'Registration failed. Please try again.';
            return { success: false, error: errorMsg };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
