"use client"; // Make this a Client Component

import localFont from "next/font/local";
import "./globals.css";
import Cookies from 'js-cookie';
import { AuthProvider } from './AuthContext'; // Correct import path for AuthProvider
import { useEffect, useState } from "react";


export default function RootLayout({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const userCookie = Cookies.get('user'); // Get the user cookie

    if (userCookie) {
      setUser(JSON.parse(userCookie)); // Parse and set user data
      setIsLoggedIn(true); // Set logged-in status to true
    }
    setLoading(false); // Set loading to false after checking the cookie
  }, []);

  const handleLogout = () => {
    setUser(null);
    setIsLoggedIn(false);
    Cookies.remove('user'); // Remove the user cookie
    window.location.href = "/"; // Redirect to home
  };

  // Show loading state while checking authentication status
  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    
      <html lang="en">
        <head>
          <title>Restaurant Booking App</title>
        </head>
        <body className="bg-gray-100 text-gray-800" suppressHydrationWarning={true}>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            {/* Navigation Bar */}
            <nav className="bg-white shadow-md">
              <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="flex justify-between items-center">
                  <a href="/" className="text-2xl font-bold text-gray-900">
                    Restaurant App
                  </a>
                  <div className="relative">
                    {isLoggedIn ? (
                      // Show dropdown if user is logged in
                      <>
                        <button
                          className="text-lg text-gray-900 focus:outline-none"
                          onClick={() => setIsDropdownOpen((prev) => !prev)}
                        >
                          {user?.name}
                        </button>
                        {isDropdownOpen && (
                          <div
                            className="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-md z-50"
                            style={{ zIndex: 50 }} // Ensure the dropdown appears on top
                          >
                            <a
                              href="/dashboard"
                              className="block px-4 py-2 text-gray-800 hover:bg-gray-200"
                            >
                              Dashboard
                            </a>
                            <button
                              onClick={handleLogout}
                              className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-200"
                            >
                              Logout
                            </button>
                          </div>
                        )}
                      </>
                    ) : (
                      // Show Sign In link if user is not logged in
                      <a href="/login" className="text-lg text-gray-900 hover:text-blue-500">
                        Sign In
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </nav>


            {/* Page Content */}
            <main className="flex-grow">{children}</main>

            {/* Footer */}
            <footer className="bg-white text-center py-6 shadow-inner">
              <p className="text-gray-500">&copy; 2024 Restaurant App. All rights reserved.</p>
            </footer>
          </div>
          </AuthProvider>
        </body>
      </html>    
  );
}
