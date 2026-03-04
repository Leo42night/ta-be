import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, message=".*np.object.*")
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from fastapi import FastAPI

# Initialize
app = FastAPI(
    title="Model NCF Inference API & CRUD Data",
    description="FastAPI inference model NCF rekomendasi mata kuliah Siskom/Sisfo 2021-2024 & CRUD Database",
    version="1.0",
)

# Routers
from .routers import lecturer, major, subject, student, score, inference
app.include_router(inference.router)
app.include_router(lecturer.router)
app.include_router(major.router)
app.include_router(student.router)
app.include_router(subject.router)
app.include_router(score.router)

# Routes
@app.get("/")
def root():
    return {
        "message": "Hello World! FastAPI inference model NCF rekomendasi mata kuliah Siskom/Sisfo 2021-2024 & CRUD Database"
    }