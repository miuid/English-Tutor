"""Standalone script to seed the database with Year 8 curriculum outcomes."""

from app.database import get_session_maker, init_db
from app.seed import seed


def main() -> None:
    init_db()
    session_factory = get_session_maker()
    with session_factory() as session:
        seed(session)
    print("Seeded Year 8 curriculum outcomes.")


if __name__ == "__main__":
    main()
