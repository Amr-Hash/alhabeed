"use client";

import Cookies from "js-cookie";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, User } from "./api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async (accessToken: string) => {
    try {
      const me = await api.me(accessToken);
      setUser(me);
      setToken(accessToken);
    } catch {
      Cookies.remove("access_token");
      Cookies.remove("refresh_token");
      setUser(null);
      setToken(null);
    }
  }, []);

  useEffect(() => {
    const access = Cookies.get("access_token");
    if (access) {
      loadUser(access).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    const tokens = await api.login(email, password);
    Cookies.set("access_token", tokens.access, { expires: 1 });
    Cookies.set("refresh_token", tokens.refresh, { expires: 7 });
    await loadUser(tokens.access);
  };

  const register = async (username: string, email: string, password: string) => {
    await api.register({ username, email, password, password_confirm: password });
    await login(email, password);
  };

  const logout = async () => {
    const refresh = Cookies.get("refresh_token");
    const access = Cookies.get("access_token");
    if (refresh && access) {
      try {
        await api.logout(refresh, access);
      } catch {
        /* ignore */
      }
    }
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
