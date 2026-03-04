import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scikeras.wrappers import KerasRegressor

# --- Split data
X = df2[["user", "item"]].values
y = df2["rating"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

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

# --- Model builder (terima satu array 2 kolom)
def build_ncf_model(n_users, n_items, embed_dim=16, hidden=[32, 16, 8], lr=0.001):
    inputs = keras.Input(shape=(2,), name="user_item_input")

    # Pisahkan kolom user & item
    user_input = SliceLayer(0)(inputs)
    item_input = SliceLayer(1)(inputs)

    # Ubah ke int agar bisa dipakai di Embedding
    user_input = layers.Reshape((1,))(user_input)
    item_input = layers.Reshape((1,))(item_input)

    user_emb = layers.Embedding(n_users, embed_dim)(user_input)
    item_emb = layers.Embedding(n_items, embed_dim)(item_input)

    # Flatten embedding
    user_vec = layers.Flatten()(user_emb)
    item_vec = layers.Flatten()(item_emb)

    # Gabungkan
    x = layers.Concatenate()([user_vec, item_vec])

    # Hidden layers
    for h in hidden:
        x = layers.Dense(h, activation="relu")(x)

    output = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=output)

    optimizer = keras.optimizers.Adam(learning_rate=lr)
    model.compile(optimizer=optimizer, loss="mse")
    return model

# --- Setup model
n_users = df2["user"].nunique()
n_items = df2["item"].nunique()

model = KerasRegressor(
    model=lambda: build_ncf_model(n_users, n_items),
    epochs=10,
    batch_size=32,
    verbose=1
)

# --- Train
model.fit(X_train, y_train)

# --- Predict
y_pred = model.predict(X_test)

# --- Evaluate
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"✅ RMSE: {rmse:.4f}")