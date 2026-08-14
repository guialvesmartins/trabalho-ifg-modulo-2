"""Rede neural MLP treinada "na mão", só com NumPy — classificação binária.

Esse código foi escrito passo a passo, de propósito, para mostrar como uma
rede neural aprende de verdade. Nada de TensorFlow, PyTorch ou autograd:
aqui a gente mesmo faz o forward, o backward (regra da cadeia) e atualiza
os pesos, uma camada de cada vez.

Arquitetura:
    entrada (96 features) -> 64 neurônios (ReLU)
                          -> 32 neurônios (ReLU)
                          -> 1 saída (sigmoid) = P(anomalia)

Para treinar direto no terminal:
    python ml/hard_code/neural_network_hardcode.py
"""

import pickle
import time

import numpy as np

# ---------------------------------------------------------------------------
# Hiperparâmetros (valores escolhidos "na mão" e testados por tentativa)
# ---------------------------------------------------------------------------
N_OCULTA_1 = 64          # neurônios da 1ª camada oculta
N_OCULTA_2 = 32          # neurônios da 2ª camada oculta
TAXA_APRENDIZADO = 0.01  # tamanho do passo do gradiente
MOMENTO = 0.9            # "inércia" do SGD (evita oscilar demais)
EPOCAS = 300             # quantas vezes vemos o dataset inteiro
TAMANHO_BATCH = 32       # amostras por passo de treino
SEMENTE = 42             # semente para o resultado ser sempre o mesmo


# ---------------------------------------------------------------------------
# Funções de ativação e suas derivadas
# ---------------------------------------------------------------------------
def relu(z):
    """ReLU: se z > 0 mantém z, senão vira 0."""
    return np.maximum(0, z)


def derivada_relu(z):
    """Derivada da ReLU: 1 quando z > 0, 0 caso contrário."""
    return (z > 0).astype(float)


def sigmoid(z):
    """Sigmoid: transforma qualquer número num valor entre 0 e 1."""
    z = np.clip(z, -500, 500)  # proteção para o exp não explodir
    return 1.0 / (1.0 + np.exp(-z))


# ---------------------------------------------------------------------------
# Inicialização dos pesos
# ---------------------------------------------------------------------------
def inicializar_pesos(n_features):
    """Cria pesos W e biases b de cada camada com valores pequenos.

    A inicialização He usa sqrt(2 / n_entradas): com a ReLU, isso impede
    que os sinais explodam ou sumam conforme a rede vai ficando mais funda.
    """
    np.random.seed(SEMENTE)

    # Camada 1: (features -> 64)
    W1 = np.random.randn(n_features, N_OCULTA_1) * np.sqrt(2.0 / n_features)
    b1 = np.zeros((1, N_OCULTA_1))

    # Camada 2: (64 -> 32)
    W2 = np.random.randn(N_OCULTA_1, N_OCULTA_2) * np.sqrt(2.0 / N_OCULTA_1)
    b2 = np.zeros((1, N_OCULTA_2))

    # Saída: (32 -> 1)
    W3 = np.random.randn(N_OCULTA_2, 1) * np.sqrt(2.0 / N_OCULTA_2)
    b3 = np.zeros((1, 1))

    return W1, b1, W2, b2, W3, b3


# ---------------------------------------------------------------------------
# Forward: da entrada até a saída
# ---------------------------------------------------------------------------
def forward(X, W1, b1, W2, b2, W3, b3):
    """Passa os dados pela rede e devolve o valor de cada camada.

    Camada 1:  Z1 = X·W1 + b1  -> ReLU -> A1
    Camada 2:  Z2 = A1·W2 + b2 -> ReLU -> A2
    Saída:     Z3 = A2·W3 + b3 -> sigmoid -> previsão (0..1)
    """
    Z1 = np.dot(X, W1) + b1
    A1 = relu(Z1)

    Z2 = np.dot(A1, W2) + b2
    A2 = relu(Z2)

    Z3 = np.dot(A2, W3) + b3
    saida = sigmoid(Z3)

    return A1, A2, saida, Z1, Z2, Z3


