from app.store import db


def test_init_db_creates_registered_tables(tmp_path, monkeypatch):
    sql = "CREATE TABLE IF NOT EXISTS test_items (id TEXT PRIMARY KEY, value TEXT)"
    monkeypatch.setattr(db, "_table_sql", [])
    db.register_table(sql)
    db.register_table(sql)
    path = tmp_path / "nested" / "grabbit.db"

    db.init_db(path)
    db.init_db(path)
    with db.connect(path) as conn:
        conn.execute("INSERT INTO test_items VALUES ('a', 'b')")
    with db.connect(path) as conn:
        row = conn.execute("SELECT value FROM test_items WHERE id = 'a'").fetchone()

    assert db.registered_tables() == (sql,)
    assert row["value"] == "b"


def test_connect_rolls_back_on_error(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "_table_sql", ["CREATE TABLE IF NOT EXISTS t (id TEXT)"])
    path = tmp_path / "grabbit.db"
    db.init_db(path)

    try:
        with db.connect(path) as conn:
            conn.execute("INSERT INTO t VALUES ('x')")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    with db.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]

    assert count == 0


def test_app_startup_creates_the_database_file(client, tmp_path):
    assert (tmp_path / "test.db").exists()
