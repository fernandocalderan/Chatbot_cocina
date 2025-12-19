import sys
from logging.config import fileConfig
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool
from alembic import context

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import get_settings  # noqa: E402
from app.db.base import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def _ensure_alembic_version_width(connection) -> None:
    """
    Alembic crea `alembic_version.version_num` como VARCHAR(32) por defecto.
    Este repo usa ids de revisión más largos (p.ej. `0012_add_ia_enabled_and_usage_fields`),
    lo que rompe migraciones en una DB limpia.
    """
    try:
        if getattr(connection.dialect, "name", "") != "postgresql":
            return
        # Importante: usar AUTOCOMMIT aquí. Si abrimos una transacción implícita antes
        # de `context.begin_transaction()`, Alembic puede entrar en un nested txn y
        # al cerrar la conexión se revierte todo (migraciones no persisten).
        ac = connection.execution_options(isolation_level="AUTOCOMMIT")
        ac.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(128) NOT NULL);"
        )
        ac.exec_driver_sql(
            "ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128);"
        )
    except Exception:
        return


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _ensure_alembic_version_width(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
