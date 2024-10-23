"use client";

import { useRouter } from "next/navigation"; // Correct import in App Router
import { useEffect } from "react";
import { useAuth } from '../../AuthContext';  // Import the useAuth hook

export default function AuthCallback() {
  const router = useRouter();  
  const { login } = useAuth();  // Use the login function from AuthContext

  useEffect(() => {
    const handleAuth = async () => {
      const searchParams = new URLSearchParams(window.location.search);
      const user = searchParams.get('user');  // Get the 'user' param from the URL
      const error = searchParams.get('error');  // Get the 'error' param from the URL

      if (error) {
        // Handle error
        console.error("Authentication error:", error);
        alert(`Authentication Error: ${error}`); // Show an alert or notification
        // Optionally redirect to a specific error page or stay on the same page
        return;
      }

      if (user) {
        try {
          const parsedUser = JSON.parse(user);  // Parse the user data

          // Call the login function to update the auth state
          login(parsedUser);

          // Redirect to the dashboard
          router.push("/dashboard");
        } catch (err) {
          console.error("Failed to parse user data:", err);
          alert("Failed to parse user data."); // Show an alert for parsing error
        }
      }
    };

    handleAuth();
  }, []);

  return <div>Loading...</div>;  // Simple loading page while processing
}
