from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Student, Major
from ..schemas import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    existing_nim = db.query(Student).filter(Student.nim == student_data.nim).first()
    if existing_nim:
        raise HTTPException(status_code=400, detail="NIM already registered")

    # cek major_id ada di major
    major = db.query(Major).filter(Major.id == student_data.major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Major not found")

    student_obj = Student(**student_data.model_dump())
    db.add(student_obj)
    db.commit()
    db.refresh(student_obj)
    return student_obj


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int, student_data: StudentCreate, db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Cek Major yang baru ada di major
    major = db.query(Major).filter(Major.id == student.major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Major not found")

    # Cek NIM dipakai mahasiswa lain
    existing_other_nim = (
        db.query(Student)
        .filter(Student.id != student_id, Student.nim == student_data.nim)
        .first()
    )
    if existing_other_nim:
        raise HTTPException(
            status_code=400, detail="NIM already used by another student"
        )

    for key, value in student_data.model_dump().items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(db_student)
    db.commit()
    return True
