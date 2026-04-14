from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Lecturer
from ..schemas import LecturerCreate, LecturerResponse

router = APIRouter(prefix="/lecturers", tags=["lecturers"])


@router.get("/", response_model=list[LecturerResponse])
def get_lecturers(db: Session = Depends(get_db)):
    return db.query(Lecturer).all()

@router.post("/", response_model=LecturerResponse, status_code=status.HTTP_201_CREATED)
def create_lecturer(lecturer: LecturerCreate, db: Session = Depends(get_db)):
    existing = db.query(Lecturer).filter(Lecturer.name == lecturer.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Name already registered")
    lecturer = Lecturer(**lecturer.model_dump())
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)
    return lecturer

@router.put("/{lecturer_id}", response_model=LecturerResponse)
def update_lecturer(lecturer_id: int, lecturer_data: LecturerCreate, db: Session = Depends(get_db)):
    db_lecturer = db.query(Lecturer).filter(Lecturer.id == lecturer_id).first()
    if not db_lecturer:
        raise HTTPException(status_code=404, detail="lecturer not found")

    # Cek Nama dipakai lecturer lain
    existing = db.query(Lecturer).filter(Lecturer.name == lecturer_data.name).first()
    if existing and existing.id != lecturer_id:
        raise HTTPException(
            status_code=400, detail="lecturer Name already used by another lecturer"
        )

    for key, value in lecturer_data.model_dump().items():
        setattr(db_lecturer, key, value)

    db.commit()
    db.refresh(db_lecturer)
    return db_lecturer

@router.delete("/{lecturer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lecturer(lecturer_id: int, db: Session = Depends(get_db)):
    db_lecturer = db.query(Lecturer).filter(Lecturer.id == lecturer_id).first()
    if not db_lecturer:
      raise HTTPException(status_code=404, detail="lecturer not found")

    db.delete(db_lecturer)
    db.commit()
    return True