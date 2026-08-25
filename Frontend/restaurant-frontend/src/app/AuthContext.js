"use client";

// src/app/AuthContext.js
import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Auth state comes from the server, not from a cookie this code can read.
  // The session cookie is HttpOnly by design, so asking the API who we are is
  // the only honest way to answer it.
  const refresh = useCallback(async () => {
    try {
      const res = await fetch('/api/backend/me', { cache: 'no-store' });
      setUser(res.ok ? await res.json() : null);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const logout = useCallback(async () => {
    try {
      await fetch('/api/backend/logout', { method: 'POST' });
    } finally {
      setUser(null);
      window.location.href = '/';
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ isLoggedIn: Boolean(user), user, loading, logout, refresh }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
