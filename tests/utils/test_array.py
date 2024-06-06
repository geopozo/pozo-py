import pytest
import numpy as np
import pandas as pd
import polars as pl
import pozo.utils.array as pzutils

list_data = [float("inf"), -float("inf"), float("nan")]
list_data_irregular = [0, 20, 40, 50, 70, 90, 300, 301, 330, 400]
np_data = np.linspace(0, 2000, num=50, endpoint=True)
np_data_irregular = np.array(list_data_irregular)
series = pd.Series(np_data)
series_data_irregular = pd.Series(np_data_irregular)
df_pandas = pd.DataFrame({"depth": np_data})
df_pandas_irregular = pd.DataFrame({"depth": list_data_irregular})
series_polars = pl.Series(np_data)
series_polars_data_irregular = pl.Series(np_data_irregular)
df_polars = pl.DataFrame({"depth": np_data})
df_polars_irregular = pl.DataFrame({"depth": list_data_irregular})



def test_summarize_array():
    assert pzutils.summarize_array(np_data) is not None
    assert pzutils.summarize_array(df_polars["depth"]) is not None
    assert pzutils.summarize_array(df_polars_irregular["depth"]) is not None
    assert pzutils.summarize_array(series) is not None
    assert pzutils.summarize_array(series_polars) is not None
    # assert pzutils.summarize_array(list_data) is None #This function doesn't use elements like inf or NaN
    assert pzutils.summarize_array(np_data_irregular) is not None
    assert pzutils.summarize_array(df_pandas["depth"]) is not None
    assert pzutils.summarize_array(df_pandas_irregular["depth"]) is not None
    assert pzutils.summarize_array(series_data_irregular) is not None
    assert pzutils.summarize_array(series_polars_data_irregular) is not None
    assert pzutils.summarize_array(list_data_irregular) is not None


def test_is_close():
    assert pzutils.is_close(np_data[0], np_data[-1]) is not None
    assert pzutils.is_close(series.iloc[0], series.iloc[-1]) is not None
    assert (
        pzutils.is_close(df_pandas_irregular["depth"].iloc[0], df_pandas_irregular["depth"].iloc[-1])
        is not None
    )
    assert pzutils.is_close(series_polars[0], series_polars[-1]) is not None
    assert pzutils.is_close(list_data[0], list_data[-1]) is not None
    assert pzutils.is_close(np_data_irregular[0], np_data_irregular[-1]) is not None
    assert pzutils.is_close(df_polars_irregular["depth"][0], df_polars_irregular["depth"][-1]) is not None
    assert (
        pzutils.is_close(series_data_irregular.iloc[0], series_data_irregular.iloc[-1])
        is not None
    )
    assert (
        pzutils.is_close(
            series_polars_data_irregular[0], series_polars_data_irregular[-1]
        )
        is not None
    )
    assert pzutils.is_close(list_data_irregular[0], list_data_irregular[-1]) is not None


def test_hash_array():
    assert pzutils.hash_array(np_data) == "fa965b73eaa75caaadcecd13d1df6aff"
    assert pzutils.hash_array(df_pandas_irregular["depth"]) == "744578fc32c6e5300c7c0784a88a4fdb"
    assert pzutils.hash_array(series) == "fa965b73eaa75caaadcecd13d1df6aff"
    assert pzutils.hash_array(series_polars) == "fa965b73eaa75caaadcecd13d1df6aff"
    assert (
        pzutils.hash_array(list_data) == "16e83a215505f98e905476615a56cc40"
    )  # This has components like [float("inf"), -float("inf"), float("nan")]
    assert pzutils.hash_array(np_data_irregular) == "d8cd63104ec584b4d83928cb8ba88639"
    assert pzutils.hash_array(df_polars_irregular["depth"]) == "744578fc32c6e5300c7c0784a88a4fdb"
    assert (
        pzutils.hash_array(series_data_irregular) == "d8cd63104ec584b4d83928cb8ba88639"
    )
    assert (
        pzutils.hash_array(series_polars_data_irregular)
        == "d8cd63104ec584b4d83928cb8ba88639"
    )
    assert pzutils.hash_array(list_data_irregular) == "d8cd63104ec584b4d83928cb8ba88639"


def test_min():
    assert pzutils.min(np_data) == 0
    assert pzutils.min(df_pandas_irregular["depth"]) == 0
    assert pzutils.min(series) == 0
    assert pzutils.min(series_polars) == 0
    assert str(pzutils.min(list_data)) == '-inf'
    assert pzutils.min(np_data_irregular) == 0
    assert pzutils.min(df_polars_irregular["depth"]) == 0
    assert pzutils.min(series_data_irregular) == 0
    assert pzutils.min(series_polars_data_irregular) == 0
    assert pzutils.min(list_data_irregular) == 0


