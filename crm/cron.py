import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"
GRAPHQL_URL = "http://localhost:8000/graphql"

def log_crm_heartbeat():
    """Logs a heartbeat message and optionally checks GraphQL endpoint."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Append to log file
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

    # Optional: GraphQL hello field check
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=1)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(""" query { hello } """)
        result = client.execute(query)
        hello_response = result.get("hello", "")

        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp} GraphQL hello: {hello_response}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp} GraphQL check failed: {e}\n")
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/low_stock_updates_log.txt"

def update_low_stock():
    """Run GraphQL mutation to update low-stock products and log results."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql(
            """
            mutation {
                updateLowStockProducts {
                    success
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
            """
        )

        result = client.execute(mutation)
        update_data = result.get("updateLowStockProducts", {})
        updated_products = update_data.get("updatedProducts", [])

        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp} - {update_data.get('success')}\n")
            for product in updated_products:
                log.write(
                    f"{timestamp} - Updated: {product['name']} (Stock: {product['stock']})\n"
                )

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp} - ERROR: {e}\n")
