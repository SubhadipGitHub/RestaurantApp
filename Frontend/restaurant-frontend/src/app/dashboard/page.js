// src/app/dashboard/page.js
"use client"; // Make this a Client Component

import { useAuth } from '../AuthContext'; // Import the useAuth hook

const Dashboard = () => {
  const { isLoggedIn, user, logout } = useAuth(); // Use the authentication context

  if (!isLoggedIn) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-xl">Please log in to access the dashboard.</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded shadow-md">
      <h1 className="text-2xl font-bold mb-4">Welcome, {user?.name}!</h1>
      <p className="text-lg mb-2">Email: {user?.email}</p>
      <p className="text-lg mb-4">User ID: {user?.id}</p>
      <button
        onClick={logout}
        className="mt-4 bg-red-500 text-white px-4 py-2 rounded transition duration-300 hover:bg-red-600"
      >
        Logout
      </button>
    </div>
  );
};

export default Dashboard;
