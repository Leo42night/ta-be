from fastapi import APIRouter, HTTPException
from ..schemas import PredictSetPayload, PredictSetResponse, NimToUserPayload

import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable

# utils
import json
from datetime import date

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

# skema item matkul perlu dikelompokkan
with open("dataset/skema_matkul_to_item.json") as f:
    matkul_to_item = json.load(f)
with open("dataset/skema_nim_to_user.json") as f:
    nim_to_user = json.load(f)
# pakai prefix nim (cth. H11..) sebagai key list items
with open("dataset/skema_prodi_items.json") as f:
    prodi_items = json.load(f)
# [{"user": 0, "item": 208, "tahun": "21", "semester": "1"},...]
with open("dataset/skema_user_item_date.json") as f:
    user_item_date = json.load(f)

def predict(features: list) -> list[float]:
    x = np.array([features], dtype=np.float32)
    pred = model.predict(x)
    return pred.tolist()


router = APIRouter(prefix="/inferences", tags=["inferences"])


@router.get("/matkuls", summary="Tampilkan list matkul yang dapat dipilih")
def get_all_matkul():
    return {"matkuls": matkul_to_item}
  
@router.get(
    "/matkul-by-item/{matkul}",
    summary="Ambil item id berdasarkan nama matkul",
)
def get_matkul_by_item(matkul: str):
    if matkul not in matkul_to_item:
        raise HTTPException(status_code=404, detail="Matkul tidak ditemukan")
    return {"matkul": matkul, "item": matkul_to_item[matkul]}

@router.get("/users", summary="Tampilkan list nim: users")
def get_all_users():
    return {"users": nim_to_user}

  
@router.post("/nim-to-user", summary="Cek apakah nim student sudah ada di dataset training user")
def get_nim_to_user(payload: NimToUserPayload):
    user_id = nim_to_user.get(payload.nim)
    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Payload harus berisi string 'nim' 11 digit, cth: 'H1101221016'",
        )
    return {"user": user_id}

@router.get("/prodi-matkuls/{nim}", summary="Tampilkan list matkul yang dapat dipilih berdasarkan prodi")
def filterProdiMatkul(nim: str) -> list[int]:
    items = prodi_items.get(nim[:3])
    if items is None:
        raise HTTPException(status_code=404, detail="Prodi tidak ditemukan")
    return items
  
@router.get("/item-filtered/{nim}", summary="Ambil list 'items' yang sudah di filter berdasarkan tahun dan semester")
# def getFilteredData(nim: str) -> list[{"item": int, "matkul": str}]:
def getFilteredData(nim: str):
    # cari user id berdasarkan nim
    user_id = nim_to_user.get(nim)
    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="User tidak ditemukan di dataset, Payload harus berisi string 'nim' 11 digit, cth: 'H1101221016'",
        )
        
    # cari item filter berdasarka prodi
    item_prodi = prodi_items.get(nim[:3]) # list [0,2,3,...]
    if item_prodi is None:
        raise HTTPException(status_code=404, detail=f"Matkul dari prodi {nim[:3]} tidak ditemukan")
    
    # filter item_prodi berdasarkan tahun dan semester
    current_year = date.today().year % 100 
    current_semester = "2" if date.today().month < 7 else "1"
    current_date = int(str(current_year) + current_semester)
    
    # item yang sudah diambil user ini sampai current_date
    user_item_map = {
      row["item"]: row
      for row in user_item_date
      if row["user"] == user_id
      and row["date"] < current_date
    }
    
    # item yang ada di item prodi tapi belum diambil oleh user
    not_taken_items = [
        item 
        for item in item_prodi 
        if item not in user_item_map
    ]
    
    # kembalikan item_id: matkul
    item_matkul_result = {
        item: matkul_to_item[matkul]
        for item, matkul in matkul_to_item.items()
        if item in not_taken_items
    }
    
    return not_taken_items

@router.post("/predict", summary="testing prediksi model")
def inference(payload: list[int]):
    result = predict(payload)
    return {"prediction": result}

@router.post(
    "/predict-set",
    response_model=PredictSetResponse,
    summary="prediksi dari user & list item matkul yang dipilih",
    description="Menghasilkan skor rekomendasi untuk satu user dan banyak mata kuliah",
)
def predict_set(payload: PredictSetPayload):
    if "user" not in payload or not isinstance(payload["user"], int):
        raise HTTPException(
            status_code=400, detail="Payload harus berisi integer 'user'"
        )
    if "items" not in payload or not isinstance(payload["items"], list):
        raise HTTPException(status_code=400, detail="Payload harus berisi list 'items'")

    user = payload["user"]
    results = {}

    for i, item in enumerate(payload["items"]):
        results[i] = predict([user, item])[0][0]

    return {"prediction_sets": results}
