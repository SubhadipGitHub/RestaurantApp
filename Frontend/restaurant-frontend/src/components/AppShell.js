"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useAuth } from "../app/AuthContext";

// Routes that render without the app chrome.
const BARE_ROUTES = ["/customer"];

export default function AppShell({ children }) {
  const pathname = usePathname();
  const { isLoggedIn, user, loading, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  if (BARE_ROUTES.includes(pathname)) {
    return <div>{children}</div>;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-gray-900">
              Restaurant App
            </Link>
            <div className="relative">
              {loading ? null : isLoggedIn ? (
                <>
                  <button
                    className="text-lg text-gray-900 focus:outline-none"
                    onClick={() => setIsDropdownOpen((prev) => !prev)}
                  >
                    {user?.name}
                  </button>
                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-md z-50">
                      <Link
                        href="/dashboard"
                        className="block px-4 py-2 text-gray-800 hover:bg-gray-200"
                        onClick={() => setIsDropdownOpen(false)}
                      >
                        Dashboard
                      </Link>
                      <button
                        onClick={logout}
                        className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-200"
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <Link
                  href="/login"
                  className="text-lg text-gray-900 hover:text-blue-500"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow">{children}</main>

      <footer className="bg-white text-center py-6 shadow-inner">
        <p className="text-gray-500">
          &copy; 2024 Restaurant App. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
