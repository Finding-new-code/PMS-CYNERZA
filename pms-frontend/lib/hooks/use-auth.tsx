'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';

interface User {
    id: number;
    email: string;
    name: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (token: string) => void;
    logout: () => void;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    const login = (token: string) => {
        localStorage.setItem('access_token', token);
        checkAuth();
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
        router.push('/login');
    };

    const checkAuth = async () => {
        const token = localStorage.getItem('access_token');
        
        // Demo mode: If no token and in development, use mock user
        const isDemoMode = process.env.NODE_ENV === 'development';
        
        if (!token && !isDemoMode) {
            setUser(null);
            setIsLoading(false);
            return;
        }

        try {
            const { data } = await apiClient.get<User>('/auth/me');
            setUser(data);
        } catch (error) {
            console.error('Auth verification failed:', error);
            
            // In demo mode, create a mock user when backend is unavailable
            if (isDemoMode) {
                console.warn('Demo mode: Using mock user (backend unavailable)');
                setUser({
                    id: 1,
                    email: 'admin@hotel.com',
                    name: 'Demo Admin',
                    role: 'admin',
                });
            } else {
                localStorage.removeItem('access_token');
                setUser(null);
            }
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    return (
        <AuthContext.Provider value={{ user, isLoading, login, logout, checkAuth }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
