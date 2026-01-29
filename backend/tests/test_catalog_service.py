from app.services.catalog_service import list_catalog


class _EmptyQuery:
    def __init__(self, data):
        self._data = data

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return list(self._data)

    def join(self, *args, **kwargs):
        return self


class _EmptySession:
    def query(self, model):
        return _EmptyQuery([])


def test_catalog_includes_filesystem_scopes():
    catalog = list_catalog(_EmptySession(), include_empty_scopes=True)
    verticals = {v.vertical_key for v in catalog.verticals}
    assert "kitchens" in verticals
    kitchens = [v for v in catalog.verticals if v.vertical_key == "kitchens"][0]
    scope_keys = {s.scope_key for s in kitchens.scopes}
    assert "cocinas_completas" in scope_keys
