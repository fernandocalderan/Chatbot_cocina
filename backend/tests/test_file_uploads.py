from app.services.file_service import FileService


def test_file_upload_and_download(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    fs = FileService(base_dir=str(tmp_path))
    key = fs.upload_pdf("t1", "l1", b"data", "comercial")
    data = fs.download_pdf(key)
    assert data == b"data"
