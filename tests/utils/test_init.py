import pytest
import numpy as np
import pandas as pd
import polars as pl
import pozo.utils as pzutils

list_data = [float("inf"), -float("inf"), None]
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
    assert pzutils.summarize_array(list_data) is None
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
    assert pzutils.hash_array(np_data) == 7568175179752105114
    assert pzutils.hash_array(df_pandas["depth"]) == 6261482111574642737
    assert pzutils.hash_array(series) == 7568175179752105114
    assert pzutils.hash_array(series_polars) == 7568175179752105114
    assert pzutils.hash_array(list_data) == 4361568316307471912 # This has components like [float("inf"), -float("inf"), None]
    assert pzutils.hash_array(np_data_irregular) == 889220209666011938
    assert pzutils.hash_array(df_polars["depth"]) == 6261482111574642737
    assert pzutils.hash_array(series_data_irregular) == 889220209666011938
    assert pzutils.hash_array(series_polars_data_irregular) == 889220209666011938
    assert pzutils.hash_array(list_data_irregular) == 889220209666011938


def test_min_data():
    assert pzutils.min_data(np_data) is None
    assert pzutils.min_data(df_pandas["depth"]) is None
    assert pzutils.min_data(series) is None
    assert pzutils.min_data(series_polars) is None
    assert pzutils.min_data(list_data) is None
    assert pzutils.min_data(np_data_irregular) is None
    assert pzutils.min_data(df_polars["depth"]) is None
    assert pzutils.min_data(series_data_irregular) is None
    assert pzutils.min_data(series_polars_data_irregular) is None
    assert pzutils.min_data(list_data_irregular) is None


def test_max_data():
    assert pzutils.max_data(np_data) is None
    assert pzutils.max_data(df_pandas["depth"]) is None
    assert pzutils.max_data(series) is None
    assert pzutils.max_data(series_polars) is None
    assert pzutils.max_data(list_data) is None
    assert pzutils.max_data(np_data_irregular) is None
    assert pzutils.max_data(df_polars["depth"]) is None
    assert pzutils.max_data(series_data_irregular) is None
    assert pzutils.max_data(series_polars_data_irregular) is None
    assert pzutils.max_data(list_data_irregular) is None


def test_isfinite_data():
    assert pzutils.isfinite_data(np_data[0]) is None
    assert pzutils.isfinite_data(df_pandas["depth"]) is None
    assert pzutils.isfinite_data(series[0]) is None
    assert pzutils.isfinite_data(series_polars[0]) is None
    assert pzutils.isfinite_data(list_data[0]) is None
    assert pzutils.isfinite_data(np_data_irregular[0]) is None
    assert pzutils.isfinite_data(df_polars["depth"]) is None
    assert pzutils.isfinite_data(series_data_irregular[0]) is None
    assert pzutils.isfinite_data(series_polars_data_irregular[0]) is None
    assert pzutils.isfinite_data(list_data_irregular[0]) is None
