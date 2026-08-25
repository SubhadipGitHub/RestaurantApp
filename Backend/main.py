import logging
import secrets
import uuid
from contextlib import asynccontextmanager
from urllib.parse import quote
from datetime import datetime
from typing import Optional

import httpx
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

import config
from auth import (
    SessionUser,
    clear_session_cookie,
    create_session_token,
    get_current_user,
    set_session_cookie,
)

logger = logging.getLogger("restaurantapp")
logging.basicConfig(level=logging.INFO)

mongo_client = None
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the Mongo connection on startup rather than at import.

    Constructing AsyncIOMotorClient with a mongodb+srv:// URI performs a
    blocking DNS SRV lookup. Doing that at import time means a transient DNS
    failure crash-loops the container, and it makes the module impossible to
    import without a live cluster. Endpoints read the module-level `db` at call
    time, so binding it here is enough.
    """
    global mongo_client, db
    mongo_client = AsyncIOMotorClient(config.MONGO_DB_URL)
    db = mongo_client[config.MONGO_DB_NAME]
    logger.info("Connected to MongoDB database %s", config.MONGO_DB_NAME)
    try:
        yield
    finally:
        mongo_client.close()


app = FastAPI(
    title="RestaurantApp API",
    lifespan=lifespan,
    docs_url="/docs" if config.ENABLE_DOCS else None,
    redoc_url="/redoc" if config.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if config.ENABLE_DOCS else None,
)

# In production the browser reaches this API through a same-origin Next.js
# rewrite, so CORS is not load-bearing. It is kept narrow for local development
# and direct API clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI's default slash handling answers /tables with a 307 whose Location is
# the *absolute* upstream URL. Behind the frontend's same-origin rewrite that
# would bounce the browser onto the backend host, dropping the first-party
# session cookie. Route paths are declared without trailing slashes and the
# redirect behaviour is switched off so it can never fire.
app.router.redirect_slashes = False


@app.middleware("http")
async def no_store(request: Request, call_next):
    """Never let an authenticated response be cached.

    Vercel may cache external-rewrite responses, which for this API would risk
    serving one user's session-scoped data to another.
    """
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response





# Models
class BookingModel(BaseModel):
    restaurant_id: str
    no_of_people: int
    time_slot: str  # e.g., "2024-10-23 18:00"
    booking_info: dict = {}
    # Optional: claim one specific table rather than any table that fits.
    table_id: Optional[str] = None
    # customer_name / customer_email are deliberately absent -- identity comes
    # from the verified session, never from the request body.


class BookingUpdateModel(BaseModel):
    status: Optional[str] = Field(None, pattern="^(PENDING|CONFIRMED|CANCELLED)$")
    table_id: Optional[str] = None
    order_info: Optional[dict] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None


class TableModel(BaseModel):
    restaurant_id: str
    seats: int
    label: Optional[str] = None
    status: str = Field(None, pattern="^(AVAILABLE|BLOCKED|OCCUPIED)$")
    booking_id: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    email: str
    name: str
    picture: str


def generate_custom_id(prefix: str) -> str:
    """Generate a collision-free custom _id with a readable prefix.

    The previous implementation used a whole-second Unix timestamp, so two
    documents created in the same second collided on _id and the insert failed.
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def _server_error(message: str, exc: Exception) -> HTTPException:
    """Log the real cause, return an opaque message.

    Exception text here can contain the Mongo connection string, so it must not
    reach the client.
    """
    logger.exception("%s: %s", message, exc)
    return HTTPException(status_code=500, detail=message)


# Helper function to get user from MongoDB
async def get_user_by_email(email: str):
    return await db.users.find_one({"email": email})


# Helper function to create or update user
async def create_or_update_user(user_data: dict):
    try:
        user = await db.users.find_one({"email": user_data["email"]})

        if user:
            await db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {"last_login": datetime.utcnow()}},
            )
            logger.info("user %s logged in", user_data["email"])
            return {"id": user["_id"], "status": "updated"}

        user_id = generate_custom_id("USER")
        user_data["_id"] = user_id
        user_data["created_at"] = datetime.utcnow()
        user_data["last_login"] = datetime.utcnow()
        insert_result = await db.users.insert_one(user_data)

        if insert_result.inserted_id:
            logger.info("user %s created", user_data["email"])
            return {"id": user_id, "status": "inserted"}

        return {"status": "error", "message": "User creation failed"}
    except Exception as e:
        logger.exception("create_or_update_user failed: %s", e)
        return {"status": "error", "message": "User persistence failed"}


