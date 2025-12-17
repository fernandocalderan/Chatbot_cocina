from app.services.flow_templates import load_flow_template
from app.services.verticals import get_vertical_config, resolve_flow_id, vertical_prompt


def test_clinics_private_vertical_prompt_from_file():
    text = vertical_prompt("clinics_private")
    assert text
    assert "No realices diagnósticos" in text
    assert "No des consejos médicos" in text


def test_clinics_private_vertical_config_merges_metadata():
    cfg = get_vertical_config("clinics_private")
    assert cfg.get("label") == "Clínicas Privadas"
    assert cfg.get("default_flow_id") == "clinics_private_base_v1"
    assert isinstance(cfg.get("promise_commercial"), str) and cfg.get("promise_commercial")


def test_clinics_private_resolve_flow_id_defaults_to_clinics_flow():
    assert resolve_flow_id(None, "clinics_private") == "clinics_private_base_v1"
    assert resolve_flow_id("invalid_flow", "clinics_private") == "clinics_private_base_v1"


def test_clinics_private_flow_template_loads():
    flow = load_flow_template("clinics_private_base_v1", plan_value="base", vertical_key="clinics_private")
    assert isinstance(flow, dict)
    assert flow.get("start_block") == "welcome"
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    assert "service_type" in blocks
    assert "appointment_offer" in blocks
