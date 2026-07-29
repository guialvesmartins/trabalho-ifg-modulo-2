import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np
import pytest
from processing.process_structured import process_dataframe
from processing.extract_text_features import extract_features as extract_text
from processing.extract_image_features import extract_features as extract_image


def test_process_dataframe_handles_nulls():
    """Should drop rows with null rating"""
    df = pd.DataFrame({
        'product_name': ['A', 'B', 'C'],
        'discounted_price': ['₹499', '₹999', '₹299'],
        'actual_price': ['₹999', '₹1999', '₹599'],
        'discount_percentage': ['50%', '50%', '50%'],
        'rating': ['4.0', None, '3.5'],
        'rating_count': ['100', '50', '200'],
        'review_title': ['Good', 'OK', 'Bad'],
        'review_content': ['Great product', 'Fine', 'Bad product'],
        'img_link': ['url1', 'url2', 'url3'],
        'category': ['Electronics', 'Clothing', 'Electronics'],
        'about_product': ['', '', ''],
        'user_id': ['1', '2', '3'],
        'user_name': ['a', 'b', 'c'],
    })
    result = process_dataframe(df)
    assert len(result) == 2


def test_process_dataframe_dedup():
    """Should remove duplicate product names"""
    df = pd.DataFrame({
        'product_name': ['A', 'A', 'B'],
        'discounted_price': ['₹100', '₹100', '₹200'],
        'actual_price': ['₹200', '₹200', '₹400'],
        'discount_percentage': ['50%', '50%', '50%'],
        'rating': ['4.0', '4.0', '3.0'],
        'rating_count': ['10', '10', '20'],
        'review_title': ['Good', 'Good', 'OK'],
        'review_content': ['Great', 'Great', 'Fine'],
        'img_link': ['u1', 'u1', 'u2'],
        'category': ['Electronics', 'Electronics', 'Clothing'],
        'about_product': ['', '', ''],
        'user_id': ['1', '1', '2'],
        'user_name': ['a', 'a', 'b'],
    })
    result = process_dataframe(df)
    assert len(result) == 2


def test_extract_text_features_columns():
    """Should generate NLP feature columns"""
    df = pd.DataFrame({
        'review_title': ['Great', 'Bad'],
        'review_content': ['Amazing product, love it!', 'Terrible, waste of money.'],
        'rating': [5, 1],
        'product_name': ['P1', 'P2'],
    })
    result = extract_text(df)
    expected = ['review_length', 'word_count', 'polarity']
    for col in expected:
        assert col in result.columns


def test_polarity_range():
    """Polarity should be between -1 and 1"""
    df = pd.DataFrame({
        'review_title': ['Love it!', 'Hate it.'],
        'review_content': ['Amazing wonderful perfect great!', 'Terrible awful worst ever.'],
        'rating': [5, 1],
        'product_name': ['P1', 'P2'],
    })
    result = extract_text(df)
    assert result['polarity'].iloc[0] > 0
    assert result['polarity'].iloc[1] < 0
