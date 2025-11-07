import sys
from pathlib import Path
from importlib import import_module
from db.connection import get_connection

# --- Ensure consistent project root ---
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

def run_migrations(conn):
    print("🏗️  Running migrations...")
    migrations_dir = BASE_DIR / "migrations"

    for file in sorted(migrations_dir.glob("*.py")):
        module_name = f"migrations.{file.stem}"
        module = import_module(module_name)
        if hasattr(module, "run"):
            module.run(conn)
    print("✅ Migrations complete.\n")


def run_seeders(conn):
    print("🌱 Running seeders...")
    seeders_dir = BASE_DIR / "seeders"

    for file in sorted(seeders_dir.glob("*.py")):
        module_name = f"seeders.{file.stem}"
        module = import_module(module_name)
        if hasattr(module, "run"):
            module.run(conn)
    print("✅ Seeders complete.\n")


def run():
    conn = get_connection()

    run_migrations(conn)
    run_seeders(conn)

    # Show record counts
    print("📊 Final counts:")
    for table in [
        "companies",
        "departments",
        "users",
        "roles",
        "user_roles",
        "company_users",
        "department_users",
    ]:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")
        except Exception:
            pass

    conn.close()


if __name__ == "__main__":
    run()
