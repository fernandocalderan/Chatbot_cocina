from app.services.verticals import list_verticals


def test_list_verticals_includes_directory_backed_verticals():
    items = list_verticals()
    keys = {v.get("key") for v in items if isinstance(v, dict)}
    assert "kitchens" in keys
    assert "clinics_private" in keys
    assert "home_services" in keys


def test_list_verticals_includes_files_status():
    items = list_verticals()
    kitchens = next((v for v in items if v.get("key") == "kitchens"), None)
    assert isinstance(kitchens, dict)
    files = kitchens.get("files")
    assert isinstance(files, dict)
    assert "metadata.json" in files

