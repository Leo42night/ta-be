from fastapi import FastAPI, Query, HTTPException
import json
import os
from typing import List, Dict
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable

app = FastAPI()

# Load data JSON
with open('dataset/skema_nim_to_user.json', 'r') as f:
    nim_to_user = json.load(f)

with open('dataset/skema_prodi_items.json', 'r') as f:
    prodi_items = json.load(f)

with open('dataset/skema_user_item_date.json', 'r') as f:
    user_item_dates = json.load(f)

with open('dataset/skema_item_to_matkul.json', 'r') as f:
    item_to_matkul = json.load(f)

# Load model
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

try:
    model = keras.models.load_model(
        "model/cf_model_v4.keras", custom_objects={"SliceLayer": SliceLayer}
    )
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

def predict(features: list) -> list:
    if model is None:
        return [0.0 for _ in features]  # fallback
    x = np.array([features], dtype=np.float32)
    pred = model.predict(x)
    return pred.tolist()

@app.get("/")
async def root():
    return {"message": "Hello World! FastAPI inference model NCF rekomendasi mata kuliah Siskom/Sisfo 2021-2024 & CRUD Database"}

@app.get("/input-nim")
async def input_nim(nim: str):
    # Cari user index berdasarkan NIM
    user_idx = nim_to_user.get(nim)
    if user_idx is None:
        raise HTTPException(status_code=404, detail="NIM tidak ditemukan")
    
    # Ambil data prodi
    prodi_prefix = nim[:3]
    prodi_list = prodi_items.get(prodi_prefix)
    if prodi_list is None:
        raise HTTPException(status_code=404, detail="Prodi tidak ditemukan")
    
    # Cari data matkul yang sudah diambil dan date terbaru
    user_items = [entry for entry in user_item_dates if entry["user"] == user_idx]
    if not user_items:
        available_items = prodi_list
    else:
        max_date = max(entry["date"] for entry in user_items)
        items_with_dates = [
            entry for entry in user_items if entry["date"] >= max_date
        ]
        taken_items = {entry["item"] for entry in items_with_dates}
        available_items = [
            item for item in prodi_list
            if item not in taken_items
        ]
    
    # Ganti ID item dengan nama matkul menggunakan skema_item_to_matkul.json
    response = []
    for item_id in available_items:
        matkul_name = item_to_matkul.get(str(item_id), f"Matkul {item_id}")
        response.append({
            "item": item_id,
            "matkul": matkul_name
        })
    return response

import json
from fastapi import Query

@app.get("/predict-items")
async def predict_items(items: str = Query(...)):
    try:
        # Parse string JSON ke list Python
        items_list = json.loads(items)
        if not isinstance(items_list, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Parameter 'items' harus berupa JSON array, misalnya: [1,2,3]")
    
    scores = predict(items_list)
    # return {"scores": scores}
    return {"items": {item: score for item, score in zip(items, scores)}}