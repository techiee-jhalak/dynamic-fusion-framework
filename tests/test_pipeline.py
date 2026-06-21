def test_preprocess_placeholder():
    from research_pipeline.scripts.preprocess import clean_text

    assert clean_text(" hi ") == "hi"
