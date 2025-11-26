from types import SimpleNamespace

from app.services.pdf_service import PDFService


def test_generate_pdfs_base_plan(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    tenant = SimpleNamespace(id="t1", name="Demo", plan="base")
    lead = SimpleNamespace(id="l1", meta_data={"contact_name": "Ana"})
    svc = PDFService()
    extracted = {
        "style": "moderno",
        "measures": "10",
        "budget": "5000",
        "urgency": "alta",
        "extras": "N/A",
        "fecha": "hoy",
    }
    ia_output = {}
    res_com = svc.generate_commercial_pdf(lead, tenant, extracted, ia_output)
    res_op = svc.generate_operational_pdf(lead, tenant, extracted, ia_output)
    assert res_com["pdf"]
    assert res_op["pdf"]
