from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    SmallInteger,
    DECIMAL,
    String,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

DATABASE_URL = "mysql+pymysql://root:@localhost/tugas_akhir"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# -- Models --
class Lecturer(Base):
    __tablename__ = "lecturers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    students = relationship("Student", back_populates="major")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nim = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id", ondelete="RESTRICT"))
    angkatan = Column(Integer, nullable=False)

    scores = relationship("Score", cascade="all, delete", back_populates="student")
    major = relationship("Major", back_populates="students")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )

    subject_id = Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    year = Column(Integer, nullable=False)  # ⬅ FIX
    semester = Column(SmallInteger, nullable=False)
    score = Column(DECIMAL(5, 2))

    student = relationship("Student", back_populates="scores")


# Create all tables
Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db()
