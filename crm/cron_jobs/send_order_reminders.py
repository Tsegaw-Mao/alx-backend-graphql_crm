#!/usr/bin/env python3
import sys
import asyncio
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Log file
LOG_FILE = "/tmp/order_reminders_log.txt"


async def fetch_orders():
    # Transport setup
    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL,
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Compute cutoff date (7 days ago)
    cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # GraphQL query
    query = gql(
        """
        query GetRecentOrders($cutoff: Date!) {
            orders(filter: {orderDate_Gte: $cutoff, status: "PENDING"}) {
                id
                customer {
                    email
                }
            }
        }
        """
    )

    params = {"cutoff": cutoff_date}

    try:
        result = await client.execute_async(query, variable_values=params)
        orders = result.get("orders", [])
    except Exception as e:
        print(f"GraphQL query failed: {e}", file=sys.stderr)
        return []

    return orders


async def main():
    orders = await fetch_orders()

    # Append logs with timestamp
    with open(LOG_FILE, "a") as log:
        for order in orders:
            log.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                f"Order ID: {order['id']}, Customer: {order['customer']['email']}\n"
            )

    print("Order reminders processed!")


if __name__ == "__main__":
    asyncio.run(main())
