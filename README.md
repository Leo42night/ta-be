Backend FastAPI Inference model NCF rekomendasi mata kuliah.<br>
Deploy ke HuggingFace Space. akses API url.<br>
Menggunakan model **.pkl**<br>

run in Windows CMD:
```bash
.venv\\Scripts\\activate.bat

set TF_ENABLE_ONEDNN_OPTS=0 # opsional: matikan message oneDNN custom operations
echo %TF_ENABLE_ONEDNN_OPTS% # opsional: check var
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uvicorn app.main:app --reload --port 8000
ngrok http 8000

```

nim -> matkul yang sudah di kerjakan, sisa sks

# table structure


# initial
Fill data tabel "scores":
  -> Jika "NIM" baru, insert "students" table
  -> Jika "teacher_name" baru, insert "teachers" (butuh tambah manual, handling unique name)
  -> Jika "major baru"

# DB Query
## Must
- CRUD: (lecturers, majors) -> (students, subjects, scores, subject_prerequisites, subject_similars)
