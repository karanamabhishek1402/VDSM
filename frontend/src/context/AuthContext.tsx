import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, AuthContextType } from '../types';
import { authService } from '../services/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAuth = async () => {
      try {
        const storedToken = localStorage.getItem('vdsm_token');
        const storedUser = localStorage.getItem('vdsm_user');

        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          try {
            await authService.getProfile();
          } catch (err) {
            authService.logout();
            setUser(null);
            setToken(null);
          }
        }
      } catch (err) {
        console.error('Failed to load auth:', err);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    loadAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);

      const tokenData = await authService.login(email, password);
      const userData = await authService.getProfile();

      localStorage.setItem('vdsm_token', tokenData.access_token);
      localStorage.setItem('vdsm_user', JSON.stringify(userData));

      setToken(tokenData.access_token);
      setUser(userData);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, username: string, password: string, fullName: string) => {
    try {
      setError(null);
      setIsLoading(true);

      await authService.register({ email, username, password, full_name: fullName });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setToken(null);
    setError(null);
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      setError(null);
      const userData = await authService.getProfile();
      setUser(userData);
      const storedToken = localStorage.getItem('vdsm_token');
      setToken(storedToken);
    } catch (err: any) {
      setError('Session expired. Please login again.');
      logout();
    }
  }, [logout]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    error,
    login,
    register,
    logout,
    checkAuth,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
