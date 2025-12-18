import pytest

from app.services.flow_templates import load_flow_template
from app.services.verticals import scope_defaults, validate_vertical_scopes


def test_home_services_scope_overrides_flow_and_defaults():
    flow = load_flow_template(
        None,
        plan_value="base",
        vertical_key="home_services",
        scopes=["electricidad"],
    )
    assert isinstance(flow, dict)
    assert flow.get("version") == "home_services__electricidad__v1"
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    assert (blocks.get("service_type") or {}).get("next") == "urgency"
    defaults = scope_defaults("home_services", ["electricidad"])
    assert defaults.get("category") == "electricidad"


def test_clinics_private_scope_overrides_flow_and_defaults():
    flow = load_flow_template(
        None,
        plan_value="base",
        vertical_key="clinics_private",
        scopes=["podologia"],
    )
    assert isinstance(flow, dict)
    assert flow.get("version") == "clinics_private__podologia__v1"
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    assert (blocks.get("service_type") or {}).get("next") == "urgency"
    defaults = scope_defaults("clinics_private", ["podologia"])
    assert defaults.get("specialty") == "podologia"


def test_validate_vertical_scopes_rejects_invalid():
    with pytest.raises(ValueError):
        validate_vertical_scopes("clinics_private", ["not_a_scope"])

