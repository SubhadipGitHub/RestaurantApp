// src/app/AuthContext.js
import { createContext, useContext, useState } from 'react';
import Cookies from 'js-cookie';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  const login = (userData) => {
    setUser(userData);
    setIsLoggedIn(true);
    Cookies.set('user', JSON.stringify(userData), { expires: 1 }); // Set cookie for 1 day
  };

  const logout = () => {
    setUser(null);
    setIsLoggedIn(false);
    Cookies.remove('user');
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
