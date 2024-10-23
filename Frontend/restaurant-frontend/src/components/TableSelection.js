"use client";

import React, { useState, useEffect } from 'react';
import Table from './table'; // Import your Table component

const TableSelection = () => {
  // Hardcode the restaurant ID for now
  const restaurantId = 'tst1'; // Replace with your actual restaurant ID
  const [tables, setTables] = useState([]);
  const [selectedTime, setSelectedTime] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);
    // Fetch table statuses when the component mounts
    const fetchTableStatuses = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/tables?restaurantId=${restaurantId}`);
        const data = await response.json();
        setTables(data.tables); // Assuming the API returns a `tables` array
      } catch (err) {
        console.error('Error fetching table statuses:', err);
        setError('Failed to fetch table statuses');
      }
    };

    fetchTableStatuses();
  }, [restaurantId]);

  const handleTableSelection = async (tableId, isSelected) => {
    // Booking API call
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/book-table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tableId, restaurantId, time: selectedTime }),
      });

      if (!response.ok) {
        throw new Error('Failed to book the table');
      }

      // Optionally update the local state here to reflect the booking status
      const updatedTables = tables.map(table => 
        table.id === tableId ? { ...table, status: isSelected ? 'booked' : 'available' } : table
      );
      setTables(updatedTables);

    } catch (err) {
      console.error('Error booking table:', err);
      setError('Failed to book the table');
    }
  };

  return (
    <div>
      <h2>Select a Table</h2>
      <input 
        type="time" 
        value={selectedTime} 
        onChange={(e) => setSelectedTime(e.target.value)} 
      />
      {error && <p className="text-red-500">{error}</p>}
      <div className="grid md:grid-cols-3 gap-4">
        {tables.map((table) => (
          <Table 
            key={table.id}
            table={table}
            onSelect={handleTableSelection}
            selectedTime={selectedTime}
          />
        ))}
      </div>
    </div>
  );
};

export default TableSelection;
