"""Standalone script to seed the database with QCAA analytical curriculum outcomes."""

from app.database import get_session_maker, init_db
from app.seed import seed


def main() -> None:
    init_db()
    session_factory = get_session_maker()
    with session_factory() as session:
        outcomes = seed(session)
    print(f"Seeded {len(outcomes)} QCAA analytical curriculum outcomes (Year 8-10).")


if __name__ == "__main__":
    main()
