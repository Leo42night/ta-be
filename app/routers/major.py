from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Major
from ..schemas import MajorCreate, MajorResponse

router = APIRouter(prefix="/majors", tags=["majors"])


@router.get("/", response_model=list[MajorResponse])
def get_majors(db: Session = Depends(get_db)):
    return db.query(Major).all()


@router.post("/", response_model=MajorResponse, status_code=status.HTTP_201_CREATED)
def create_major(major: MajorCreate, db: Session = Depends(get_db)):
    existing = db.query(Major).filter(Major.name == major.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Name already registered")
    major = Major(**major.model_dump())
    db.add(major)
    db.commit()
    db.refresh(major)
    return major


@router.put("/{major_id}", response_model=MajorResponse)
def update_major(major_id: int, major_data: MajorCreate, db: Session = Depends(get_db)):
    db_major = db.query(Major).filter(Major.id == major_id).first()
    if not db_major:
        raise HTTPException(status_code=404, detail="Major not found")

    # Cek Nama dipakai major lain
    existing = db.query(Major).filter(Major.name == major_data.name).first()
    if existing and existing.id != major_id:
        raise HTTPException(
            status_code=400, detail="Major Name already used by another major"
        )

    for key, value in major_data.model_dump().items():
        setattr(db_major, key, value)

    db.commit()
    db.refresh(db_major)
    return db_major


@router.delete("/{major_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_major(major_id: int, db: Session = Depends(get_db)):
    db_major = db.query(Major).filter(Major.id == major_id).first()
    if not db_major:
        raise HTTPException(status_code=404, detail="Major not found")

    db.delete(db_major)
    db.commit()
    return True
