"""Minimal XML-RPC upsert example for syncing Power Apps employees to Odoo.

Usage:
    python docs/powerapps_sync_example.py

Set the Odoo URL/db/login/api key values before running. In production you
would plug this logic into Azure Functions / Power Automate / etc.
"""
import xmlrpc.client

ODOO_URL = "https://yourproject.odoo.com"
ODOO_DB = "yourproject"
ODOO_USER = "integration@company.com"
ODOO_APIKEY = "replace_with_real_api_key"

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_APIKEY, {})
if not uid:
    raise RuntimeError("Invalid credentials – double check API key/login")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def upsert_employee(emp_payload):
    """Insert-or-update hr.employee using the Power Apps GUID."""
    ext_id = emp_payload["employeeid"]
    vals = {
        "name": emp_payload["fullname"],
        "work_email": emp_payload.get("emailaddress1"),
        "work_phone": emp_payload.get("telephone1"),
        "x_powerapps_id": ext_id,
    }

    existing_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_APIKEY,
        "hr.employee",
        "search",
        [[[("x_powerapps_id", "=", ext_id)]]],
        {"limit": 1},
    )

    if existing_ids:
        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_APIKEY,
            "hr.employee",
            "write",
            [existing_ids, vals],
        )
        return existing_ids[0], "updated"

    new_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_APIKEY,
        "hr.employee",
        "create",
        [vals],
    )
    return new_id, "created"


if __name__ == "__main__":
    sample = {
        "employeeid": "GUID-1234",
        "fullname": "Ali Khan",
        "emailaddress1": "ali@company.com",
        "telephone1": "+92...",
    }
    emp_id, action = upsert_employee(sample)
    print(f"Employee {emp_id} {action}")
