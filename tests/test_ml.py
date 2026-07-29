import sys
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
import pytest


def test_hardcode_naive_bayes_fit_predict():
    """Hard-code NB should train and predict without errors"""
    from ml.hard_code.naive_bayes_hardcode import HardCodedNaiveBayes

    X = pd.DataFrame({
        'tfidf_great': [1, 0, 1],
        'tfidf_bad': [0, 1, 0],
        'tfidf_product': [1, 1, 0],
        'not_tfidf_feature': [0.5, 0.3, 0.8],
    })
    y = np.array([5, 1, 5])

    model = HardCodedNaiveBayes(alpha=1.0)
    model.fit(X, y)
    preds = model.predict(X)

    assert len(preds) == 3
    assert set(preds).issubset({1, 2, 3, 4, 5})


def test_hardcode_predict_proba():
    """predict_proba should return valid probability distribution"""
    from ml.hard_code.naive_bayes_hardcode import HardCodedNaiveBayes

    X = pd.DataFrame({
        'tfidf_great': [1, 0],
        'tfidf_bad': [0, 1],
    })
    y = np.array([5, 1])

    model = HardCodedNaiveBayes(alpha=1.0)
    model.fit(X, y)
    probs = model.predict_proba(X)

    assert probs.shape == (2, 5)
    assert np.allclose(probs.sum(axis=1), 1.0)
    assert np.all(probs >= 0) and np.all(probs <= 1)


def test_binarize_features():
    """_binarize_features should convert numeric to binary"""
    from ml.hard_code.naive_bayes_hardcode import HardCodedNaiveBayes

    X = pd.DataFrame({
        'tfidf_great': [0.5, 0.0, 0.01, 0.0],
        'tfidf_bad': [0.0, 0.8, 0.0, 0.0],
        'regular_col': [5, 3, 8, 1],
    })
    y = np.array([5, 1, 5, 3])

    model = HardCodedNaiveBayes(alpha=1.0)
    model.fit(X, y)

    binarized = model._binarize_features(X)
    assert binarized['tfidf_great'].iloc[0] == 1
    assert binarized['tfidf_great'].iloc[1] == 0
    assert binarized['tfidf_great'].iloc[2] == 1
