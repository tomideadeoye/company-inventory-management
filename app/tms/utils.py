from collections.abc import Iterable
import pandas as pd


def read_csv_file(file) -> Iterable:
    """
    read csv and return a stream
    Args:
        file: A csv file
    Returns: a stream of rows
    """
    try:
        df = pd.read_csv(file, encoding="utf-8-sig")
        df.drop(df.filter(regex="Unnamed"), axis=1, inplace=True)
        df.fillna("", inplace=True)
        reader = list(df.T.to_dict().values())
        if len(df.columns) < 6:
            raise Exception("CSV header incomplete")
    except Exception as e:
        return str(e)
    return reader