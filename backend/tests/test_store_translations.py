from app.store import db, translations
from app.store.translations import Translation


def test_a_database_initialised_without_the_table_still_stores_translations(tmp_path, monkeypatch):
    # A database from before the translations table existed (the event's cache file).
    path = tmp_path / "old.db"
    monkeypatch.setenv("DATABASE_PATH", str(path))
    from app.config import get_settings

    get_settings.cache_clear()
    with db.connect(path) as conn:
        conn.execute("CREATE TABLE cala_cache (key TEXT PRIMARY KEY)")

    assert translations.get_many(["Hei"], "en") == {}
    translations.put_many({"Hei": Translation(language="fi", text="Hi")}, "en")
    assert translations.get_many(["Hei"], "en")["Hei"].text == "Hi"
