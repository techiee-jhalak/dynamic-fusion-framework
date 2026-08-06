import pandas as pd


def test_sail_loader_creates_labeled_columns():
    from scripts.load_sail import load_sail_to_df

    df = load_sail_to_df('datasets/sail_codemixed')

    assert isinstance(df, pd.DataFrame)
    assert {'text', 'sentiment'}.issubset(df.columns)
    assert not df.empty
    assert df['text'].str.len().gt(0).all()
    assert df['sentiment'].isin({'positive', 'negative', 'neutral'}).all()
