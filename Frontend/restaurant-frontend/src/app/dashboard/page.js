// src/app/dashboard/page.js
"use client";

import Image from 'next/image';
import Link from 'next/link';

import { useAuth } from '../AuthContext';
import TableSelection from '../../components/TableSelection';

const Dashboard = () => {
  const { isLoggedIn, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-xl">Loading...</p>
      </div>
    );
  }

  // A convenience redirect, not a security boundary -- the API rejects
  // unauthenticated requests regardless of what this component renders.
  if (!isLoggedIn || !user) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <p className="text-xl">Please log in to access the dashboard.</p>
        <Link href="/login" className="text-blue-600 underline">
          Go to sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-3xl mx-auto mt-10">
      <div className="flex items-center mb-4">
        {user.picture && (
          <Image
            src={user.picture}
            alt="Profile Picture"
            width={128}
            height={128}
            className="border-2 border-gray-300 shadow-md mr-4 rounded-lg"
            priority
          />
        )}
        <div>
          <h1 className="text-2xl font-bold">{`Welcome, ${user.name}!`}</h1>
          <p className="text-lg text-gray-600">{user.email}</p>
        </div>
      </div>

      <div className="container mx-auto py-4">
        <h2 className="text-3xl font-bold mb-6">Table Selection</h2>
        <TableSelection />
      </div>
    </div>
  );
};

export default Dashboard;
