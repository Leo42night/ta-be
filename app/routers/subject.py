from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Subject, Lecturer
from ..schemas import SubjectCreate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=list[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db)):
    # cek lecturer_id ada di lecturer
    lecturer = db.query(Lecturer).filter(Lecturer.id == subject_data.lecturer_id).first()
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer not found")

    subject_obj = Subject(**subject_data.model_dump())
    db.add(subject_obj)
    db.commit()
    db.refresh(subject_obj)
    return subject_obj


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int, subject_data: SubjectCreate, db: Session = Depends(get_db)
):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Cek lecturer_id yang baru ada di lecturer
    lecturer = db.query(Lecturer).filter(Lecturer.id == subject_data.lecturer_id).first()
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer not found")

    for key, value in subject_data.model_dump().items():
        setattr(db_subject, key, value)

    db.commit()
    db.refresh(db_subject)
    return db_subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    db.delete(db_subject)
    db.commit()
    return True
