import sys
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
import pytest


def test_hardcode_mlp_binary_fit_predict():
    """Hard-code MLP should train and predict binary without errors"""
    from ml.hard_code.neural_network_hardcode import prever, treinar

    np.random.seed(42)
    X = np.random.randn(200, 20)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    model = treinar(X, y, epocas=50, batch_size=32)
    preds = prever(model, X)

    assert len(preds) == 200
    assert set(preds).issubset({0, 1})


def test_hardcode_mlp_predict_proba():
    """predict_proba should return probabilities between 0 and 1"""
    from ml.hard_code.neural_network_hardcode import prever_probabilidade, treinar

    np.random.seed(42)
    X = np.random.randn(100, 10)
    y = (X[:, 0] > 0).astype(int)

    model = treinar(X, y, epocas=30, batch_size=32)
    probs = prever_probabilidade(model, X)

    assert len(probs) == 100
    assert np.all(probs >= 0) and np.all(probs <= 1)


def test_hardcode_mlp_loss_decreases():
    """Loss should generally decrease during training"""
    from ml.hard_code.neural_network_hardcode import treinar

    np.random.seed(42)
    X = np.random.randn(300, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    model = treinar(X, y, epocas=100, batch_size=64)

    loss_history = model["historico_perda"]
    assert len(loss_history) == 100
    assert loss_history[0] > loss_history[-1]


def test_hardcode_mlp_save_load_roundtrip(tmp_path):
    """Modelo salvo com pickle deve reproduzir as mesmas predicoes ao carregar"""
    from ml.hard_code.neural_network_hardcode import (
        carregar_modelo,
        prever,
        prever_probabilidade,
        salvar_modelo,
        treinar,
    )

    np.random.seed(42)
    X = np.random.randn(150, 12)
    y = (X[:, 0] - X[:, 2] > 0).astype(int)

    model = treinar(X, y, epocas=30, batch_size=32)

    path = tmp_path / "mlp_hardcode.pkl"
    salvar_modelo(model, path)
    loaded = carregar_modelo(path)

    assert np.array_equal(prever(model, X), prever(loaded, X))
    assert np.allclose(prever_probabilidade(model, X), prever_probabilidade(loaded, X))


def test_sklearn_mlp_binary():
    """Sklearn MLP should train binary classification"""
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import accuracy_score

    np.random.seed(42)
    X = np.random.randn(200, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    model = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        max_iter=200,
        random_state=42,
    )
    model.fit(X, y)
    preds = model.predict(X)
    acc = accuracy_score(y, preds)

    assert acc > 0.5
