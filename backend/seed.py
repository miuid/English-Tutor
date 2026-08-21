"""Standalone script to seed the database with QCAA curriculum outcomes."""

from app.database import get_session_maker, init_db
from app.seed import seed


def main() -> None:
    init_db()
    session_factory = get_session_maker()
    with session_factory() as session:
        outcomes = seed(session)
    print(
        f"Seeded {len(outcomes)} QCAA curriculum outcomes "
        "(analytical + persuasive + imaginative, Year 8-10; "
        "senior QCE Units 1-4 + IA1/IA2/IA3/EA framework)."
    )


if __name__ == "__main__":
    main()
