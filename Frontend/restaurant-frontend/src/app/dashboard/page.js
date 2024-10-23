// src/app/dashboard/page.js
"use client"; // Make this a Client Component

import { useAuth } from '../AuthContext';
import TableSelection from '../../components/TableSelection'; // Adjust the path based on your file structure

import Image from 'next/image';

const Dashboard = () => {
  const { isLoggedIn, user, logout } = useAuth();

  console.log("isLoggedIn:", isLoggedIn);
  console.log("user:", user);

  if (!isLoggedIn || !user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-xl">Please log in to access the dashboard.</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-3xl mx-auto mt-10">
      {/* Profile Image */}
      <div className="flex items-center mb-4">
        <Image
          src={user.picture || '/images/default-profile.png'} // Ensure the default image path is correct
          alt="Profile Picture"
          width={128} // Set width
          height={128} // Set height
          className="border-2 border-gray-300 shadow-md mr-4 rounded-lg"
          priority // This ensures the image is prioritized during loading
        />
        <div>
          <h1 className="text-2xl font-bold">{`Welcome, ${user.name}!`}</h1>
          <p className="text-lg text-gray-600">{`Email: ${user.email}`}</p>
          <p className="text-lg text-gray-600">{`User ID: ${user.id}`}</p>
        </div>
      </div>
      {/* Additional Info Section (optional) */}
      <div className="mt-4">
        <h2 className="text-xl font-semibold">About You</h2>
        <p className="text-gray-500">Add some additional info here if needed.</p>
      </div>

      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">Table Selection</h1>
        <TableSelection />
      </div>
    </div>

  );
};

export default Dashboard;
