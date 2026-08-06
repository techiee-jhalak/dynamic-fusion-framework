from pathlib import Path
import os
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))


def _coerce_text(value):
    return ' '.join(str(value).strip().split()) if pd.notna(value) else ''


def _infer_sentiment(values):
    numeric_values = []
    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            continue

    if len(numeric_values) < 5:
        return 'neutral'

    overall_fscore = numeric_values[4]
    if overall_fscore >= 0.65:
        return 'positive'
    if overall_fscore <= 0.45:
        return 'negative'
    return 'neutral'


def load_sail_to_df(data_dir):
    data_dir = Path(data_dir)
    if not data_dir.is_absolute():
        data_dir = ROOT / data_dir

    workbook_path = data_dir / 'SAIL_CodeMixed_2017_results.xlsx'
    if not workbook_path.exists():
        raise FileNotFoundError(f'SAIL workbook not found: {workbook_path}')

    sheet = pd.read_excel(workbook_path, sheet_name='Sheet1')
    rows = []
    for _, row in sheet.iterrows():
        values = [str(value).strip() for value in row.tolist() if pd.notna(value) and str(value).strip()]
        if not values:
            continue
        if values and values[0].lower().startswith('systemid'):
            continue
        if len(values) < 5:
            continue
        if re.fullmatch(r'\d+(\.\d+)?', values[0]) or values[0].lower() in {'hi-en', 'bn-en'}:
            continue

        text = ' '.join(values)
        sentiment = _infer_sentiment(values)
        rows.append({'text': text, 'sentiment': sentiment})

    if not rows:
        return pd.DataFrame(columns=['text', 'sentiment'])

    df = pd.DataFrame(rows)
    df['text'] = df['text'].apply(_coerce_text)
    df = df[df['text'].str.len() > 0].copy()
    df['sentiment'] = df['sentiment'].map({'positive': 'positive', 'negative': 'negative', 'neutral': 'neutral'})
    df['label'] = df['sentiment'].map({'positive': 2, 'negative': 0, 'neutral': 1}).astype(int)
    return df


def main():
    data_dir = ROOT / 'datasets' / 'sail_codemixed'
    output_path = ROOT / 'data' / 'sail_cleaned.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = load_sail_to_df(data_dir)
    df.to_csv(output_path, index=False)
    print(f'Loaded {len(df)} samples into {output_path}')


if __name__ == '__main__':
    main()
