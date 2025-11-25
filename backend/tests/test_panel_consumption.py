def test_panel_can_consume_api_without_errors(client_demo, demo_headers, demo_data, force_password_ok):
    client = client_demo
    headers = demo_headers
    tenant_id = demo_data["tenant_id"]

    # Leads
    leads_resp = client.get("/v1/leads", headers=headers)
    assert leads_resp.status_code == 200
    leads_data = leads_resp.json()["items"]
    lead_ids = {item["id"] for item in leads_data}
    assert "lead-demo" in lead_ids
    assert "lead-other" not in lead_ids

    # Appointments
    appt_resp = client.get("/v1/appointments", headers=headers)
    assert appt_resp.status_code == 200
    appt_data = appt_resp.json()["items"]
    appt_ids = {item["id"] for item in appt_data}
    assert "appt-demo" in appt_ids
    assert "appt-other" not in appt_ids

    # Flow current
    flow_resp = client.get("/v1/flows/current", headers=headers)
    assert flow_resp.status_code == 200
    flow_data = flow_resp.json()
    assert flow_data["tenant_id"] == tenant_id
    assert flow_data["flow_id"] == "flow-demo"

    # Session state
    sess_resp = client.get(f"/v1/sessions/{demo_data['session'].id}", headers=headers)
    assert sess_resp.status_code == 200
    sess_data = sess_resp.json()
    assert sess_data["tenant_id"] == tenant_id
    assert sess_data["session_id"] == demo_data["session"].id
import pytest


@pytest.fixture
def force_password_ok(monkeypatch):
    import app.core.security
    import app.api.auth

    monkeypatch.setattr("app.core.security.verify_password", lambda plain, hashed: True)
    monkeypatch.setattr("app.api.auth.verify_password", lambda plain, hashed: True, raising=False)
