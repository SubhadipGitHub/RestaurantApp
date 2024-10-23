"use client";

import { useState } from "react";

export default function GoogleSignIn() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleLogin = () => {
    setIsLoading(true);
    const googleSignInURL = `https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=${process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_FASTAPI}&scope=openid%20profile%20email&access_type=offline`;
    
    // Redirect to Google Sign-In
    window.location.href = googleSignInURL;
  };

  return (
    <div
      className="flex items-center justify-center h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/images/restaurant-bg.jpeg')" }}
    >
      <div className="bg-white bg-opacity-80 p-8 rounded-lg shadow-lg flex flex-col items-center max-w-lg w-full">
        {/* Logo */}
        <img
          src="/images/placeholder-image.jpg"
          alt="Restaurant App Logo"
          className="w-16 h-16 mb-6"
        />

        {/* Heading */}
        <h1 className="text-4xl font-extrabold text-gray-800 mb-4">
          Welcome to Restaurant App
        </h1>
        <p className="text-gray-600 mb-8">
          Book your favorite restaurant in seconds. 
          Sign in to get started.
        </p>

        {/* Google Sign-In Button */}
        <button
          onClick={handleGoogleLogin}
          className={`${
            isLoading ? "bg-gray-400 cursor-not-allowed" : "bg-red-500"
          } text-white font-bold py-3 px-6 rounded-lg hover:bg-red-600 focus:outline-none flex items-center justify-center w-full transition-colors duration-300 ease-in-out`}
          disabled={isLoading}
        >
          <img
            src="/images/google-icon.png"
            alt="Google Icon"
            className="w-5 h-5 mr-3"
          />
          {isLoading ? "Signing in..." : "Sign in with Google"}
        </button>
      </div>
    </div>
  );
}