# ---------------------------------------------------------------------------
# Backward: quanto cada peso precisa mudar (regra da cadeia)
# ---------------------------------------------------------------------------
def backward(X, y, W2, W3, A1, A2, saida, Z1, Z2):
    """Calcula os gradientes propagando o erro da saída para trás.

    A derivada da binary cross-entropy combinada com a sigmoid resulta em
    (saida - y) — por isso o erro começa assim na última camada.
    """
    m = X.shape[0]

    # --- Camada de saída ------------------------------------------------
    dZ3 = (saida - y) / m
    dW3 = np.dot(A2.T, dZ3)
    db3 = np.sum(dZ3, axis=0, keepdims=True)

    # --- Camada 2 -------------------------------------------------------
    dA2 = np.dot(dZ3, W3.T)
    dZ2 = dA2 * derivada_relu(Z2)
    dW2 = np.dot(A1.T, dZ2)
    db2 = np.sum(dZ2, axis=0, keepdims=True)

    # --- Camada 1 -------------------------------------------------------
    dA1 = np.dot(dZ2, W2.T)
    dZ1 = dA1 * derivada_relu(Z1)
    dW1 = np.dot(X.T, dZ1)
    db1 = np.sum(dZ1, axis=0, keepdims=True)

    return dW1, db1, dW2, db2, dW3, db3


# ---------------------------------------------------------------------------
# Função de perda
# ---------------------------------------------------------------------------
def perda_bce(y, previsao):
    """Binary Cross-Entropy: mede o quanto a previsão erra o alvo."""
    eps = 1e-12
    previsao = np.clip(previsao, eps, 1.0 - eps)
    return -np.mean(y * np.log(previsao) + (1 - y) * np.log(1 - previsao))


# ---------------------------------------------------------------------------
# Treinamento (SGD em mini-batches + momento)
# ---------------------------------------------------------------------------
def treinar(X, y, epocas=EPOCAS, batch_size=TAMANHO_BATCH,
            learning_rate=TAXA_APRENDIZADO, momentum=MOMENTO, semente=SEMENTE):
    """Treina a rede e devolve um dicionário com todos os pesos.

    Passos do treino:
      1. embaralha as amostras;
      2. divide em mini-batches;
      3. para cada batch: forward -> calcula gradiente -> atualiza pesos;
      4. repete por `epocas` vezes, anotando a perda média de cada época.
    """
    n_features = X.shape[1]
    W1, b1, W2, b2, W3, b3 = inicializar_pesos(n_features)

    y = y.reshape(-1, 1)
    n_samples = X.shape[0]

    # "Velocidade" dos pesos — é isso que o momento guarda
    vW1 = np.zeros_like(W1)
    vb1 = np.zeros_like(b1)
    vW2 = np.zeros_like(W2)
    vb2 = np.zeros_like(b2)
    vW3 = np.zeros_like(W3)
    vb3 = np.zeros_like(b3)

    historico_perda = []

    for epoca in range(1, epocas + 1):
        # Embaralha para o treino não "viciar" na ordem dos dados
        indices = np.random.permutation(n_samples)
        X_emb = X[indices]
        y_emb = y[indices]

        perda_epoca = 0.0
        n_batches = 0

        for inicio in range(0, n_samples, batch_size):
            fim = inicio + batch_size
            X_batch = X_emb[inicio:fim]
            y_batch = y_emb[inicio:fim]

            # Forward do batch
            A1, A2, saida, Z1, Z2, Z3 = forward(X_batch, W1, b1, W2, b2, W3, b3)

            # Gradientes pelo backprop
            dW1, db1, dW2, db2, dW3, db3 = backward(
                X_batch, y_batch, W2, W3, A1, A2, saida, Z1, Z2
            )

            # Atualização com SGD + momento:
            #   v = momento*v + gradiente   (velocidade)
            #   peso = peso - taxa*v        (anda contra o gradiente)
            vW1 = momentum * vW1 + dW1
            W1 = W1 - learning_rate * vW1
            vb1 = momentum * vb1 + db1
            b1 = b1 - learning_rate * vb1

            vW2 = momentum * vW2 + dW2
            W2 = W2 - learning_rate * vW2
            vb2 = momentum * vb2 + db2
            b2 = b2 - learning_rate * vb2

            vW3 = momentum * vW3 + dW3
            W3 = W3 - learning_rate * vW3
            vb3 = momentum * vb3 + db3
            b3 = b3 - learning_rate * vb3

            perda_epoca += perda_bce(y_batch, saida)
            n_batches += 1

        historico_perda.append(perda_epoca / n_batches)

        if epoca == 1 or epoca % 50 == 0:
            print(f"Epoca {epoca:3d}/{epocas} | Loss: {historico_perda[-1]:.6f}")

    # Juntamos tudo num único "modelo" (um dicionário simples de arrays)
    modelo = {
        "W1": W1, "b1": b1,
        "W2": W2, "b2": b2,
        "W3": W3, "b3": b3,
        "historico_perda": historico_perda,
        "hiperparametros": {
            "camada_1": N_OCULTA_1,
            "camada_2": N_OCULTA_2,
            "learning_rate": learning_rate,
            "momentum": momentum,
            "epocas": epocas,
            "batch_size": batch_size,
            "semente": semente,
        },
    }
    return modelo


