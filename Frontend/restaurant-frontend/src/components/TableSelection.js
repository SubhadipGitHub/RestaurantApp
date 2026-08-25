"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Table from './Table';

// Same-origin path; next.config.mjs rewrites it to the backend. Relative means
// the browser attaches the HttpOnly session cookie automatically.
const API = '/api/backend';

const RESTAURANT_ID = process.env.NEXT_PUBLIC_RESTAURANT_ID || 'REST_001';

const TableSelection = () => {
  const [tables, setTables] = useState([]);
  const [selectedTime, setSelectedTime] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busyTableId, setBusyTableId] = useState(null);

  const fetchTables = useCallback(async () => {
    try {
      const response = await fetch(
        `${API}/tables?restaurant_id=${encodeURIComponent(RESTAURANT_ID)}`,
        { cache: 'no-store' }
      );
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      const data = await response.json();
      setTables(data.tables || []);
      setError('');
    } catch (err) {
      console.error('Error fetching table statuses:', err);
      setError('Failed to load tables. Please refresh.');
    }
  }, []);

  useEffect(() => {
    fetchTables();
  }, [fetchTables]);

  const handleTableSelection = async (tableId, isAvailable) => {
    setNotice('');
    if (!isAvailable) {
      setError('That table is already taken.');
      return;
    }
    if (!selectedTime) {
      setError('Pick a date and time first.');
      return;
    }
    if (!partySize || partySize < 1) {
      setError('How many people are coming?');
      return;
    }

    setBusyTableId(tableId);
    try {
      const response = await fetch(`${API}/bookings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          restaurant_id: RESTAURANT_ID,
          no_of_people: Number(partySize),
          time_slot: selectedTime,
          table_id: tableId,
        }),
      });

      if (response.status === 401) {
        setError('Your session expired. Please sign in again.');
        return;
      }
      if (response.status === 409) {
        setError('Someone just took that table. Try another.');
        await fetchTables();
        return;
      }
      if (!response.ok) throw new Error(`Request failed (${response.status})`);

      const data = await response.json();
      setError('');
      setNotice(`Booked. Your reference is ${data.booking_id}.`);
      // Re-read from the server rather than guessing the new state locally.
      await fetchTables();
    } catch (err) {
      console.error('Error booking table:', err);
      setError('Failed to book the table.');
    } finally {
      setBusyTableId(null);
    }
  };

  return (
    <div>
      <div className="flex flex-wrap gap-4 items-end mb-4">
        <label className="flex flex-col text-sm">
          <span className="mb-1 font-medium">Date &amp; time</span>
          <input
            type="datetime-local"
            className="border rounded px-2 py-1"
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="mb-1 font-medium">Party size</span>
          <input
            type="number"
            min="1"
            className="border rounded px-2 py-1 w-24"
            value={partySize}
            onChange={(e) => setPartySize(e.target.value)}
          />
        </label>
      </div>

      {error && <p className="text-red-600 mb-2">{error}</p>}
      {notice && <p className="text-green-700 mb-2">{notice}</p>}

      {tables.length === 0 ? (
        <p className="text-gray-500">No tables set up for this restaurant yet.</p>
      ) : (
        <div className="grid md:grid-cols-3 gap-4">
          {tables.map((table) => (
            <Table
              key={table._id}
              table={table}
              onSelect={handleTableSelection}
              selectedTime={selectedTime}
              busy={busyTableId === table._id}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TableSelection;
