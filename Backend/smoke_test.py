"""Offline smoke test for the API's auth and hardening behaviour.

Runs the app in-process against a TestClient. No live database is needed --
every assertion here is about request handling, not persistence.

    python smoke_test.py

Exits non-zero if anything regresses, so it is safe to wire into CI later.
"""

import os
import sys

# Values only need to be well-formed; nothing here dials the database.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "restoDB")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
    "GOOGLE_CLIENT_REDIRECT", "http://localhost:3000/api/backend/auth/google"
)
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("ENABLE_DOCS", "false")

from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402

import auth  # noqa: E402
import main  # noqa: E402

failures = []


def check(label, condition, extra=""):
    status = "PASS" if condition else "FAIL"
    if not condition:
        failures.append(label)
    print(f"{status}  {label}" + (f"   [{extra}]" if extra else ""))


def run():
    with TestClient(main.app) as c:
        r = c.get("/health")
        check("/health returns 200", r.status_code == 200)
        check(
            "responses are not cacheable",
            r.headers.get("cache-control") == "no-store",
            r.headers.get("cache-control"),
        )

        check("/docs is gated off", c.get("/docs").status_code == 404)
        check("/openapi.json is gated off", c.get("/openapi.json").status_code == 404)

        # Every business endpoint must reject an anonymous caller.
        anon = [
            ("GET /me", c.get("/me")),
            (
                "POST /bookings",
                c.post(
                    "/bookings",
                    json={
                        "restaurant_id": "REST_001",
                        "no_of_people": 2,
                        "time_slot": "2026-01-01 19:00",
                    },
                ),
            ),
            ("POST /tables", c.post("/tables", json={"restaurant_id": "REST_001", "seats": 4})),
            ("PUT /update_table", c.put("/update_table/TABLE_x?status=BLOCKED")),
            ("PUT /bookings/{id}", c.put("/bookings/B_1", json={"status": "CANCELLED"})),
            ("PUT /clear_table_booking/{id}", c.put("/clear_table_booking/B_1")),
        ]
        for label, resp in anon:
            check(f"{label} rejects anonymous callers", resp.status_code == 401,
                  resp.status_code)

        r = c.get("/login/google", follow_redirects=False)
        location = r.headers.get("location", "")
        check("/login/google redirects to Google",
              r.status_code in (302, 307)
              and location.startswith("https://accounts.google.com/"))
        check("authorize URL carries a state parameter", "state=" in location)
        check("state is stored in a cookie", "oauth_state" in r.cookies)

        # OAuth CSRF: a callback whose state does not match the cookie is refused.
        c.cookies.clear()
        r = c.get("/auth/google?code=abc&state=attacker", follow_redirects=False)
        check(
            "callback with mismatched state is refused",
            r.status_code in (302, 307)
            and "/login?error=" in r.headers.get("location", ""),
        )

        c.cookies.clear()
        token = auth.create_session_token(
            email="a@b.com", name="Ann", picture="p", uid="USER_1"
        )
        r = c.get("/me", cookies={"session": token})
        check("a valid session is accepted", r.status_code == 200)
        check(
            "/me reports the session's identity",
            r.status_code == 200 and r.json().get("email") == "a@b.com",
        )

        forged = jwt.encode({"sub": "a@b.com"}, "wrong-key", algorithm="HS256")
        check(
            "a token signed with the wrong key is refused",
            c.get("/me", cookies={"session": forged}).status_code == 401,
        )

        r = c.post("/logout")
        check(
            "/logout clears the session cookie",
            r.status_code == 200 and "session=" in r.headers.get("set-cookie", ""),
        )


if __name__ == "__main__":
    run()
    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All checks passed.")
