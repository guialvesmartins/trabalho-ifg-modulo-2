"""Rede Neural Feedforward (MLP) implementada do zero com NumPy — Classificação Binária.

Arquitetura:
    Entrada (N features) -> Hidden1 (64, ReLU) -> Hidden2 (32, ReLU) -> Saída (1, Sigmoid)

Target: condition_binary (0 = normal, 1 = anomaly).
Otimizador: mini-batch SGD com momento.
"""

import pickle
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class HardCodedMLP:
    def __init__(
        self,
        hidden1=64,
        hidden2=32,
        learning_rate=0.01,
        momentum=0.9,
        epochs=300,
        batch_size=32,
        random_state=42,
    ):
        self.hidden1 = hidden1
        self.hidden2 = hidden2
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state
        self.loss_history = []

    def _init_params(self, n_features):
        np.random.seed(self.random_state)

        self.W1 = np.random.randn(n_features, self.hidden1) * np.sqrt(2.0 / n_features)
        self.b1 = np.zeros((1, self.hidden1))

        self.W2 = np.random.randn(self.hidden1, self.hidden2) * np.sqrt(2.0 / self.hidden1)
        self.b2 = np.zeros((1, self.hidden2))

        self.W3 = np.random.randn(self.hidden2, 1) * np.sqrt(2.0 / self.hidden2)
        self.b3 = np.zeros((1, 1))

        self.vW1 = np.zeros_like(self.W1)
        self.vb1 = np.zeros_like(self.b1)
        self.vW2 = np.zeros_like(self.W2)
        self.vb2 = np.zeros_like(self.b2)
        self.vW3 = np.zeros_like(self.W3)
        self.vb3 = np.zeros_like(self.b3)

    def _relu(self, Z):
        return np.maximum(0, Z)

    def _relu_derivative(self, Z):
        return (Z > 0).astype(float)

    def _sigmoid(self, Z):
        return 1.0 / (1.0 + np.exp(-np.clip(Z, -500, 500)))

    def _forward(self, X):
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = self._relu(Z1)

        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self._relu(Z2)

        Z3 = np.dot(A2, self.W3) + self.b3
        A3 = self._sigmoid(Z3)

        cache = (Z1, Z2, Z3)
        return A1, A2, A3, cache

    def _backward(self, X, y, cache, A1, A2, A3):
        m = X.shape[0]
        Z1, Z2, Z3 = cache

        dZ3 = (A3 - y) / m
        dW3 = np.dot(A2.T, dZ3)
        db3 = np.sum(dZ3, axis=0, keepdims=True)

        dA2 = np.dot(dZ3, self.W3.T)
        dZ2 = dA2 * self._relu_derivative(Z2)
        dW2 = np.dot(A1.T, dZ2)
        db2 = np.sum(dZ2, axis=0, keepdims=True)

        dA1 = np.dot(dZ2, self.W2.T)
        dZ1 = dA1 * self._relu_derivative(Z1)
        dW1 = np.dot(X.T, dZ1)
        db1 = np.sum(dZ1, axis=0, keepdims=True)

        return dW1, db1, dW2, db2, dW3, db3

    def _binary_cross_entropy(self, y_true, y_pred):
        eps = 1e-12
        y_pred = np.clip(y_pred, eps, 1.0 - eps)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

    def fit(self, X, y):
        n_features = X.shape[1]
        self._init_params(n_features)

        y = y.reshape(-1, 1)

        n_samples = X.shape[0]

        for epoch in range(1, self.epochs + 1):
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n_samples, self.batch_size):
                end = start + self.batch_size
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]

                A1, A2, A3, cache = self._forward(X_batch)

                dW1, db1, dW2, db2, dW3, db3 = self._backward(
                    X_batch, y_batch, cache, A1, A2, A3
                )

                self.vW1 = self.momentum * self.vW1 + dW1
                self.W1 -= self.learning_rate * self.vW1
                self.vb1 = self.momentum * self.vb1 + db1
                self.b1 -= self.learning_rate * self.vb1

                self.vW2 = self.momentum * self.vW2 + dW2
                self.W2 -= self.learning_rate * self.vW2
                self.vb2 = self.momentum * self.vb2 + db2
                self.b2 -= self.learning_rate * self.vb2

                self.vW3 = self.momentum * self.vW3 + dW3
                self.W3 -= self.learning_rate * self.vW3
                self.vb3 = self.momentum * self.vb3 + db3
                self.b3 -= self.learning_rate * self.vb3

                batch_loss = self._binary_cross_entropy(y_batch, A3)
                epoch_loss += batch_loss
                n_batches += 1

            avg_loss = epoch_loss / n_batches
            self.loss_history.append(avg_loss)

            if epoch % 50 == 0 or epoch == 1:
                print(f"Epoca {epoch:3d}/{self.epochs} | Loss: {avg_loss:.6f}")

    def predict(self, X):
        _, _, A3, _ = self._forward(X)
        return (A3 >= 0.5).astype(int).flatten()

    def predict_proba(self, X):
        _, _, A3, _ = self._forward(X)
        return A3.flatten()

    def save(self, path):
        """Serializa hiperparametros e pesos treinados via pickle."""
        state = {
            "hyperparams": {
                "hidden1": self.hidden1,
                "hidden2": self.hidden2,
                "learning_rate": self.learning_rate,
                "momentum": self.momentum,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "random_state": self.random_state,
            },
            "weights": {
                "W1": self.W1, "b1": self.b1,
                "W2": self.W2, "b2": self.b2,
                "W3": self.W3, "b3": self.b3,
            },
            "loss_history": self.loss_history,
        }
        with open(path, "wb") as f:
            pickle.dump(state, f)

    @classmethod
    def load(cls, path):
        """Reconstroi um modelo treinado a partir de um arquivo pickle."""
        with open(path, "rb") as f:
            state = pickle.load(f)

        model = cls(**state["hyperparams"])
        for name, value in state["weights"].items():
            setattr(model, name, value)
        model.loss_history = state.get("loss_history", [])
        return model


