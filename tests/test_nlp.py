import sys
sys.path.insert(0, '.')
import pandas as pd
import pytest
from processing.extract_text_features import extract_features as extract_text


def test_review_length_computed():
    df = pd.DataFrame({
        'review_title': ['Test'],
        'review_content': ['This is a test review.'],
        'rating': [5],
        'product_name': ['P1'],
    })
    result = extract_text(df)
    assert result['review_length'].iloc[0] > 0
    assert result['word_count'].iloc[0] == 5
    assert result['sentence_count'].iloc[0] == 1


def test_complaint_detection():
    df = pd.DataFrame({
        'review_title': ['Disappointed'],
        'review_content': ['This product is terrible and a complete waste of money.'],
        'rating': [1],
        'product_name': ['P1'],
    })
    result = extract_text(df)
    assert result['contains_complaint'].iloc[0] == 1
    assert result['contains_praise'].iloc[0] == 0
    assert result['contains_price_mention'].iloc[0] == 1


def test_praise_detection():
    df = pd.DataFrame({
        'review_title': ['Amazing!'],
        'review_content': ['This is an excellent product, I love it and highly recommend.'],
        'rating': [5],
        'product_name': ['P1'],
    })
    result = extract_text(df)
    assert result['contains_praise'].iloc[0] == 1
    assert result['contains_complaint'].iloc[0] == 0
