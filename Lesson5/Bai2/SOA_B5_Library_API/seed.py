"""Run: python seed.py -- inserts repeatable example library records."""
from datetime import timedelta
from app import create_app
from extensions import db
from models import Author, Book, BookAuthor, BookCopy, Genre, Loan, Member, utc_now


def seed():
    if db.session.query(Book).first():
        print("Books already exist; seed skipped")
        return
    genres = [Genre(name=name, slug=slug) for name, slug in [
        ("Technology", "technology"), ("Literature", "literature"),
        ("Science", "science"), ("History", "history")]]
    authors = [Author(name=name) for name in [
        "Robert C. Martin", "Martin Fowler", "Eric Evans", "Nguyen Nhat Anh", "Carl Sagan"]]
    members = [Member(full_name=name, email=email) for name, email in [
        ("Nguyen An", "an@example.com"), ("Tran Binh", "binh@example.com"),
        ("Le Chi", "chi@example.com")]]
    db.session.add_all(genres + authors + members)
    db.session.flush()

    # Deliberate year/title ties to test deterministic composite cursor traversal.
    items = [
        ("Clean Code", "9780132350884", 2008, 0, [0]),
        ("Refactoring", "9780201485677", 1999, 0, [1]),
        ("Domain-Driven Design", "9780321125217", 2003, 0, [2]),
        ("Clean Architecture", "9780134494166", 2017, 0, [0]),
        ("Algorithms A", "9780000000001", 2022, 0, [1, 2]),
        ("Algorithms A", "9780000000002", 2022, 0, [2]),
        ("Algorithms B", "9780000000003", 2022, 0, [1]),
        ("Mat Biec", "9780000000004", 1990, 1, [3]),
        ("Cosmos", "9780345539434", 1980, 2, [4]),
        ("History of Time", "9780000000005", 1990, 3, [4]),
    ]
    for title, isbn, year, gi, ais in items:
        b = Book(title=title, isbn=isbn, publication_year=year, genre_id=genres[gi].id)
        db.session.add(b)
        db.session.flush()
        for pos, ai in enumerate(ais):
            db.session.add(BookAuthor(book_id=b.id, author_id=authors[ai].id,
                                      role="lead" if pos == 0 else "co"))
        for j in range(2):
            db.session.add(BookCopy(book_id=b.id, barcode=f"COPY-{b.id:03d}-{j+1}"))
    db.session.flush()
    copy = db.session.query(BookCopy).order_by(BookCopy.id).first()
    db.session.add(Loan(member_id=members[0].id, copy_id=copy.id,
                        borrowed_at=utc_now(), due_at=utc_now() + timedelta(days=14)))
    db.session.commit()
    print(f"Seed complete: {len(items)} books, {len(genres)} genres, {len(authors)} authors")


if __name__ == "__main__":
    with create_app().app_context():
        seed()
