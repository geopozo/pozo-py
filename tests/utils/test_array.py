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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, True),
        (df_pandas_irregular["depth"], False),
        (series, True),
        (series_polars, True),
        (np_data_irregular, False),
        (df_polars_irregular["depth"], False),
        (series_data_irregular, False),
        (series_polars_data_irregular, False),
        (list_data_irregular, False),
    ],
    ids=[
        "isfinite_01",
        "isfinite_02",
        "isfinite_03",
        "isfinite_04",
        "isfinite_05",
        "isfinite_06",
        "isfinite_07",
        "isfinite_08",
        "isfinite_09",
    ],
)
def test_isfinite(test_input, expected):
    assert pzutils.isfinite(test_input).all() == expected


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, 49),
        (df_pandas_irregular["depth"], 12),
        (series, 49),
        (series_polars, 49),
        (np_data_irregular, 12),
        (df_polars_irregular["depth"], 12),
        (series_data_irregular, 12),
        (series_polars_data_irregular, 12),
        (list_data_irregular, 12),
    ],
    ids=[
        "count_nonzero_01",
        "count_nonzero_02",
        "count_nonzero_03",
        "count_nonzero_04",
        "count_nonzero_05",
        "count_nonzero_06",
        "count_nonzero_07",
        "count_nonzero_08",
        "count_nonzero_09",
    ],
)
def test_count_nonzero(test_input, expected):
    assert pzutils.count_nonzero(test_input) == expected


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, len(np_data)),
        (df_pandas_irregular["depth"], len(df_pandas_irregular["depth"])),
        (series, len(series)),
        (series_polars, len(series_polars)),
        (np_data_irregular, len(np_data_irregular)),
        (df_polars_irregular["depth"], len(df_pandas_irregular["depth"])),
        (series_data_irregular, len(series_data_irregular)),
        (series_polars_data_irregular, len(series_polars_data_irregular)),
        (list_data_irregular, len(list_data_irregular)),
    ],
    ids=[
        "append_01",
        "append_02",
        "append_03",
        "append_04",
        "append_05",
        "append_06",
        "append_07",
        "append_08",
        "append_09",
    ],
)
def test_append(test_input, expected): #You should use list, tuple, numpy array and also just one value
    assert len(pzutils.append(test_input, (2, 3, 4, 5, 6, 7))) == expected + len((2, 3, 4, 5, 6, 7))
