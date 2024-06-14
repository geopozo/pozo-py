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


@pytest.mark.parametrize(
    "test_input",
    [
        (np_data),
        (series),
        (series_polars),
    ],
    ids=[
        "summarize_array_01",
        "summarize_array_02",
        "summarize_array_03",
    ],
)
def test_summarize_array(test_input):
    assert pzutils.summarize_array(test_input)

    with pytest.raises(Exception):
        assert pzutils.summarize_array(list_data_irregular)
        assert pzutils.summarize_array(df_polars_irregular["depth"])
        assert pzutils.summarize_array(np_data_irregular)
        assert pzutils.summarize_array(df_pandas_irregular["depth"])
        assert pzutils.summarize_array(series_data_irregular)
        assert pzutils.summarize_array(series_polars_data_irregular)


@pytest.mark.parametrize(
    "test_input_1,test_input_2,expected",
    [
        (np_data[0], np_data[-1], False),
        (series.iloc[0], series.iloc[-1], False),
        (series_polars[0], series_polars[-1], False),
    ],
    ids=[
        "is_close_01",
        "is_close_02",
        "is_close_03",
    ],
)
def test_is_close(test_input_1, test_input_2, expected):
    assert pzutils.is_close(test_input_1, test_input_2) == expected


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


@pytest.mark.parametrize(
    "test_input",
    [
        (np_data),
        (df_pandas_irregular["depth"]),
        (series),
        (np_data_irregular),
        (series_data_irregular),
        (list_data_irregular),
    ],
    ids=[
        "abs_01",
        "abs_02",
        "abs_03",
        "abs_04",
        "abs_05",
        "abs_06",
    ],
)
def test_abs(test_input):
    assert pzutils.abs(test_input).all() >= 0
    assert (pzutils.abs(series_polars) >= 0).all()
    assert (pzutils.abs(df_polars_irregular["depth"]) >= 0).all()
    assert (pzutils.abs(series_polars_data_irregular) >= 0).all()


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


@pytest.mark.parametrize(
    "test_input",
    [
        (np_data),
        (df_pandas_irregular["depth"]),
        (series),
        (series_polars),
        (np_data_irregular),
        (df_polars_irregular["depth"]),
        (series_data_irregular),
        (series_polars_data_irregular),
        (list_data_irregular),
    ],
    ids=[
        "isnan_01",
        "isnan_02",
        "isnan_03",
        "isnan_04",
        "isnan_05",
        "isnan_06",
        "isnan_07",
        "isnan_08",
        "isnan_09",
    ],
)
def test_isnan(test_input):
    assert pzutils.isnan(test_input) is not None


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np_data, 1000),
        (df_pandas_irregular["depth"], 80),
        (series, 1000),
        (series_polars, 1000),
        (np_data_irregular, 80),
        (df_polars_irregular["depth"], 90), #ERROR, NAN ALTERA EL VALOR EN POLARS
        (series_data_irregular, 80),
        (series_polars_data_irregular, 90), #ERROR, NAN ALTERA EL VALOR EN POLARS
        (list_data_irregular, 80),
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
def test_nanquantile(test_input, expected):
    assert pzutils.nanquantile(test_input, 0.5) == expected


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
