"use client";
import { useState, useEffect } from "react";
import { QRCode } from 'react-qr-code'; // Importing react-qr-code
import { useSearchParams } from 'next/navigation';
import { FaFacebookF, FaTwitter, FaInstagram, FaPrint } from 'react-icons/fa'; // Importing social icons

const Customer = () => {
  const [tableUrl, setTableUrl] = useState("");
  const searchParams = useSearchParams();
  const tableId = searchParams.get('tableId');

  useEffect(() => {
    if (tableId) {
      const url = `${window.location.origin}/table/${tableId}`;
      setTableUrl(url);
    }
  }, [tableId]);

  // Function to print the QR card
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="bg-white shadow-md rounded-lg p-6 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-4">Restaurant Name</h1>
        <img
          src="/path/to/your/booking-image.jpg" // Replace with your image path
          alt="Online Booking"
          className="w-full h-48 object-cover rounded-md mb-4"
        />
        <h2 className="text-xl font-semibold text-center mb-2">Scan to View Table {tableId} Details</h2>
        {tableUrl ? (
          <div className="flex justify-center mb-4">
            <QRCode value={tableUrl} size={256} fgColor="#000000" />
          </div>
        ) : (
          <p className="text-center">Loading QR code...</p>
        )}
        <p className="mt-4 text-lg text-center">Scan the QR code to view the table details.</p>

        <div className="flex justify-center space-x-4 mt-4">
          <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-600">
            <FaFacebookF size={24} />
          </a>
          <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-400">
            <FaTwitter size={24} />
          </a>
          <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-pink-500">
            <FaInstagram size={24} />
          </a>
        </div>

        <button
          onClick={handlePrint}
          className="mt-4 w-full bg-blue-600 text-white font-semibold py-2 rounded-md hover:bg-blue-500 transition duration-200"
        >
          <FaPrint className="inline mr-2" /> Print QR Card
        </button>
      </div>
    </div>
  );
}

export default Customer;
