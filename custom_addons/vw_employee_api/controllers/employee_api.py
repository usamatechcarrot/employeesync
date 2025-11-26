# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response


def _json_response(payload, status=200):
    return Response(
        json.dumps(payload),
        status=status,
        content_type="application/json; charset=utf-8",
    )


class EmployeeAPIController(http.Controller):

    @http.route(
        "/api/employees",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def upsert_employee(self, **kwargs):

        # Odoo 19: JSON-RPC params are here
        data = request.params or {}

        # ---- API KEY AUTH ----
        api_key = request.httprequest.headers.get("X-API-KEY")
        if not api_key:
            return _json_response({"error": "Missing X-API-KEY header"}, status=401)

        user = request.env["res.users"].sudo().search(
            [("api_key_ids.key", "=", api_key)],
            limit=1
        )
        if not user:
            return _json_response({"error": "Invalid API key"}, status=401)

        env = request.env(user=user).sudo()

        # ---- Required fields ----
        name = data.get("name")
        if not name:
            return _json_response({"error": "name is required"}, status=400)

        external_id = data.get("external_id")

        vals = {
            "name": name,
            "work_email": data.get("work_email"),
            "work_phone": data.get("work_phone"),
            "job_title": data.get("job_title"),
        }

        if data.get("department_id"):
            vals["department_id"] = int(data["department_id"])
        if data.get("manager_id"):
            vals["parent_id"] = int(data["manager_id"])

        Employee = env["hr.employee"]

        employee = False
        if external_id:
            employee = Employee.search([("x_external_id", "=", external_id)], limit=1)
            if not employee:
                vals["x_external_id"] = external_id

        if employee:
            employee.write(vals)
            return {"result": "updated", "id": employee.id}
        else:
            new_emp = Employee.create(vals)
            return {"result": "created", "id": new_emp.id}
