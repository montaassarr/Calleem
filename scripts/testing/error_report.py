#!/usr/bin/env python3
"""Utility script to inspect recent backend/frontend errors."""

import argparse
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from backend.database.mongo_config import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
)


async def fetch_documents(collection, limit: int, since: Optional[datetime]):
    query = {}
    if since:
        query["timestamp"] = {"$gte": since}
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


def format_doc(doc):
    timestamp = doc.get("timestamp")
    if timestamp:
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    level = doc.get("level", doc.get("metric", "info"))
    message = doc.get("error_message") or doc.get("message") or doc.get("action")
    return f"[{timestamp}] {level}: {message}"


async def main():
    parser = argparse.ArgumentParser(description="Error log reporter")
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours")
    parser.add_argument("--limit", type=int, default=20, help="Number of records per collection")
    args = parser.parse_args()

    await connect_to_mongo()
    db = get_database()

    since = datetime.utcnow() - timedelta(hours=args.hours)

    sections = [
        ("Backend Errors", "error_logs"),
        ("Frontend Errors", "frontend_error_logs"),
        ("Performance", "performance_logs"),
    ]

    for title, collection_name in sections:
        collection = getattr(db, collection_name, None)
        if not collection:
            print(f"\n{title}: collection '{collection_name}' missing")
            continue
        docs = await fetch_documents(collection, args.limit, since)
        print(f"\n{title} (showing {len(docs)} entries)")
        print("-" * 60)
        if not docs:
            print("No records found.")
            continue
        for doc in docs:
            print(format_doc(doc))

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
