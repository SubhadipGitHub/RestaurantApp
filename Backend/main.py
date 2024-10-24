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
from pydantic import BaseModel, Field
import asyncio
from typing import List, Optional
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

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_CLIENT_REDIRECT")

# Models
class BookingModel(BaseModel):
    restaurant_id: str
    no_of_people: int
    time_slot: str  # e.g., "2024-10-23 18:00"
    booking_info: dict = {}
    customer_name: str
    customer_email: str

class BookingUpdateModel(BaseModel):
    status: Optional[str] = Field(None, pattern="^(PENDING|CONFIRMED|CANCELLED)$")
    table_id: Optional[str]
    order_info: Optional[dict]  # Update order items
    customer_name: Optional[str]
    customer_email: Optional[str]

class TableModel(BaseModel):
    restaurant_id: str
    seats: int
    status: str = Field(None, pattern="^(AVAILABLE|BLOCKED|OCCUPIED)$")
    booking_id: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
class User(BaseModel):
    email: str
    name: str
    picture: str

#Frontend config
FRONTEND_URL = os.getenv("FRONTEND_URL")

def generate_custom_id(prefix: str):
    """Generate a custom _id with a prefix and current Unix timestamp."""
    return f"{prefix}_{int(time.time())}"


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

@app.post("/bookings/")
async def create_booking(booking: BookingModel):
    try:
        available_table = await db.tables.find_one({
            "restaurant_id": booking.restaurant_id,
            "seats": {"$gte": booking.no_of_people},
            "status": "AVAILABLE"
        })

        if not available_table:
            raise HTTPException(status_code=404, detail="No available tables for the booking")

        booking_id = generate_custom_id("BOOKING")

        booking_data = {
            "_id": booking_id,
            "restaurant_id": booking.restaurant_id,
            "no_of_people": booking.no_of_people,
            "time_slot": booking.time_slot,
            "booking_info": booking.booking_info,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "status": "CONFIRMED",
            "table_id": available_table["_id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await db.bookings.insert_one(booking_data)

        # Update table to mark it as occupied and link booking ID
        await db.tables.update_one(
            {"_id": available_table["_id"]},
            {"$set": {
                "status": "OCCUPIED",
                "booking_id": booking_id,
                "updated_at": datetime.utcnow()
            }}
        )

        return {"message": "Booking confirmed", "booking_id": booking_id, "table_id": available_table["_id"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")
    

@app.put("/bookings/{booking_id}")
async def update_booking(booking_id: str, update_data: BookingUpdateModel):
    try:
        booking = await db.bookings.find_one({"_id": booking_id})

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        update_fields = {}

        # Update status if provided
        if update_data.status:
            update_fields["status"] = update_data.status
        
        # Update table_id if provided
        if update_data.table_id:
            update_fields["table_id"] = update_data.table_id

        # Update order_info if provided
        if update_data.order_info:
            if "order_info" in booking:
                booking["order_info"].update(update_data.order_info)
            else:
                booking["order_info"] = update_data.order_info
            update_fields["order_info"] = booking["order_info"]

        # Update customer_name and customer_email if provided
        if update_data.customer_name:
            update_fields["customer_name"] = update_data.customer_name
        if update_data.customer_email:
            update_fields["customer_email"] = update_data.customer_email

        # Update the timestamp
        update_fields["updated_at"] = datetime.utcnow()

        # Apply the update
        result = await db.bookings.update_one(
            {"_id": booking_id},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made to the booking")

        return {"message": "Booking updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating booking: {str(e)}")
    
# Clear table booking when booking is closed or cancelled
@app.put("/clear_table_booking/{booking_id}")
async def clear_table_booking(booking_id: str):
    try:
        # Find the booking first
        booking = await db.bookings.find_one({"_id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Find the associated table
        table = await db.tables.find_one({"_id": booking['table_id']})
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        # Clear the booking id from the table and set status to AVAILABLE
        result = await db.tables.update_one(
            {"_id": booking['table_id']},
            {"$set": {"status": "AVAILABLE", "booking_id": None, "updated_at": datetime.utcnow()}}
        )

        # Mark booking as closed or cancelled
        await db.bookings.update_one(
            {"_id": booking_id},
            {"$set": {"status": "CANCELLED", "updated_at": datetime.utcnow()}}
        )

        return {"message": "Booking cleared and table status set to AVAILABLE", "table": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Update table details by table ID
@app.put("/update_table/{table_id}")
async def update_table(table_id: str, status: Optional[str] = None, number_of_seats: Optional[int] = None):
    try:
        # Prepare the update fields
        update_fields = {}
        if status:
            if status not in ["AVAILABLE", "BLOCKED"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            update_fields["status"] = status
        if number_of_seats:
            update_fields["seats"] = number_of_seats
        
        update_fields["updated_at"] = datetime.utcnow()  # Keep track of update time

        # Update the table in the database
        update_result = await db.tables.update_one(
            {"_id": table_id},
            {"$set": update_fields}
        )

        # Check if the table was found
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Table not found")

        # Check if the table was actually modified
        if update_result.modified_count == 0:
            return {"message": "No changes made to the table data."}

        # Optionally, fetch the updated table details if needed
        updated_table = await db.tables.find_one({"_id": table_id})

        return {
            "message": "Table updated successfully",
            "table": updated_table  # This will return the updated document
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tables/")
async def create_table(table: TableModel):
    try:
        table_id = generate_custom_id("TABLE")

        table_data = {
            "_id": table_id,
            "restaurant_id": table.restaurant_id,
            "seats": table.seats,
            "status": "AVAILABLE",  # Default new tables as available
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await db.tables.insert_one(table_data)

        return {"message": "Table created successfully", "table_id": table_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating table: {str(e)}")

@app.get("/tables/")
async def get_tables(restaurant_id: str):
    try:
        tables = await db.tables.find({"restaurant_id": restaurant_id}).to_list(100)

        if not tables:
            raise HTTPException(status_code=404, detail="No tables found for the restaurant")

        return {"tables": tables}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
