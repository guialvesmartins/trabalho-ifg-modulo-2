"""
Rede Neural Feedforward (MLP) implementada do zero com NumPy.

Arquitetura:
    Entrada (N features) -> Hidden1 (64, ReLU) -> Hidden2 (32, ReLU) -> Saída (5, Softmax)

Classes de saída: ratings 2, 3, 4, 5 mapeados para índices 0, 1, 2, 3 respectivamente.
Otimizador: mini-batch SGD com momento.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class HardCodedMLP:
    """
    MLP com duas camadas ocultas, implementada manualmente com NumPy.

    Parâmetros
    ----------
    hidden1 : int
        Número de neurônios na primeira camada oculta (default: 64).
    hidden2 : int
        Número de neurônios na segunda camada oculta (default: 32).
    learning_rate : float
        Taxa de aprendizado para o SGD (default: 0.01).
    momentum : float
        Fator de momento para o SGD (default: 0.9).
    epochs : int
        Número de épocas de treinamento (default: 300).
    batch_size : int
        Tamanho do mini-batch (default: 32).
    random_state : int
        Semente para reprodutibilidade (default: 42).
    """

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

    def _init_params(self, n_features, num_classes):
        """Inicializa pesos com He e vieses com zeros."""
        np.random.seed(self.random_state)

        # He initialization: sqrt(2 / fan_in)
        self.W1 = np.random.randn(n_features, self.hidden1) * np.sqrt(2.0 / n_features)
        self.b1 = np.zeros((1, self.hidden1))

        self.W2 = np.random.randn(self.hidden1, self.hidden2) * np.sqrt(2.0 / self.hidden1)
        self.b2 = np.zeros((1, self.hidden2))

        self.W3 = np.random.randn(self.hidden2, num_classes) * np.sqrt(2.0 / self.hidden2)
        self.b3 = np.zeros((1, num_classes))

        # Termos de momento (inicializados com zeros)
        self.vW1 = np.zeros_like(self.W1)
        self.vb1 = np.zeros_like(self.b1)
        self.vW2 = np.zeros_like(self.W2)
        self.vb2 = np.zeros_like(self.b2)
        self.vW3 = np.zeros_like(self.W3)
        self.vb3 = np.zeros_like(self.b3)

    def _relu(self, Z):
        """Ativação ReLU: max(0, Z)."""
        return np.maximum(0, Z)

    def _relu_derivative(self, Z):
        """Derivada da ReLU: 1 se Z > 0, senão 0."""
        return (Z > 0).astype(float)

    def _softmax(self, Z):
        """
        Softmax com estabilidade numérica (subtrai o máximo por linha).
        """
        Z_stable = Z - np.max(Z, axis=1, keepdims=True)
        exp_Z = np.exp(Z_stable)
        return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)

    def _forward(self, X):
        """
        Forward pass completo.

        Retorna
        -------
        A1, A2, A3 : ndarray
            Ativações de cada camada.
        cache : tuple
            (Z1, Z2, Z3) para uso no backward pass.
        """
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = self._relu(Z1)

        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self._relu(Z2)

        Z3 = np.dot(A2, self.W3) + self.b3
        A3 = self._softmax(Z3)

        cache = (Z1, Z2, Z3)
        return A1, A2, A3, cache

    def _backward(self, X, y_onehot, cache, A1, A2, A3):
        """
        Backpropagation calculando os gradientes de W e b.

        Retorna
        -------
        dW1, db1, dW2, db2, dW3, db3 : ndarray
            Gradientes dos parâmetros.
        """
        m = X.shape[0]
        Z1, Z2, Z3 = cache

        # Gradiente da camada de saída (softmax + cross-entropy)
        dZ3 = A3 - y_onehot
        dW3 = np.dot(A2.T, dZ3) / m
        db3 = np.sum(dZ3, axis=0, keepdims=True) / m

        # Gradiente da segunda camada oculta
        dA2 = np.dot(dZ3, self.W3.T)
        dZ2 = dA2 * self._relu_derivative(Z2)
        dW2 = np.dot(A1.T, dZ2) / m
        db2 = np.sum(dZ2, axis=0, keepdims=True) / m

        # Gradiente da primeira camada oculta
        dA1 = np.dot(dZ2, self.W2.T)
        dZ1 = dA1 * self._relu_derivative(Z1)
        dW1 = np.dot(X.T, dZ1) / m
        db1 = np.sum(dZ1, axis=0, keepdims=True) / m

        return dW1, db1, dW2, db2, dW3, db3

    def _cross_entropy_loss(self, y_onehot, A3):
        """
        Categorical cross-entropy com epsilon para evitar log(0).
        """
        eps = 1e-12
        A3_clipped = np.clip(A3, eps, 1.0 - eps)
        # Soma sobre classes, média sobre exemplos
        loss = -np.mean(np.sum(y_onehot * np.log(A3_clipped), axis=1))
        return loss

    def fit(self, X, y):
        """
        Treina a rede neural com mini-batch SGD + momento.

        Parâmetros
        ----------
        X : ndarray de shape (n_amostras, n_features)
        y : ndarray de shape (n_amostras,)
            Rótulos com valores originais (2, 3, 4, 5).
        """
        n_features = X.shape[1]
        
        # Classes reais presentes nos dados
        self.classes_ = np.unique(y)
        num_classes = len(self.classes_)
        self._init_params(n_features, num_classes)

        # Mapeia ratings para indices 0..(num_classes-1)
        class_to_idx = {c: i for i, c in enumerate(self.classes_)}
        y_idx = np.array([class_to_idx[r] for r in y])

        # One-hot encoding dinamico
        y_onehot = np.zeros((y_idx.shape[0], num_classes))
        y_onehot[np.arange(y_idx.shape[0]), y_idx] = 1

        n_samples = X.shape[0]

        for epoch in range(1, self.epochs + 1):
            # Embaralha os dados a cada época
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y_onehot[indices]

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n_samples, self.batch_size):
                end = start + self.batch_size
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]

                # Forward pass
                A1, A2, A3, cache = self._forward(X_batch)

                # Backward pass
                dW1, db1, dW2, db2, dW3, db3 = self._backward(
                    X_batch, y_batch, cache, A1, A2, A3
                )

                # Atualização dos parâmetros com momento
                # W = W - lr * vW,  vW = momentum * vW + dW
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

                # Acumula loss do batch
                batch_loss = self._cross_entropy_loss(y_batch, A3)
                epoch_loss += batch_loss
                n_batches += 1

            # Loss média da época
            avg_loss = epoch_loss / n_batches
            self.loss_history.append(avg_loss)

            if epoch % 50 == 0 or epoch == 1:
                print(f"Época {epoch:3d}/{self.epochs} | Loss: {avg_loss:.6f}")

    def predict(self, X):
        """
        Retorna as predições de classe mapeadas de volta para os ratings originais.

        Retorna
        -------
        ndarray de shape (n_amostras,)
            Ratings preditos [2, 3, 4, 5].
        """
        _, _, A3, _ = self._forward(X)
        # Índice da classe com maior probabilidade
        idx_pred = np.argmax(A3, axis=1)
        return self.classes_[idx_pred]

    def predict_proba(self, X):
        """
        Retorna as probabilidades softmax para cada classe.
        """
        _, _, A3, _ = self._forward(X)
        return A3


def accuracia(y_true, y_pred):
    """Acurácia: proporção de predições corretas."""
    return np.mean(y_true == y_pred)


def precisao_macro(y_true, y_pred, classes):
    """Precisão macro: média das precisões por classe."""
    precisions = []
    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        if tp + fp == 0:
            precisions.append(0.0)
        else:
            precisions.append(tp / (tp + fp))
    return np.mean(precisions)


def recall_macro(y_true, y_pred, classes):
    """Recall macro: média dos recalls por classe."""
    recalls = []
    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))
        if tp + fn == 0:
            recalls.append(0.0)
        else:
            recalls.append(tp / (tp + fn))
    return np.mean(recalls)


def f1_score_macro(y_true, y_pred, classes):
    """F1-Score macro: média dos F1 por classe."""
    f1s = []
    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        if prec + rec == 0:
            f1s.append(0.0)
        else:
            f1s.append(2 * (prec * rec) / (prec + rec))
    return np.mean(f1s)


def matriz_confusao_manual(y_true, y_pred, classes):
    """
    Monta a matriz de confusão manualmente.

    Retorna
    -------
    ndarray (n_classes, n_classes)
        Matriz de confusão.
    """
    n_classes = len(classes)
    cm = np.zeros((n_classes, n_classes), dtype=int)
    for i, true_cls in enumerate(classes):
        for j, pred_cls in enumerate(classes):
            cm[i, j] = np.sum((y_true == true_cls) & (y_pred == pred_cls))
    return cm


def main():
    """Pipeline principal: carrega dados, treina e avalia a MLP."""

    # 1. Carregar dados
    df = pd.read_csv("data/processed/ml_features.csv")

    # 2. Separar features e target
    cols_excluir = ["product_id", "product_name", "review_id", "rating"]
    feature_cols = [c for c in df.columns if c not in cols_excluir]
    X = df[feature_cols].values.astype(float)
    y = df["rating"].values.astype(int)

    # 3. Preencher NaN com 0
    X = np.nan_to_num(X, nan=0.0)

    # 4. Split treino/teste 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 5. Padronizar features (média 0, desvio 1)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # 6. Treinar modelo
    mlp = HardCodedMLP()
    inicio = time.time()
    mlp.fit(X_train, y_train)
    fim = time.time()
    tempo_ms = (fim - inicio) * 1000

    # 7. Predição no teste
    y_pred = mlp.predict(X_test)

    # 8. Métricas manuais
    classes = [2, 3, 4, 5]
    acc = accuracia(y_test, y_pred)
    prec = precisao_macro(y_test, y_pred, classes)
    rec = recall_macro(y_test, y_pred, classes)
    f1 = f1_score_macro(y_test, y_pred, classes)

    # 9. Matriz de confusão
    cm = matriz_confusao_manual(y_test, y_pred, classes)

    # 10. Resultados
    print("\n" + "=" * 50)
    print("RESULTADOS - Rede Neural Hard-Coded")
    print("=" * 50)
    print(f"Acurácia:        {acc:.4f}")
    print(f"Precisão (macro): {prec:.4f}")
    print(f"Recall (macro):   {rec:.4f}")
    print(f"F1-Score (macro): {f1:.4f}")
    print(f"Tempo de treino:  {tempo_ms:,.2f} ms")
    print()
    print("Matriz de Confusão:")
    print("(Linha = Real, Coluna = Predito)")
    print(f"{'':>8}  Pred 2  Pred 3  Pred 4  Pred 5")
    for i, cls in enumerate(classes):
        print(f"  Real {cls}:   {cm[i,0]:>6}  {cm[i,1]:>6}  {cm[i,2]:>6}  {cm[i,3]:>6}")
    print("=" * 50)


if __name__ == "__main__":
    main()
