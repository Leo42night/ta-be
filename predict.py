import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable
from sklearn.model_selection import train_test_split, GridSearchCV
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
    

# --- Model builder
def build_ncf_model(n_users, n_items, embed_dim=16, hidden=[32, 16, 8], lr=0.001):
    inputs = keras.Input(shape=(2,), name="user_item_input")

    user_input = SliceLayer(0)(inputs)
    item_input = SliceLayer(1)(inputs)

    user_input = layers.Reshape((1,))(user_input)
    item_input = layers.Reshape((1,))(item_input)

    user_emb = layers.Embedding(n_users, embed_dim)(user_input)
    item_emb = layers.Embedding(n_items, embed_dim)(item_input)

    user_vec = layers.Flatten()(user_emb)
    item_vec = layers.Flatten()(item_emb)
    x = layers.Concatenate()([user_vec, item_vec])

    for h in hidden:
        x = layers.Dense(h, activation="relu")(x)

    output = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=output)

    optimizer = keras.optimizers.Adam(learning_rate=lr)
    model.compile(optimizer=optimizer, loss="mse")
    return model


# --- Hitung jumlah user & item
n_users = df2["user"].nunique()
n_items = df2["item"].nunique()

# --- Bungkus ke KerasRegressor
regressor = KerasRegressor(
    model=lambda embed_dim, hidden, lr: build_ncf_model(
        n_users=n_users, n_items=n_items, embed_dim=embed_dim, hidden=hidden, lr=lr
    ),
    epochs=10,
    batch_size=32,
    verbose=0
)

param_grid = {
    "model__embed_dim": [16],              # tetap 1 nilai tengah
    "model__hidden": [[64, 32, 16], [32, 16, 8]],  # 2 kombinasi arsitektur
    "model__lr": [0.001],                  # 1 nilai stabil
    "batch_size": [32],                    # 1 nilai default efisien
    "epochs": [5, 8]                       # 2 nilai ringan
}

# --- Grid Search
grid = GridSearchCV(
    estimator=regressor,
    param_grid=param_grid,
    scoring="neg_mean_squared_error",
    cv=3,
    verbose=2
)

grid_result = grid.fit(X_train, y_train)

# --- Hasil terbaik
print(f"Best Params: {grid_result.best_params_}")

best_model = grid_result.best_estimator_
y_pred = best_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"✅ Test RMSE: {rmse:.4f}")