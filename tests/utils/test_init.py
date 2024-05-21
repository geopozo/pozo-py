import pytest
import numpy as np
import pandas as pd
import polars as pl
import pozo.utils as pzutils

list_data = [float("inf"), -float("inf"), float("nan")]
list_data_irregular = [0, 20, 40, 50, 70, 90, 300, 301, 330, 400]
np_data = np.linspace(0, 2000, num=50, endpoint=True)
np_data_irregular = np.array(list_data_irregular)
series = pd.Series(np_data)
series_data_irregular = pd.Series(np_data_irregular)
df_pandas = pd.DataFrame({"depth": list_data_irregular})
series_polars = pl.Series(np_data)
series_polars_data_irregular = pl.Series(np_data_irregular)
df_polars = pl.DataFrame({"depth": list_data_irregular})


def test_summarize_array():
    assert pzutils.summarize_array(np_data) is not None
    assert pzutils.summarize_array(df_polars["depth"]) is not None
    assert pzutils.summarize_array(series) is not None
    assert pzutils.summarize_array(series_polars) is not None
    #assert pzutils.summarize_array(list_data) is None #This function doesn't use elements like inf or NaN
    assert pzutils.summarize_array(np_data_irregular) is not None
    assert pzutils.summarize_array(df_pandas["depth"]) is not None
    assert pzutils.summarize_array(series_data_irregular) is not None
    assert pzutils.summarize_array(series_polars_data_irregular) is not None
    assert pzutils.summarize_array(list_data_irregular) is None


def test_is_close():
    assert (
        pzutils.is_close(np_data[0], np_data[-1], True, np_data[1] - np_data[0], 0.001)
        is not None
    )
    assert (
        pzutils.is_close(series[0], series[-1], True, series[1] - series[0], 0.001)
        is not None
    )
    assert (
        pzutils.is_close(
            df_pandas["depth"][0],
            df_pandas["depth"][9],
            True,
            df_pandas[9] - df_pandas[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            series_polars[0],
            series_polars[-1],
            True,
            series_polars[1] - series_polars[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            list_data[0], list_data[-1], True, list_data[1] - list_data[0], 0.001
        )
        is not None
    )
    assert (
        pzutils.is_close(
            np_data_irregular[0],
            np_data_irregular[-1],
            True,
            np_data_irregular[1] - np_data_irregular[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            df_polars["depth"][0],
            df_polars["depth"][9],
            True,
            df_polars[9] - df_polars[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            series_data_irregular[0],
            series_data_irregular[-1],
            True,
            series_data_irregular[1] - series_data_irregular[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            series_polars_data_irregular[0],
            series_polars_data_irregular[-1],
            True,
            series_polars_data_irregular[1] - series_polars_data_irregular[0],
            0.001,
        )
        is not None
    )
    assert (
        pzutils.is_close(
            list_data_irregular[0],
            list_data_irregular[-1],
            True,
            list_data_irregular[1] - list_data_irregular[0],
            0.001,
        )
        is not None
    )


def test_hash_array():
    assert pzutils.hash_array(np_data) == 'fa965b73eaa75caaadcecd13d1df6aff'
    assert pzutils.hash_array(df_pandas["depth"]) == '744578fc32c6e5300c7c0784a88a4fdb'
    assert pzutils.hash_array(series) == 'fa965b73eaa75caaadcecd13d1df6aff'
    assert pzutils.hash_array(series_polars) == 'fa965b73eaa75caaadcecd13d1df6aff'
    assert pzutils.hash_array(list_data) == '16e83a215505f98e905476615a56cc40' # This has components like [float("inf"), -float("inf"), float("nan")]
    assert pzutils.hash_array(np_data_irregular) == 'd8cd63104ec584b4d83928cb8ba88639'
    assert pzutils.hash_array(df_polars["depth"]) == '744578fc32c6e5300c7c0784a88a4fdb'
    assert pzutils.hash_array(series_data_irregular) == 'd8cd63104ec584b4d83928cb8ba88639'
    assert pzutils.hash_array(series_polars_data_irregular) == 'd8cd63104ec584b4d83928cb8ba88639'
    assert pzutils.hash_array(list_data_irregular) == 'd8cd63104ec584b4d83928cb8ba88639'


def test_min():
    assert pzutils.min(np_data) is None
    assert pzutils.min(df_pandas["depth"]) is None
    assert pzutils.min(series) is None
    assert pzutils.min(series_polars) is None
    assert pzutils.min(list_data) is None
    assert pzutils.min(np_data_irregular) is None
    assert pzutils.min(df_polars["depth"]) is None
    assert pzutils.min(series_data_irregular) is None
    assert pzutils.min(series_polars_data_irregular) is None
    assert pzutils.min(list_data_irregular) is None


def test_max():
    assert pzutils.max(np_data) is None
    assert pzutils.max(df_pandas["depth"]) is None
    assert pzutils.max(series) is None
    assert pzutils.max(series_polars) is None
    assert pzutils.max(list_data) is None
    assert pzutils.max(np_data_irregular) is None
    assert pzutils.max(df_polars["depth"]) is None
    assert pzutils.max(series_data_irregular) is None
    assert pzutils.max(series_polars_data_irregular) is None
    assert pzutils.max(list_data_irregular) is None


def test_isfinite():
    assert pzutils.isfinite(np_data[0]) is None
    assert pzutils.isfinite(df_pandas["depth"]) is None
    assert pzutils.isfinite(series[0]) is None
    assert pzutils.isfinite(series_polars[0]) is None
    assert pzutils.isfinite(list_data[0]) is None
    assert pzutils.isfinite(np_data_irregular[0]) is None
    assert pzutils.isfinite(df_polars["depth"]) is None
    assert pzutils.isfinite(series_data_irregular[0]) is None
    assert pzutils.isfinite(series_polars_data_irregular[0]) is None
    assert pzutils.isfinite(list_data_irregular[0]) is None
