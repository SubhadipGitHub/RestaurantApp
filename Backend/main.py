from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests as grequests
from google.oauth2 import id_token
from motor.motor_asyncio import AsyncIOMotorClient
import time
from datetime import datetime
import os
import json
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer
import asyncio
from bson import ObjectId
from dotenv import load_dotenv
import urllib.parse
from jose import jwt, JWTError
import requests

load_dotenv()

app = FastAPI()

# MongoDB configuration
MONGO_USERNAME = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME"))
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_CLUSTER_URL = os.getenv("MONGO_CLUSTER_URL")

MONGO_DB_URL = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER_URL}/{MONGO_DB_NAME}?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_DB_URL)
db = client.restoDB  # Database

# Kafka producer setup
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(loop=loop, bootstrap_servers='localhost:9092')

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_CLIENT_REDIRECT")

# Models
class BookingRequest(BaseModel):
    table_id: int
    datetime: str  # ISO datetime format is recommended
    
class User(BaseModel):
    email: str
    name: str
    picture: str

#Frontend config
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Kafka startup/shutdown events
@app.on_event("startup")
async def startup_event():
    await producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()


# Helper function to get user from MongoDB
async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    return user

# Helper function to create or update user
async def create_or_update_user(user_data: dict):
    print("scope for create or update user info")
    try:
        user = await db.users.find_one({"email": user_data["email"]})

        if user:
            # Update the last login time
            result = await db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {"token": user_data["token"], "last_login": datetime.utcnow()}}
            )

            if result.modified_count > 0:
                print(f"user {user_data['email']} updated during authorization")
                return {"id": user["_id"], "status": "updated"}
            else:
                print(f"no changes made for user {user_data['email']}")
                return {"id": user["_id"], "status": "no change"}
        else:
            # Generate a custom unique user ID with prefix "USER - " and Unix timestamp
            current_unix_time = int(time.time())  # Get current time in Unix timestamp
            # Create a new user with created_at and last_login timestamps
            user_data["_id"] = f"USER - {current_unix_time}"
            user_data["created_at"] = datetime.utcnow()
            user_data["last_login"] = datetime.utcnow()
            insert_result = await db.users.insert_one(user_data)

            if insert_result.inserted_id:
                print("user created during authorization")
                return {"id": f"USER - {current_unix_time}", "status": "inserted"}
            else:
                print("user creation failed")
                return {"status": "error", "message": "User creation failed"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": str(e)}



@app.get("/login/google")
async def login_google():
    """
    This will redirect the user to Google’s OAuth2 consent screen.
    """
    url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20profile%20email&access_type=offline"
    )
    return {"url": url}


@app.get("/auth/google")
async def auth_google(code: str):
    """
    This endpoint is the callback for Google OAuth2. It exchanges the authorization code for an access token
    and fetches the user's profile information.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing or invalid")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        token_response = requests.post(token_url, data=data)
        token_response.raise_for_status()
        token_response_data = token_response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"Token request failed: {str(e)}"
        return RedirectResponse(f"{FRONTEND_URL}/auth/callback?error={json.dumps(error_message)}")

    access_token = token_response_data.get("access_token")
    if not access_token:
        error_message = "Failed to obtain access token"
        return RedirectResponse(f"{FRONTEND_URL}/auth/callback?error={json.dumps(error_message)}")

    try:
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"User info request failed: {str(e)}"
        return RedirectResponse(f"{FRONTEND_URL}/auth/callback?error={json.dumps(error_message)}")

    if "email" not in user_info:
        error_message = "Failed to fetch user info"
        return RedirectResponse(f"{FRONTEND_URL}/auth/callback?error={json.dumps(error_message)}")

    # Prepare user data
    user_data = {
        "email": user_info["email"],
        "name": user_info["name"],
        "picture": user_info["picture"],
        "token": access_token,
        "message": "User successfully logged in"
    }

    try:
        # Create or update user in MongoDB
        result = await create_or_update_user(user_data)

        # Check if user creation or update was successful
        if result.get("status") == "inserted":
            user_data["id"] = result.get("id")
            user_data["status"] = "User created successfully."
        elif result.get("status") == "updated":
            user_data["id"] = result.get("id")
            user_data["status"] = "User updated successfully."
        else:
            user_data["id"] = result.get("id")
            user_data["status"] = "No changes made or user already exists."

    except Exception as e:
        error_message = f"An error occurred while creating/updating user: {str(e)}"
        return RedirectResponse(f"{FRONTEND_URL}/auth/callback?error={json.dumps(error_message)}")

    # Redirect the user back to the frontend with the user data
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?user={json.dumps(user_data)}")


@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    """
    Verifies the token passed and decodes it.
    """
    try:
        payload = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


# Endpoint to handle table booking and store the booking data in MongoDB
@app.post("/book_table/")
async def book_table(booking_request: BookingRequest, user_id: str, token: str = Depends(oauth2_scheme)):
    user = await get_user_by_email(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Prepare the booking event
    booking_event = {
        "table_id": booking_request.table_id,
        "datetime": booking_request.datetime,
        "user_id": user["_id"],
        "user_name": user["name"]
    }
    
    # Store booking in MongoDB
    await db.bookings.insert_one(booking_event)

    # Send the booking event to Kafka topic
    await producer.send_and_wait("booking_events", json.dumps(booking_event).encode("utf-8"))

    return {"status": "Booking confirmed", "table_id": booking_request.table_id, "datetime": booking_request.datetime}


# Endpoint to fetch all bookings made by a user
@app.get("/user/{user_id}/bookings/")
async def get_user_bookings(user_id: str, token: str = Depends(oauth2_scheme)):
    user = await get_user_by_email(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    bookings = await db.bookings.find({"user_id": user["_id"]}).to_list(length=100)
    return {"user": user, "bookings": bookings}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