def test_max():
    assert pzutils.max(np_data) == 2000
    assert pzutils.max(df_pandas_irregular["depth"]) == 400
    assert pzutils.max(series) == 2000
    assert pzutils.max(series_polars) == 2000
    assert str(pzutils.max(list_data)) == 'inf'
    assert pzutils.max(np_data_irregular) == 400
    assert pzutils.max(df_polars_irregular["depth"]) == 400
    assert pzutils.max(series_data_irregular) == 400
    assert pzutils.max(series_polars_data_irregular) == 400
    assert pzutils.max(list_data_irregular) == 400


def test_abs():
    assert pzutils.abs(np_data) is not None
    assert pzutils.abs(df_pandas_irregular["depth"]) is not None
    assert pzutils.abs(series) is not None
    assert pzutils.abs(series_polars) is not None
    assert pzutils.abs(list_data) is not None
    assert pzutils.abs(np_data_irregular) is not None
    assert pzutils.abs(df_polars_irregular["depth"]) is not None
    assert pzutils.abs(series_data_irregular) is not None
    assert pzutils.abs(series_polars_data_irregular) is not None
    assert pzutils.abs(list_data_irregular) is not None


def test_isfinite():
    assert pzutils.isfinite(np_data).all()
    assert pzutils.isfinite(df_pandas_irregular["depth"]).all()
    assert pzutils.isfinite(series).all()
    assert pzutils.isfinite(series_polars).all()
    assert pzutils.isfinite(list_data) is not None
    assert pzutils.isfinite(np_data_irregular).all()
    assert pzutils.isfinite(df_polars_irregular["depth"]).all()
    assert pzutils.isfinite(series_data_irregular).all()
    assert pzutils.isfinite(series_polars_data_irregular).all()
    assert pzutils.isfinite(list_data_irregular).all()


def test_isnan():
    assert pzutils.isnan(np_data) is not None
    assert pzutils.isnan(df_pandas_irregular["depth"]) is not None
    assert pzutils.isnan(series) is not None
    assert pzutils.isnan(series_polars) is not None
    assert pzutils.isnan(list_data) is not None
    assert pzutils.isnan(np_data_irregular) is not None
    assert pzutils.isnan(df_polars_irregular["depth"]) is not None
    assert pzutils.isnan(series_data_irregular) is not None
    assert pzutils.isnan(series_polars_data_irregular) is not None
    assert pzutils.isnan(list_data_irregular) is not None


def test_count_nonzero():
    assert pzutils.count_nonzero(np_data) == 49
    assert pzutils.count_nonzero(df_pandas_irregular["depth"]) == 9
    assert pzutils.count_nonzero(series) == 49
    assert pzutils.count_nonzero(series_polars) == 49
    assert pzutils.count_nonzero(list_data) == 3
    assert pzutils.count_nonzero(np_data_irregular) == 9
    assert pzutils.count_nonzero(df_polars_irregular["depth"]) == 9
    assert pzutils.count_nonzero(series_data_irregular) == 9
    assert pzutils.count_nonzero(series_polars_data_irregular) == 9
    assert pzutils.count_nonzero(list_data_irregular) == 9


def test_nanquantile():
    assert pzutils.nanquantile(np_data, .5) == 1000
    assert pzutils.nanquantile(df_pandas_irregular["depth"], .5) == 80
    assert pzutils.nanquantile(series, .5) == 1000
    assert pzutils.nanquantile(series_polars, .5) == 1000
    assert str(pzutils.nanquantile(list_data, .5)) == 'nan'
    assert pzutils.nanquantile(np_data_irregular, .5) == 80
    assert pzutils.nanquantile(df_polars_irregular["depth"], .5) == 80
    assert pzutils.nanquantile(series_data_irregular, .5) == 80
    assert pzutils.nanquantile(series_polars_data_irregular, .5) == 80
    assert pzutils.nanquantile(list_data_irregular, .5) == 80


def test_round():
    assert pzutils.round(np_data).any()
    assert pzutils.round(df_pandas_irregular["depth"]).any()
    assert pzutils.round(series).any()
    assert (pzutils.round(series_polars) != 0).any()
    assert pzutils.round(list_data).any()
    assert pzutils.round(np_data_irregular).any()
    assert (pzutils.round(df_polars_irregular["depth"]) != 0).any()
    assert pzutils.round(series_data_irregular).any()
    assert (pzutils.round(series_polars_data_irregular) != 0).any()
    assert pzutils.round(list_data_irregular).any()


def test_append():
    assert pzutils.append(np_data, 1) is not None
    assert pzutils.append(df_pandas_irregular["depth"], [2,3,4]) is not None
    assert pzutils.append(series, (2,3,4,5,6,7)) is not None
    assert pzutils.append(series_polars, 8) is not None
    assert pzutils.append(list_data, np.array([1,2,3,4])) is not None
    assert pzutils.append(np_data_irregular, (2,3,4,5,6,7)) is not None
    assert pzutils.append(df_polars_irregular["depth"], np.array([1,2,3,4])) is not None
    assert pzutils.append(series_data_irregular, np.array([1,2,3,4])) is not None
    assert pzutils.append(series_polars_data_irregular, (2,3,4,5,6,7)) is not None
    assert pzutils.append(list_data_irregular, 1000) is not None
