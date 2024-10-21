from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests as grequests
from google.oauth2 import id_token
from motor.motor_asyncio import AsyncIOMotorClient
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

load_dotenv()  # Load variables from .env file

# FastAPI instance
app = FastAPI()

# Get MongoDB credentials from environment variables
MONGO_USERNAME = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME"))
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_CLUSTER_URL = os.getenv("MONGO_CLUSTER_URL")  # The cluster URL without credentials

# Construct the full MongoDB URI with escaped credentials
MONGO_DB_URL = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER_URL}/{MONGO_DB_NAME}?retryWrites=true&w=majority"

if not MONGO_DB_URL:
    raise EnvironmentError("MONGO_DB_URL environment variable not set")

client = AsyncIOMotorClient(MONGO_DB_URL)
db = client.restoDB  # Database

# Kafka producer setup
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(loop=loop, bootstrap_servers='localhost:9092')

# OAuth2 token URL (can be used in frontend to generate tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Google OAuth Client ID (Ensure GOOGLE_CLIENT_ID is set in environment variables)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_CLIENT_REDIRECT")
if not GOOGLE_CLIENT_ID:
    raise EnvironmentError("GOOGLE_CLIENT_ID environment variable not set")


# Pydantic model for the booking request
class BookingRequest(BaseModel):
    table_id: int
    datetime: str  # ISO datetime format is recommended
    
class User(BaseModel):
    email: str
    name: str
    picture: str


# Startup and Shutdown events for Kafka producer
@app.on_event("startup")
async def startup_event():
    await producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()


# Helper function to get user details from MongoDB
async def get_user(user_id: str):
    user = await db.users.find_one({"google_id": user_id})
    return user


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
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    # Request to exchange the code for access token
    token_response = requests.post(token_url, data=data)
    token_response_data = token_response.json()
    
    if "access_token" not in token_response_data:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")
    
    access_token = token_response_data["access_token"]
    
    # Fetch user info from Google API
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()
    
    if "email" not in user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    # Return or store user info
    user_data = User(
        email=user_info["email"],
        name=user_info["name"],
        picture=user_info["picture"],
    )
    
    # Here, you can store the user in the database if required

    return user_data

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
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Prepare the booking event
    booking_event = {
        "table_id": booking_request.table_id,
        "datetime": booking_request.datetime,
        "user_id": user["google_id"],
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
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    bookings = await db.bookings.find({"user_id": user["google_id"]}).to_list(length=100)
    return {"user": user, "bookings": bookings}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
