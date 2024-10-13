# 🏨 Restaurant Table Booking App

A full-stack, scalable application that allows customers to visualize a restaurant's layout, select available tables for booking, and manage their bookings. Includes features like Google OAuth-based authentication, MongoDB integration for data storage, and Kafka for real-time event streaming.

## 📖 Table of Contents

Overview
Features
Tech Stack
Architecture Diagram
Flow Diagram
Project Structure
Frontend Setup
Backend Setup
Database Schema
Usage
Environment Variables
Contributing
License

## 📋 Overview

The Restaurant Table Booking App provides a seamless booking experience for customers. The application enables users to:

View the layout of the restaurant.
Select and book available tables for a specific date and time.
Manage their bookings via an authenticated user profile.
Real-time notifications and events through Kafka.

## ✨ Features

Visual Table Layout: Customers can see which tables are available and book them.
Date and Time Picker: Select tables for specific time slots.
Google OAuth: Secure login system using Google Authentication.
Profile Management: Users can view their booking history and profile information.
MongoDB Atlas Integration: Stores user and booking data.
Kafka Integration: Real-time streaming of booking events.

## 🛠️ Tech Stack

### Frontend:
React: Frontend library for building user interfaces.
Google OAuth: Authentication mechanism.
Axios: For API calls.

### Backend:
FastAPI: Python-based web framework.
MongoDB Atlas: Cloud database for storing user and booking data.
Kafka: Streaming platform for event handling.

## 🗺️ Architecture Diagram

Architecture Overview:

Frontend (React) communicates with Backend (FastAPI).
Backend interacts with MongoDB for storing user and booking data.
Kafka handles event streaming.
Google OAuth is used for secure login and session handling.

## 📊 Flow Diagram

Booking Flow:

User logs in via Google OAuth.
User views the restaurant layout and selects a table.
Date and time for booking are selected.
Upon confirmation, booking details are stored in MongoDB.
Kafka streams booking events for real-time updates.

## 📂 Project Structure

### Frontend (React)

/client
├── public
│   ├── index.html
│   └── manifest.json
├── src
│   ├── components
│   │   ├── BookingLayout.js        # Layout and table view
│   │   ├── Table.js                # Table component
│   │   ├── DateTimePicker.js       # DateTime picker component
│   │   ├── BookingConfirmation.js  # Booking confirmation modal
│   │   └── Profile.js              # User profile and booking history
│   ├── api
│   │   └── booking.js              # API calls for booking
│   ├── context
│   │   └── AuthContext.js          # Authentication management with Google OAuth
│   ├── App.js                      # Main app component
│   └── index.js                    # ReactDOM render
├── .env                             # Environment variables
└── package.json                     # Project dependencies

### Backend (FastAPI)

/server
├── app
│   ├── main.py                      # FastAPI app entry point
│   ├── auth.py                      # Google OAuth logic
│   ├── models.py                    # MongoDB schema (User, Booking)
│   ├── routes
│   │   ├── booking.py               # Booking routes
│   │   └── user.py                  # User profile routes
│   ├── services
│   │   └── kafka_producer.py        # Kafka event producer
│   └── utils.py                     # Helper functions (Google token verification)
├── .env                              # Environment variables
└── requirements.txt                  # Python dependencies

⚙️ Frontend Setup

## Prerequisites
Node.js installed.
Google OAuth credentials (Client ID and Secret).
Installation Steps
Clone the repository:

`
git clone https://github.com/yourusername/restaurant-booking-app.git
cd restaurant-booking-app/client
`
## Install dependencies:

`
npm install
Create .env file in the root of the client directory and add:
`
env
`
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_BACKEND_URL=http://localhost:8000
`

## Run the development server:

`
npm start
`
Access the app: Visit http://localhost:3000 in your browser.

## ⚙️ Backend Setup

Prerequisites
Python 3.7+
MongoDB Atlas account

Kafka installed locally or through a cloud service.

## Installation Steps
Clone the repository:

`
git clone https://github.com/yourusername/restaurant-booking-app.git
cd restaurant-booking-app/server
`

Create a virtual environment:

`
python3 -m venv venv
source venv/bin/activate
`

Install dependencies:

`
pip install -r requirements.txt
`

Create .env file in the root of the server directory:

env
`
MONGO_URI=your-mongo-atlas-uri
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAFKA_SERVER=localhost:9092
SECRET_KEY=your-random-secret-key
`

Run the FastAPI server:

`
uvicorn app.main:app --reload4
`

Access API documentation: Visit http://localhost:8000/docs for interactive API documentation.

## 🗃️ Database Schema

User Collection:
json
`
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "google_id": "string",
  "bookings": [
    {
      "table_id": "string",
      "date": "datetime",
      "time": "string"
    }
  ]
}
`

Booking Collection:
json
`
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "table_id": "string",
  "date": "datetime",
  "time": "string"
}
`

## 🛠️ Usage

Google OAuth: Users log in through Google, and the OAuth token is verified by the backend.
Table Booking: After logging in, users can select tables, pick a time, and confirm bookings.
Profile Management: Users can view and manage their bookings in the profile section.
Kafka Streaming: Booking events are handled in real-time using Kafka.

## 🔐 Environment Variables
To run this project, you will need to set the following environment variables in both client/.env and server/.env:

### Frontend (client/.env):

env
`
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_BACKEND_URL=http://localhost:8000
`

### Backend (server/.env):

env
`
MONGO_URI=your-mongo-atlas-uri
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAFKA_SERVER=localhost:9092
SECRET_KEY=your-random-secret-key
`

## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to contribute to this project:

Fork the repository.
Create your feature branch (git checkout -b feature/YourFeature).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/YourFeature).
Open a pull request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact
For any queries, feel free to reach out to the project maintainer: subhadip.dutta.18@gmail.com
