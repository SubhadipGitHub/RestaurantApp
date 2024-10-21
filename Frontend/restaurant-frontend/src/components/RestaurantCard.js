export default function RestaurantCard({ restaurant }) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-2">{restaurant.name}</h2>
        <p className="text-gray-700 mb-4">{restaurant.description}</p>
        <button className="bg-blue-500 text-white px-4 py-2 rounded">
          Book Now
        </button>
      </div>
    );
  }
  