@app.get("/health")
async def health():
    """Liveness probe. Deliberately does not touch the database."""
    return {"status": "ok"}


OAUTH_STATE_COOKIE = "oauth_state"


@app.get("/login/google")
async def login_google():
    """Send the user to Google's consent screen.

    A random `state` is minted here and echoed back by Google, which is what
    stops a third party from feeding us their own authorization code.
    """
    state = secrets.token_urlsafe(32)
    url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code&client_id={config.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={config.GOOGLE_REDIRECT_URI}"
        f"&state={state}"
        "&scope=openid%20profile%20email"
    )
    response = RedirectResponse(url)
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        max_age=600,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return response


def _auth_error_redirect(message: str) -> RedirectResponse:
    return RedirectResponse(
        f"{config.FRONTEND_URL}/login?error={quote(message)}"
    )


@app.get("/auth/google")
async def auth_google(
    code: str = "",
    state: str = "",
    oauth_state: Optional[str] = Cookie(None),
):
    """Google OAuth2 callback.

    Exchanges the authorization code, upserts the user, then issues our own
    session cookie. Neither the Google access token nor the user record is put
    in the redirect URL any more -- that leaked both into browser history,
    Referer headers, and proxy logs.
    """
    if not code:
        raise HTTPException(
            status_code=400, detail="Authorization code is missing or invalid"
        )

    if not state or not oauth_state or not secrets.compare_digest(state, oauth_state):
        logger.warning("OAuth state mismatch on callback")
        return _auth_error_redirect("Sign-in failed. Please try again.")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    # httpx, not requests: these run inside an async handler and a synchronous
    # client would block the event loop for the whole round trip to Google.
    async with httpx.AsyncClient(timeout=10) as http:
        try:
            token_response = await http.post(token_url, data=data)
            token_response.raise_for_status()
            token_response_data = token_response.json()
        except httpx.HTTPError as e:
            logger.exception("Google token exchange failed: %s", e)
            return _auth_error_redirect("Sign-in failed. Please try again.")

        access_token = token_response_data.get("access_token")
        if not access_token:
            logger.error("Google token response contained no access_token")
            return _auth_error_redirect("Sign-in failed. Please try again.")

        try:
            user_info_response = await http.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        except httpx.HTTPError as e:
            logger.exception("Google userinfo request failed: %s", e)
            return _auth_error_redirect("Could not read your Google profile.")

    if "email" not in user_info:
        return _auth_error_redirect("Could not read your Google profile.")

    user_data = {
        "email": user_info["email"],
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
    }

    result = await create_or_update_user(dict(user_data))
    if result.get("status") == "error":
        return _auth_error_redirect("Could not save your profile.")

    token = create_session_token(
        email=user_data["email"],
        name=user_data["name"],
        picture=user_data["picture"],
        uid=str(result.get("id", "")),
    )

    response = RedirectResponse(f"{config.FRONTEND_URL}/dashboard")
    set_session_cookie(response, token)
    response.delete_cookie(OAUTH_STATE_COOKIE, path="/")
    return response


@app.get("/me")
async def me(current_user: SessionUser = Depends(get_current_user)):
    """Who am I? Backs the frontend's auth state with a real server check."""
    return current_user.as_dict()


@app.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    clear_session_cookie(response)
    return response


