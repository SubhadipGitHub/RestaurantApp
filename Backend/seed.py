"""Create a restaurant's initial tables.

A fresh Atlas database leaves the app inert: the dashboard has no tables to
show and a booking cannot find one to claim. This fills that gap once.

Idempotent -- if the restaurant already has tables, it reports and exits
without touching them.

    python seed.py                       # 6 tables, 4 seats, restaurant tst1
    python seed.py --restaurant-id r2 --count 10 --seats 2
"""

import argparse
import asyncio
import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

import config


async def seed(restaurant_id: str, count: int, seats: int) -> None:
    client = AsyncIOMotorClient(config.MONGO_DB_URL)
    db = client[config.MONGO_DB_NAME]

    existing = await db.tables.count_documents({"restaurant_id": restaurant_id})
    if existing:
        print(
            f"Restaurant {restaurant_id!r} already has {existing} table(s); "
            f"leaving them alone."
        )
        client.close()
        return

    now = datetime.utcnow()
    tables = [
        {
            "_id": f"TABLE_{uuid.uuid4().hex}",
            "restaurant_id": restaurant_id,
            "label": f"T{i}",
            "seats": seats,
            "status": "AVAILABLE",
            "booking_id": None,
            "created_at": now,
            "updated_at": now,
        }
        for i in range(1, count + 1)
    ]

    await db.tables.insert_many(tables)
    print(f"Created {len(tables)} table(s) for restaurant {restaurant_id!r}.")
    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restaurant-id", default="tst1")
    parser.add_argument("--count", type=int, default=6)
    parser.add_argument("--seats", type=int, default=4)
    args = parser.parse_args()

    asyncio.run(seed(args.restaurant_id, args.count, args.seats))


if __name__ == "__main__":
    main()
