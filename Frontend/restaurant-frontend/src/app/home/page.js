"use client"; // Ensure this is a client component

import { useState, useEffect } from "react";
import RestaurantCard from "../../components/RestaurantCard"; 

export default function HomePage() {
  const [restaurants, setRestaurants] = useState([]);

  useEffect(() => {
    fetch("/api/restaurants")
      .then((res) => res.json())
      .then((data) => setRestaurants(data));
  }, []);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <h1 className="text-4xl font-bold text-center mb-8">
        Welcome to RestaurantApp
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {restaurants.length ? (
          restaurants.map((restaurant) => (
            <RestaurantCard key={restaurant.id} restaurant={restaurant} />
          ))
        ) : (
          <p className="text-center">No restaurants available at the moment.</p>
        )}
      </div>
    </div>
  );
}
