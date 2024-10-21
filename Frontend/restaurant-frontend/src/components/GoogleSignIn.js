"use client"; // Make this a Client Component

import { useState } from "react";

export default function GoogleSignIn() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleLogin = () => {
    setIsLoading(true); // Set loading state

    const googleSignInURL =
      `https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=${process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:3000/login&scope=openid%20profile%20email&access_type=offline`;

    window.location.href = googleSignInURL; // Redirect to Google Sign-In
  };

  return (
      <button
        onClick={handleGoogleLogin}
        className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
        disabled={isLoading}
      >
        {isLoading ? "Signing in..." : "Sign in with Google"}
      </button>
  );
}