@app.post("/bookings")
async def create_booking(
    booking: BookingModel,
    current_user: SessionUser = Depends(get_current_user),
):
    try:
        booking_id = generate_custom_id("BOOKING")

        # Claim the table in a single atomic operation. A find-then-update pair
        # lets two concurrent requests both see the same AVAILABLE table and
        # both book it; find_one_and_update makes the claim the point of
        # serialisation, so the loser gets nothing back and is told to retry.
        claim_filter = {
            "restaurant_id": booking.restaurant_id,
            "seats": {"$gte": booking.no_of_people},
            "status": "AVAILABLE",
        }
        if booking.table_id:
            claim_filter["_id"] = booking.table_id

        available_table = await db.tables.find_one_and_update(
            claim_filter,
            {
                "$set": {
                    "status": "OCCUPIED",
                    "booking_id": booking_id,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if not available_table:
            raise HTTPException(
                status_code=409, detail="No available tables for the booking"
            )

        booking_data = {
            "_id": booking_id,
            "restaurant_id": booking.restaurant_id,
            "no_of_people": booking.no_of_people,
            "time_slot": booking.time_slot,
            "booking_info": booking.booking_info,
            # The booking always belongs to the authenticated caller; the
            # client does not get to nominate someone else.
            "customer_name": current_user.name,
            "customer_email": current_user.email,
            "status": "CONFIRMED",
            "table_id": available_table["_id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await db.bookings.insert_one(booking_data)

        return {
            "message": "Booking confirmed",
            "booking_id": booking_id,
            "table_id": available_table["_id"],
        }

    except HTTPException:
        # Must precede the generic handler, otherwise intended 4xx responses
        # get swallowed and re-raised as 500s.
        raise
    except Exception as e:
        raise _server_error("Error creating booking", e)


@app.get("/bookings")
async def list_my_bookings(current_user: SessionUser = Depends(get_current_user)):
    """The caller's own bookings, most recent first."""
    try:
        bookings = (
            await db.bookings.find({"customer_email": current_user.email})
            .sort("created_at", -1)
            .to_list(100)
        )
        return {"bookings": bookings}
    except Exception as e:
        raise _server_error("Error fetching bookings", e)


@app.put("/bookings/{booking_id}")
async def update_booking(
    booking_id: str,
    update_data: BookingUpdateModel,
    current_user: SessionUser = Depends(get_current_user),
):
    try:
        booking = await db.bookings.find_one({"_id": booking_id})

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.get("customer_email") != current_user.email:
            raise HTTPException(status_code=403, detail="Not your booking")

        update_fields = {}

        if update_data.status:
            update_fields["status"] = update_data.status

        if update_data.table_id:
            update_fields["table_id"] = update_data.table_id

        if update_data.order_info:
            merged = dict(booking.get("order_info") or {})
            merged.update(update_data.order_info)
            update_fields["order_info"] = merged

        update_fields["updated_at"] = datetime.utcnow()

        result = await db.bookings.update_one(
            {"_id": booking_id}, {"$set": update_fields}
        )

        if result.modified_count == 0:
            return {"message": "No changes made to the booking"}

        return {"message": "Booking updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise _server_error("Error updating booking", e)


@app.put("/clear_table_booking/{booking_id}")
async def clear_table_booking(
    booking_id: str,
    current_user: SessionUser = Depends(get_current_user),
):
    """Cancel a booking and release its table."""
    try:
        booking = await db.bookings.find_one({"_id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.get("customer_email") != current_user.email:
            raise HTTPException(status_code=403, detail="Not your booking")

        table = await db.tables.find_one({"_id": booking["table_id"]})
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        await db.tables.update_one(
            {"_id": booking["table_id"]},
            {
                "$set": {
                    "status": "AVAILABLE",
                    "booking_id": None,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        await db.bookings.update_one(
            {"_id": booking_id},
            {"$set": {"status": "CANCELLED", "updated_at": datetime.utcnow()}},
        )

        return {"message": "Booking cleared and table status set to AVAILABLE"}

    except HTTPException:
        raise
    except Exception as e:
        raise _server_error("Error clearing booking", e)


@app.put("/update_table/{table_id}")
async def update_table(
    table_id: str,
    status: Optional[str] = None,
    number_of_seats: Optional[int] = None,
    current_user: SessionUser = Depends(get_current_user),
):
    try:
        update_fields = {}
        if status:
            if status not in ["AVAILABLE", "BLOCKED"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            update_fields["status"] = status
        if number_of_seats:
            update_fields["seats"] = number_of_seats

        update_fields["updated_at"] = datetime.utcnow()

        update_result = await db.tables.update_one(
            {"_id": table_id}, {"$set": update_fields}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Table not found")

        if update_result.modified_count == 0:
            return {"message": "No changes made to the table data."}

        updated_table = await db.tables.find_one({"_id": table_id})

        return {"message": "Table updated successfully", "table": updated_table}

    except HTTPException:
        raise
    except Exception as e:
        raise _server_error("Error updating table", e)


@app.post("/tables")
async def create_table(
    table: TableModel,
    current_user: SessionUser = Depends(get_current_user),
):
    try:
        table_id = generate_custom_id("TABLE")

        table_data = {
            "_id": table_id,
            "restaurant_id": table.restaurant_id,
            "label": table.label,
            "seats": table.seats,
            "status": "AVAILABLE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await db.tables.insert_one(table_data)

        return {"message": "Table created successfully", "table_id": table_id}

    except Exception as e:
        raise _server_error("Error creating table", e)


@app.get("/tables")
async def get_tables(restaurant_id: str):
    """List a restaurant's tables.

    Readable without a session so the layout can be shown before sign-in.
    An empty restaurant is an empty list, not a 404.
    """
    try:
        tables = await db.tables.find({"restaurant_id": restaurant_id}).to_list(100)
        return {"tables": tables}
    except Exception as e:
        raise _server_error("Error fetching tables", e)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
