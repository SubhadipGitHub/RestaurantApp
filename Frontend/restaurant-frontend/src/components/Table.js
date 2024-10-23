import React from 'react';

const Table = ({ table, onSelect, selectedTime }) => {
  const isAvailable = table.status === 'available';

  const handleClick = () => {
    onSelect(table.id, isAvailable);
  };

  return (
    <div 
      className={`p-4 border rounded-lg cursor-pointer ${isAvailable ? 'bg-green-200' : 'bg-red-200'}`} 
      onClick={handleClick}
    >
      <h3 className="text-lg font-bold">Table {table.number}</h3>
      <p>Status: {table.status}</p>
      {isAvailable && selectedTime && <p>Selected Time: {selectedTime}</p>}
    </div>
  );
};

export default Table;
