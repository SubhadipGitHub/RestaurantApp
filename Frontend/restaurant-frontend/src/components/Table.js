import React from 'react';

const Table = ({ table, onSelect, selectedTime, busy }) => {
  // The API reports status in upper case: AVAILABLE | BLOCKED | OCCUPIED.
  const isAvailable = table.status === 'AVAILABLE';

  const handleClick = () => {
    if (busy) return;
    onSelect(table._id, isAvailable);
  };

  return (
    <div
      className={`p-4 border rounded-lg ${
        busy ? 'opacity-60 cursor-wait' : 'cursor-pointer'
      } ${isAvailable ? 'bg-green-200' : 'bg-red-200'}`}
      onClick={handleClick}
    >
      <h3 className="text-lg font-bold">Table {table.label || table._id}</h3>
      <p>Seats: {table.seats}</p>
      <p>Status: {table.status}</p>
      {isAvailable && selectedTime && <p>Selected: {selectedTime}</p>}
    </div>
  );
};

export default Table;