def accuracia(y_true, y_pred):
    return np.mean(y_true == y_pred)


def precisao(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def recall(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def f1_score(y_true, y_pred):
    prec = precisao(y_true, y_pred)
    rec = recall(y_true, y_pred)
    return 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0


def matriz_confusao_manual(y_true, y_pred):
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]])


def main():
    print("=== MLP Hard-Coded — Classificacao Binaria (Normal vs Anomalia) ===\n")

    df = pd.read_csv("data/processed/ml_features.csv")

    exclude_cols = [
        "file_id", "filename", "file_path", "condition",
        "condition_binary", "machine_type", "model_id",
    ]
    id_cols = [c for c in df.columns if c.endswith("_id") and c != "file_id"]
    exclude_cols.extend(id_cols)

    feature_cols = [c for c in df.columns if c not in exclude_cols]
    numeric_df = df[feature_cols].select_dtypes(include=["number"])
    X = numeric_df.fillna(0).values
    y = df["condition_binary"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    mlp = HardCodedMLP()
    inicio = time.time()
    mlp.fit(X_train, y_train)
    fim = time.time()
    tempo_ms = (fim - inicio) * 1000

    y_pred = mlp.predict(X_test)

    acc = accuracia(y_test, y_pred)
    prec = precisao(y_test, y_pred)
    rec = recall(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = matriz_confusao_manual(y_test, y_pred)

    print("\n" + "=" * 50)
    print("RESULTADOS — Hard-Code MLP Binario")
    print("=" * 50)
    print(f"Acuracia:        {acc:.4f}")
    print(f"Precisao:        {prec:.4f}")
    print(f"Recall:          {rec:.4f}")
    print(f"F1-Score:        {f1:.4f}")
    print(f"Tempo de treino: {tempo_ms:,.2f} ms")
    print()
    print("Matriz de Confusao (Linha=Real, Coluna=Predito):")
    print(f"  Normal (TN): {cm[0,0]:>6}  Falso Positivo: {cm[0,1]:>6}")
    print(f"  Falso Neg:   {cm[1,0]:>6}  Anomalia (TP): {cm[1,1]:>6}")
    print("=" * 50)


if __name__ == "__main__":
    main()
