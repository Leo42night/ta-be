from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional

# Inference Schema
class PredictSetPayload(BaseModel):
    nim: str = Field(..., max_length=11)
    year: int
    semester: int
    
class PredictSetResponse(BaseModel):
    prediction_sets: dict[int, float]
    
class NimToUserPayload(BaseModel):
    nim: str = Field(..., max_length=11)
    
# Lecturer
class LecturerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    
class LecturerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Major
class MajorCreate(BaseModel):
    name: str = Field(..., max_length=100)

class MajorResponse(BaseModel):
    id: int

    class Config:
        from_attributes = True

# Student
class StudentCreate(BaseModel):
    nim: str = Field(..., min_length=11, max_length=11)
    name: str
    major_id: int
    angkatan: int

class StudentResponse(BaseModel):
    id: int
    nim:str
    name: str
    major_id: int
    angkatan: int

    class Config:
        from_attributes = True

# Subject
class SubjectCreate(BaseModel):
    code: str = Field(..., max_length=10)
    name: str
    lecture_id: int

class SubjectResponse(BaseModel):
    id: int
    code: str
    name: str
    lecture_id: int

    class Config:
        from_attributes = True
        
# Score
class ScoreCreate(BaseModel):
    student_id: int
    subject_id: int
    year: int = Field(..., min_length=4, max_length=4)
    semester: int = Field(..., min_length=1, max_length=2)
    score: Decimal = Field(..., precision=5, scale=2, gt=0, le=101)

class ScoreResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    year: int
    semester: int
    score: Decimal

    class Config:
        from_attributes = True