# ---------------------------------------------------------------------------
# Previsão
# ---------------------------------------------------------------------------
def prever(modelo, X):
    """Devolve 0 (normal) ou 1 (anomalia) para cada amostra."""
    _, _, saida, _, _, _ = forward(X, modelo["W1"], modelo["b1"],
                                   modelo["W2"], modelo["b2"],
                                   modelo["W3"], modelo["b3"])
    return (saida >= 0.5).astype(int).flatten()


def prever_probabilidade(modelo, X):
    """Devolve P(anomalia) em [0,1] para cada amostra."""
    _, _, saida, _, _, _ = forward(X, modelo["W1"], modelo["b1"],
                                   modelo["W2"], modelo["b2"],
                                   modelo["W3"], modelo["b3"])
    return saida.flatten()


# ---------------------------------------------------------------------------
# Salvar / carregar o modelo treinado
# ---------------------------------------------------------------------------
def salvar_modelo(modelo, caminho):
    """Serializa o modelo (pesos + histórico) via pickle."""
    with open(caminho, "wb") as f:
        pickle.dump(modelo, f)


def carregar_modelo(caminho):
    """Recarrega um modelo treinado anteriormente."""
    with open(caminho, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------
# Métricas calculadas "na mão" também
# ---------------------------------------------------------------------------
def acuracia(y_true, y_pred):
    return np.mean(y_true == y_pred)


def precisao(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def recall(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def f1(y_true, y_pred):
    p = precisao(y_true, y_pred)
    r = recall(y_true, y_pred)
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


def matriz_confusao(y_true, y_pred):
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]])


# ---------------------------------------------------------------------------
# Execução standalone
# ---------------------------------------------------------------------------
def main():
    print("=== MLP Hard-Coded — Classificacao Binaria (Normal vs Anomalia) ===\n")

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

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

    inicio = time.time()
    modelo = treinar(X_train, y_train)
    tempo_ms = (time.time() - inicio) * 1000

    y_pred = prever(modelo, X_test)

    acc = acuracia(y_test, y_pred)
    prec = precisao(y_test, y_pred)
    rec = recall(y_test, y_pred)
    f1_score = f1(y_test, y_pred)
    cm = matriz_confusao(y_test, y_pred)

    print("\n" + "=" * 50)
    print("RESULTADOS — Hard-Code MLP Binario")
    print("=" * 50)
    print(f"Acuracia:        {acc:.4f}")
    print(f"Precisao:        {prec:.4f}")
    print(f"Recall:          {rec:.4f}")
    print(f"F1-Score:        {f1_score:.4f}")
    print(f"Tempo de treino: {tempo_ms:,.2f} ms")
    print()
    print("Matriz de Confusao (Linha=Real, Coluna=Predito):")
    print(f"  Normal (TN): {cm[0,0]:>6}  Falso Positivo: {cm[0,1]:>6}")
    print(f"  Falso Neg:   {cm[1,0]:>6}  Anomalia (TP): {cm[1,1]:>6}")
    print("=" * 50)


if __name__ == "__main__":
    main()
