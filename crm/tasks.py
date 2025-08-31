from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    """Fetch CRM stats from GraphQL and log them."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(
        """
        query {
            totalCustomers
            totalOrders
            totalRevenue
        }
        """
    )

    try:
        result = client.execute(query)
        customers = result.get("totalCustomers", 0)
        orders = result.get("totalOrders", 0)
        revenue = result.get("totalRevenue", 0.0)

        log_entry = (
            f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"
        )

    except Exception as e:
        log_entry = f"{timestamp} - ERROR generating report: {e}\n"

    with open(LOG_FILE, "a") as log:
        log.write(log_entry)
