from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, Score, Student, Subject
from ..schemas import ScoreCreate, ScoreResponse

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/", response_model=list[ScoreResponse])
def get_scores(db: Session = Depends(get_db)):
    return db.query(Score).all()


@router.post("/", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(score: ScoreCreate, db: Session = Depends(get_db)):
    # cek student_id & subject_id ada di student & subject
    student = db.query(Student).filter(Student.id == score.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    subject = db.query(Subject).filter(Subject.id == score.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    score = Score(**score.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.put("/{score_id}", response_model=ScoreResponse)
def update_score(score_id: int, score_data: ScoreCreate, db: Session = Depends(get_db)):
    db_score = db.query(Score).filter(Score.id == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="score not found")

    for key, value in score_data.model_dump().items():
        setattr(db_score, key, value)

    db.commit()
    db.refresh(db_score)
    return db_score


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_score(score_id: int, db: Session = Depends(get_db)):
    db_score = db.query(Score).filter(Score.id == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="score not found")

    db.delete(db_score)
    db.commit()
    return True
