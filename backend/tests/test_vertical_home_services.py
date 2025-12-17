from app.services.flow_templates import load_flow_template
from app.services.verticals import get_vertical_config, resolve_flow_id, vertical_prompt


def test_home_services_vertical_prompt_from_file():
    text = vertical_prompt("home_services")
    assert text
    assert "servicios para el hogar" in text.lower()
    assert "No prometas precios" in text


def test_home_services_vertical_config_merges_metadata():
    cfg = get_vertical_config("home_services")
    assert cfg.get("label") == "Servicios para el Hogar"
    assert cfg.get("default_flow_id") == "home_services_base_v1"
    assert isinstance(cfg.get("promise_commercial"), str) and cfg.get("promise_commercial")
    ci = cfg.get("conversational_intelligence")
    assert isinstance(ci, dict) and bool(ci.get("enabled")) is True


def test_home_services_resolve_flow_id_defaults_to_home_services_flow():
    assert resolve_flow_id(None, "home_services") == "home_services_base_v1"
    assert resolve_flow_id("invalid_flow", "home_services") == "home_services_base_v1"


def test_home_services_flow_template_loads():
    flow = load_flow_template("home_services_base_v1", plan_value="base", vertical_key="home_services")
    assert isinstance(flow, dict)
    assert flow.get("start_block") == "welcome"
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    assert "service_type" in blocks
    assert "appointment_offer" in blocks
