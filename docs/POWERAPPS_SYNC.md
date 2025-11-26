# Power Apps → Odoo Employee Sync

## 1. Authentication
- Create a dedicated technical user in Odoo (`Settings > Users`).
- Generate an API key for that user and keep it secret.
- Use that API key as the password when authenticating over XML-RPC/JSON-RPC.

## 2. Core endpoints (Odoo 18/19)
```
https://YOUR_ODOO_DOMAIN/xmlrpc/2/common  # authenticate
https://YOUR_ODOO_DOMAIN/xmlrpc/2/object  # execute model methods
```
> Odoo 20 replaces `/xmlrpc` + `/jsonrpc` with the “External JSON-2 API”, so keep middleware abstracted in case you need to swap transports.

## 3. Data model additions
`custom_addons/vw_employee_api/models/hr_employee.py` now adds `x_powerapps_id` so each hr.employee keeps the Dataverse GUID for idempotent upserts.

## 4. Upsert algorithm
1. Receive payload from Power Apps (Dataverse).
2. Search `hr.employee` by `x_powerapps_id`.
3. If found → `write` the mapped fields.
4. If not → `create` with the mapped values, including the GUID.
5. When a record is deleted/disabled, set `active=False` for the matching employee in Odoo.

See `docs/powerapps_sync_example.py` for a runnable skeleton.

## 5. Field mapping checklist
| Dataverse field | Odoo field | Notes |
| --------------- | ---------- | ----- |
| employeeid | x_powerapps_id | required, unique |
| fullname | name | required |
| emailaddress1 | work_email | optional |
| telephone1 | work_phone | optional |
| jobtitle | job_id | resolve/create `hr.job` first |
| department | department_id | resolve/create `hr.department` |
| manager | parent_id | find manager via their `x_powerapps_id` |
| status | active | set `False` when inactive |

## 6. Scheduling & reliability tips
- Run sync job every 5–15 minutes (depending on business needs).
- Log each push (Dataverse GUID, Odoo ID, timestamp, payload hash).
- Use retry/backoff logic when Odoo is temporarily unavailable.

## 7. Optional REST layer
This repo still exposes `/api/employees` (JSON POST). That gives you a future-proof REST façade if you prefer pushing from Dataverse webhooks instead of running middleware. Authentication uses the same Odoo API key (send it in `X-API-KEY`).
