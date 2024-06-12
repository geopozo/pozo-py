import pytest
import numpy as np
import pandas as pd
import polars as pl
import pozo.utils.array as pzutils

list_data_irregular = [
    0,
    20,
    40,
    50,
    70,
    90,
    300,
    301,
    330,
    400,
    float("inf"),
    -float("inf"),
    float("nan"),
]
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
        pzutils.is_close(
            df_pandas_irregular["depth"].iloc[0], df_pandas_irregular["depth"].iloc[-1]
        )
        is not None
    )
    assert pzutils.is_close(series_polars[0], series_polars[-1]) is not None
    assert pzutils.is_close(np_data_irregular[0], np_data_irregular[-1]) is not None
    assert (
        pzutils.is_close(
            df_polars_irregular["depth"][0], df_polars_irregular["depth"][-1]
        )
        is not None
    )
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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, "fa965b73eaa75caaadcecd13d1df6aff"),
        (df_pandas_irregular["depth"], "16e98044c7a2e7fda3eabc23520d99ce"),
        (series, "fa965b73eaa75caaadcecd13d1df6aff"),
        (series_polars, "fa965b73eaa75caaadcecd13d1df6aff"),
        (np_data_irregular, "16e98044c7a2e7fda3eabc23520d99ce"),
        (df_polars_irregular["depth"], "16e98044c7a2e7fda3eabc23520d99ce"),
        (series_data_irregular, "16e98044c7a2e7fda3eabc23520d99ce"),
        (series_polars_data_irregular, "16e98044c7a2e7fda3eabc23520d99ce"),
        (list_data_irregular, "16e98044c7a2e7fda3eabc23520d99ce"),
    ],
    ids=[
        "hash_01",
        "hash_02",
        "hash_03",
        "hash_04",
        "hash_05",
        "hash_06",
        "hash_07",
        "hash_08",
        "hash_09",
    ],
)
def test_hash_array(test_input, expected):
    assert pzutils.hash_array(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, 0),
        (df_pandas_irregular["depth"], float("-inf")),
        (series, 0),
        (series_polars, 0),
        (np_data_irregular, float("-inf")),
        (df_polars_irregular["depth"], float("-inf")),
        (series_data_irregular, float("-inf")),
        (series_polars_data_irregular, float("-inf")),
        (list_data_irregular, float("-inf")),
    ],
    ids=[
        "min_01",
        "min_02",
        "min_03",
        "min_04",
        "min_05",
        "min_06",
        "min_07",
        "min_08",
        "min_09",
    ],
)
def test_min(test_input, expected):
    assert pzutils.min(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, 2000),
        (df_pandas_irregular["depth"], float("inf")),
        (series, 2000),
        (series_polars, 2000),
        (np_data_irregular, float("inf")),
        (df_polars_irregular["depth"], float("inf")),
        (series_data_irregular, float("inf")),
        (series_polars_data_irregular, float("inf")),
        (list_data_irregular, float("inf")),
    ],
    ids=[
        "max_01",
        "max_02",
        "max_03",
        "max_04",
        "max_05",
        "max_06",
        "max_07",
        "max_08",
        "max_09",
    ],
)
def test_max(test_input, expected):
    assert pzutils.max(test_input) == expected


def test_abs():
    assert pzutils.abs(np_data) is not None
    assert pzutils.abs(df_pandas_irregular["depth"]) is not None
    assert pzutils.abs(series) is not None
    assert pzutils.abs(series_polars) is not None
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
    assert pzutils.count_nonzero(np_data_irregular) == 9
    assert pzutils.count_nonzero(df_polars_irregular["depth"]) == 9
    assert pzutils.count_nonzero(series_data_irregular) == 9
    assert pzutils.count_nonzero(series_polars_data_irregular) == 9
    assert pzutils.count_nonzero(list_data_irregular) == 9


def test_nanquantile():
    assert pzutils.nanquantile(np_data, 0.5) == 1000
    assert pzutils.nanquantile(df_pandas_irregular["depth"], 0.5) == 80
    assert pzutils.nanquantile(series, 0.5) == 1000
    assert pzutils.nanquantile(series_polars, 0.5) == 1000
    assert pzutils.nanquantile(np_data_irregular, 0.5) == 80
    assert pzutils.nanquantile(df_polars_irregular["depth"], 0.5) == 80
    assert pzutils.nanquantile(series_data_irregular, 0.5) == 80
    assert pzutils.nanquantile(series_polars_data_irregular, 0.5) == 80
    assert pzutils.nanquantile(list_data_irregular, 0.5) == 80


def test_round():
    assert pzutils.round(np_data).any()
    assert pzutils.round(df_pandas_irregular["depth"]).any()
    assert pzutils.round(series).any()
    assert (pzutils.round(series_polars) != 0).any()
    assert pzutils.round(np_data_irregular).any()
    assert (pzutils.round(df_polars_irregular["depth"]) != 0).any()
    assert pzutils.round(series_data_irregular).any()
    assert (pzutils.round(series_polars_data_irregular) != 0).any()
    assert pzutils.round(list_data_irregular).any()


def test_append():
    assert (pzutils.append(np_data, 1))[-1] == 1
    assert (pzutils.append(df_pandas_irregular["depth"], [2, 3, 4])).iloc[-1] == 4
    assert (pzutils.append(series, (2, 3, 4, 5, 6, 7))).iloc[-1] == 7
    assert (pzutils.append(series_polars, 8))[-1] == 8
    assert (pzutils.append(np_data_irregular, (2, 3, 4, 5, 6, 7)))[-1] == 7
    assert (pzutils.append(df_polars_irregular["depth"], np.array([1, 2, 3, 4])))[
        -1
    ] == 4
    assert (pzutils.append(series_data_irregular, np.array([1, 2, 3, 4]))).iloc[-1] == 4
    assert (pzutils.append(series_polars_data_irregular, (2, 3, 4, 5, 6, 7)))[-1] == 7
    assert (pzutils.append(list_data_irregular, 1000))[-1] == 1000
