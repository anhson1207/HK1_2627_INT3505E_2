"""Persistence models. API serializers intentionally hide internal DB columns."""
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Integer, String, Text
from extensions import db


def utc_now():
    # SQLite returns naive datetimes; interpret these as UTC in representations.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


class Genre(db.Model):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    books: Mapped[list["Book"]] = relationship(back_populates="genre")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, index=True)
    genre: Mapped[Genre] = relationship(back_populates="books")
    author_links: Mapped[list["BookAuthor"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    copies: Mapped[list["BookCopy"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    __table_args__ = (CheckConstraint("publication_year BETWEEN 1450 AND 2100", name="ck_publication_year"),)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "publicationYear": self.publication_year,
            "description": self.description,
            "genre": self.genre.to_dict(),
            "authors": [
                {"id": link.author.id, "name": link.author.name, "role": link.role}
                for link in sorted(self.author_links, key=lambda link: link.author_id)
            ],
            "totalCopies": len(self.copies),
            "availableCopies": sum(c.is_available() for c in self.copies),
            "createdAt": iso_utc(self.created_at),
        }


class Author(db.Model):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_links: Mapped[list["BookAuthor"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="co")
    book: Mapped[Book] = relationship(back_populates="author_links")
    author: Mapped[Author] = relationship(back_populates="book_links")
    __table_args__ = (CheckConstraint("role IN ('lead', 'co', 'editor')", name="ck_author_role"),)


class BookCopy(db.Model):
    __tablename__ = "book_copies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    barcode: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False, default="available")
    book: Mapped[Book] = relationship(back_populates="copies")
    loans: Mapped[list["Loan"]] = relationship(back_populates="copy")
    __table_args__ = (CheckConstraint("condition IN ('available', 'maintenance')", name="ck_copy_condition"),)

    def is_available(self):
        return self.condition == "available" and not any(l.returned_at is None for l in self.loans)

    def to_dict(self):
        return {"id": self.id, "bookId": self.book_id, "barcode": self.barcode,
                "condition": self.condition, "isAvailable": self.is_available()}


class Member(db.Model):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    loans: Mapped[list["Loan"]] = relationship(back_populates="member")

    def to_dict(self):
        return {"id": self.id, "fullName": self.full_name, "email": self.email,
                "joinedAt": iso_utc(self.joined_at)}


class Loan(db.Model):
    __tablename__ = "loans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False, index=True)
    copy_id: Mapped[int] = mapped_column(ForeignKey("book_copies.id"), nullable=False, index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    due_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    member: Mapped[Member] = relationship(back_populates="loans")
    copy: Mapped[BookCopy] = relationship(back_populates="loans")
    __table_args__ = (CheckConstraint("due_at > borrowed_at", name="ck_loan_due_after_borrow"),)

    def to_dict(self):
        return {"id": self.id, "memberId": self.member_id, "copyId": self.copy_id,
                "borrowedAt": iso_utc(self.borrowed_at), "dueAt": iso_utc(self.due_at),
                "returnedAt": iso_utc(self.returned_at),
                "status": "returned" if self.returned_at else "active"}
