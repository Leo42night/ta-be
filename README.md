Backend FastAPI Inference model NCF rekomendasi mata kuliah.<br>
Deploy ke HuggingFace Space. akses API url.<br>
Menggunakan model **.pkl**<br>

run in Windows CMD:
```bash
.venv\\Scripts\\activate.bat

# install dependency
pip install -r requirements.txt
# opsional: matikan message oneDNN custom operations
set TF_ENABLE_ONEDNN_OPTS=0 
# opsional: check var
echo %TF_ENABLE_ONEDNN_OPTS%

# Run Laragon, Buat database MySQL dengan nama 'tugas_akhir'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uvicorn app.main:app --reload --port 8000
ngrok http 8000

```

Backend menggunakan FastAPI:
"/input-nim"?nim=string -> {item (number): matkul (string)}[]:
- gunakan file `skema_nim_to_user.json`: Ambil data student/user berdasarkan NIM
```json
{
  "H1051131001": 0,
  "H1051131005": 1,
  "H1051131007": 2,
  "H1051131009": 3,
  ...
}
```
- gunakan file `skema_prodi_items.json`: Filter matkul/item per Prodi (prefix `H10` or `H11`)
```json
{
  "H10": [
    0,
    3,
    4,
    5,
    8,
    ...
  ],
   "H11": [
    0,
    1,
    2,
    3,
    6
  ],...
}
```
- gunakan file `skema_user_item_date.json`: Filter matkul/item: (hapus item yang sudah diambil, hapus item yang date di bawah date user terbaru), kembalikan sisanya. 
```json
[
    {
        "user": 0,
        "item": 208,
        "date": 211
    },
    {
        "user": 1,
        "item": 208,
        "date": 211
    },
    {
        "user": 2,
        "item": 51,
        "date": 211
    },...
]
```

"/predict-items"?items=number[] -> {items {number}: score {float}}[]
run Model Keras to predict each, return score for each.
```python
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable

@register_keras_serializable(package="Custom")
class SliceLayer(Layer):
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index

    def call(self, inputs):
        return inputs[:, self.index]

    def get_config(self):
        config = super().get_config()
        config.update({"index": self.index})
        return config


# Load Model & Metadata
model = keras.models.load_model(
    "model/cf_model_v4.keras", custom_objects={"SliceLayer": SliceLayer}
)

def predict(features: list) -> list[float]:
    x = np.array([features], dtype=np.float32)
    pred = model.predict(x)
    return pred.tolist()
```
- 


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
