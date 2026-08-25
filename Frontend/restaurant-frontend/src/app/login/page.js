"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

function LoginContent() {
  const [isLoading, setIsLoading] = useState(false);
  // The backend may be idle on a free hosting tier; waking it before the user
  // clicks avoids a timeout on the OAuth round trip.
  const [apiReady, setApiReady] = useState(false);
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  useEffect(() => {
    let cancelled = false;
    const wake = async () => {
      try {
        const res = await fetch("/api/backend/health", { cache: "no-store" });
        if (!cancelled && res.ok) setApiReady(true);
      } catch {
        if (!cancelled) setTimeout(wake, 3000);
      }
    };
    wake();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleGoogleLogin = () => {
    setIsLoading(true);
    // The backend owns the whole Google URL, including the state parameter.
    // The browser never needs to know the client ID.
    window.location.href = "/api/backend/login/google";
  };

  const disabled = isLoading || !apiReady;

  return (
    <div
      className="flex items-center justify-center h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/images/restaurant-bg.jpeg')" }}
    >
      <div className="bg-white bg-opacity-80 p-8 rounded-lg shadow-lg flex flex-col items-center max-w-lg w-full">
        <h1 className="text-4xl font-extrabold text-gray-800 mb-4">
          Welcome to Restaurant App
        </h1>
        <p className="text-gray-600 mb-8">
          Book your favorite restaurant in seconds. Sign in to get started.
        </p>

        {error && (
          <p className="mb-4 w-full text-center text-red-700 bg-red-100 border border-red-200 rounded px-3 py-2">
            {error}
          </p>
        )}

        <button
          onClick={handleGoogleLogin}
          className={`${
            disabled ? "bg-gray-400 cursor-not-allowed" : "bg-red-500 hover:bg-red-600"
          } text-white font-bold py-3 px-6 rounded-lg focus:outline-none flex items-center justify-center w-full transition-colors duration-300 ease-in-out`}
          disabled={disabled}
        >
          {isLoading
            ? "Signing in..."
            : apiReady
            ? "Sign in with Google"
            : "Waking up the server..."}
        </button>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
      <LoginContent />
    </Suspense>
  );
}
