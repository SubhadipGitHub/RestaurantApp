# RestaurantApp🏨 Restaurant Table Booking App
A full-stack application for booking restaurant tables, allowing users to see the layout of the restaurant, select available tables for booking, and manage their bookings through an integrated authentication system using Google OAuth. The backend is built with FastAPI, MongoDB Atlas, and Kafka for event streaming.

🖥️ Demo
You can view the demo of the web application here: Demo Link


📖 Table of Contents
Features
Tech Stack
Project Structure
Frontend Setup
Backend Setup
Usage
Environment Variables
Contributing
License
✨ Features
Visual table layout for booking
Google OAuth-based authentication
MongoDB Atlas integration for user and booking data
Real-time Kafka streaming for handling events
Profile page showing user's booking history
Date and time picker for booking
Backend session validation using Google token
🛠️ Tech Stack
Frontend: React, Google OAuth

Backend: FastAPI, MongoDB Atlas, Kafka

📂 Project Structure
Frontend (React)
bash
Copy code
/client
├── public
│   ├── index.html
│   └── manifest.json
├── src
│   ├── components
│   │   ├── BookingLayout.js       # Renders restaurant layout and tables
│   │   ├── Table.js               # Individual table component
│   │   ├── DateTimePicker.js      # DateTime picker component
│   │   ├── BookingConfirmation.js # Handles booking confirmation
│   │   └── Profile.js             # Displays user profile and booking history
│   ├── context
│   │   └── AuthContext.js         # Manages Google OAuth authentication
│   ├── api
│   │   └── booking.js             # API calls for booking and user data
│   ├── App.js                     # Main entry point for React components
│   └── index.js                   # ReactDOM render
├── .env                           # Environment variables for React
└── package.json                   # Dependencies and scripts
Backend (FastAPI)
bash
Copy code
/server
├── app
│   ├── main.py                    # Entry point of FastAPI server
│   ├── auth.py                    # Handles Google OAuth authentication
│   ├── models.py                  # MongoDB data models (User, Booking)
│   ├── routes
│   │   ├── booking.py             # Booking-related routes
│   │   └── user.py                # User-related routes (profile, authentication)
│   ├── services
│   │   └── kafka_producer.py       # Kafka producer for event streaming
│   └── utils.py                   # Helper functions for Google token verification
├── .env                           # Environment variables for FastAPI
└── requirements.txt               # Python dependencies
🚀 Frontend Setup
Prerequisites
Node.js installed
Google OAuth credentials (Client ID)
Steps to Set Up the Frontend
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/restaurant-booking-app.git
cd restaurant-booking-app/client
Install dependencies:

bash
Copy code
npm install
Create .env file in the root of the client directory and add the following:

env
Copy code
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_BACKEND_URL=http://localhost:8000
Start the development server:

bash
Copy code
npm start
Access the app: Open http://localhost:3000 in your browser.

⚙️ Backend Setup
Prerequisites
Python 3.7+
MongoDB Atlas account and cluster
Kafka installed (or use a cloud-based Kafka service)
Steps to Set Up the Backend
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/restaurant-booking-app.git
cd restaurant-booking-app/server
Create a virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Create .env file in the root of the server directory and add the following:

env
Copy code
MONGO_URI=your-mongo-atlas-uri
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAFKA_SERVER=localhost:9092
SECRET_KEY=your-random-secret-key
Run the FastAPI server:

bash
Copy code
uvicorn app.main:app --reload
Access API docs: Visit http://localhost:8000/docs to view interactive API documentation.

🔄 Usage
Google OAuth Login
Users can log in using their Google account. The token received from Google will be verified by the FastAPI backend, and the user profile will be stored in MongoDB.

Booking a Table
Select an available table from the visual layout.
Choose a date and time using the date-time picker.
Confirm the booking.
The booking details will be saved and associated with the user's profile.
Viewing Bookings
After logging in, users can view their booking history from the Profile section.
The profile data is fetched from the MongoDB database.
🔐 Environment Variables
To run this project, you will need the following environment variables set in both client/.env and server/.env:

Frontend (client/.env):

env
Copy code
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_BACKEND_URL=http://localhost:8000
Backend (server/.env):

env
Copy code
MONGO_URI=your-mongo-atlas-uri
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAFKA_SERVER=localhost:9092
SECRET_KEY=your-random-secret-key
🤝 Contributing
Contributions, issues, and feature requests are welcome!

Feel free to check the issues page. If you want to contribute, please fork the repository and submit a pull request.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
