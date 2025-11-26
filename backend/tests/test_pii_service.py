from app.services.pii_service import PIIService, PII_PREFIX, CURRENT_KEY_VERSION


def test_encrypt_decrypt_roundtrip(monkeypatch):
    monkeypatch.setenv("PII_ENCRYPTION_KEY", "test-key-12345678901234567890")
    svc = PIIService()
    plain = "test@example.com"
    enc = svc.encrypt_pii(plain, field_name="email", tenant_id="t1")
    assert enc.startswith(f"{PII_PREFIX}:v{CURRENT_KEY_VERSION}:")
    dec = svc.decrypt_pii(enc)
    assert dec == plain


def test_masking():
    svc = PIIService()
    masked_email = svc.mask_pii("john.doe@example.com", "email")
    assert masked_email.startswith("jo")
    assert masked_email.endswith("@example.com")
    masked_phone = svc.mask_pii("1234567890", "phone")
    assert masked_phone.startswith("12") and masked_phone.endswith("90")


def test_encrypt_meta_only_pii(monkeypatch):
    monkeypatch.setenv("PII_ENCRYPTION_KEY", "another-key-123456789012345678")
    svc = PIIService()
    meta = {"contact_name": "Ana", "contact_email": "ana@example.com", "notes": "ok"}
    new_meta, changed = svc.encrypt_meta(meta, "t1")
    assert changed
    assert svc.is_encrypted(new_meta["contact_name"])
    decrypted = svc.decrypt_meta(new_meta)
    assert decrypted["contact_email"] == "ana@example.com"
