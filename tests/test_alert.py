import alert

import os
import pandas as pd
import pytest


dirpath = os.path.dirname(os.path.abspath(__file__))

def path_to_datafile(filename: str) -> str:
    return os.path.join(dirpath, "data", filename)

def df_from_datafile(filename: str) -> pd.DataFrame:
    return pd.read_pickle(path_to_datafile(filename))

def df_with_regressions(expected_regressions: str) -> pd.DataFrame:
    return pd.read_pickle(path_to_datafile(expected_regressions))

@pytest.mark.parametrize(
    "filename, expected_regressions",
    [
        ("outFeb22.pkl", "output-test.pkl")
    ],
)

def test_find_regressions(filename: str, expected_regressions: str):
    df = df_from_datafile(filename)
    regressions = alert.find_regressions(df)
    regressions_results = df_from_datafile(expected_regressions)
    
    assert regressions.equals(regressions_results)