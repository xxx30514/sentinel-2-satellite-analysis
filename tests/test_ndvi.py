
import numpy as np
import pytest
import rasterio

from calculate_ndvi import (
    B08_PATH,
    OUTPUT_NODATA,
    OUTPUT_PATH,
    calculate_ndvi_array,
)


def test_ndvi_formula():
    """驗證 NDVI 公式的計算結果。"""

    red = np.array([2, 6], dtype=np.float32)
    nir = np.array([6, 2], dtype=np.float32)

    ndvi, valid_mask = calculate_ndvi_array(red, nir)

    np.testing.assert_allclose(
        ndvi,
        [0.5, -0.5],
        rtol=1e-6,
    )

    assert valid_mask.all()


def test_zero_denominator_returns_nodata():
    """分母為零時，不應產生除以零的結果。"""

    red = np.array([1, 0], dtype=np.float32)
    nir = np.array([-1, 0], dtype=np.float32)

    ndvi, valid_mask = calculate_ndvi_array(red, nir)

    assert not valid_mask[0]
    assert not valid_mask[1]

    np.testing.assert_array_equal(
        ndvi,
        [OUTPUT_NODATA, OUTPUT_NODATA],
    )


def test_invalid_mask_returns_nodata():
    """來源遮罩判定為無效的像素應保留為 NoData。"""

    red = np.array([2, 2], dtype=np.float32)
    nir = np.array([6, 6], dtype=np.float32)

    red_mask = np.array([True, False])
    nir_mask = np.array([True, True])

    ndvi, valid_mask = calculate_ndvi_array(
        red,
        nir,
        red_mask=red_mask,
        nir_mask=nir_mask,
    )

    assert valid_mask[0]
    assert not valid_mask[1]

    assert ndvi[0] == pytest.approx(0.5)
    assert ndvi[1] == OUTPUT_NODATA


def test_non_finite_values_are_invalid():
    """NaN 與無限大不應被當成有效 NDVI。"""

    red = np.array([2, np.nan, 1], dtype=np.float32)
    nir = np.array([6, 6, np.inf], dtype=np.float32)

    ndvi, valid_mask = calculate_ndvi_array(red, nir)

    assert valid_mask[0]
    assert not valid_mask[1]
    assert not valid_mask[2]

    assert ndvi[0] == pytest.approx(0.5)
    assert np.all(ndvi[~valid_mask] == OUTPUT_NODATA)


def test_different_array_shapes_raise_error():
    """兩個波段的陣列形狀不同時，應明確報錯。"""

    red = np.zeros((2, 2), dtype=np.float32)
    nir = np.zeros((3, 3), dtype=np.float32)

    with pytest.raises(ValueError, match="形狀不同"):
        calculate_ndvi_array(red, nir)


def test_generated_ndvi_metadata():
    """驗證已產生的 NDVI GeoTIFF 地理資訊。"""

    if not OUTPUT_PATH.is_file() or not B08_PATH.is_file():
        pytest.skip("請先執行 calculate_ndvi.py 產生 NDVI 檔案")

    with rasterio.open(OUTPUT_PATH) as ndvi_src, \
         rasterio.open(B08_PATH) as b08_src:

        assert ndvi_src.count == 1
        assert ndvi_src.dtypes[0] == "float32"
        assert ndvi_src.nodata == OUTPUT_NODATA

        assert ndvi_src.crs == b08_src.crs
        assert ndvi_src.transform == b08_src.transform

        assert ndvi_src.width == b08_src.width
        assert ndvi_src.height == b08_src.height

        assert ndvi_src.res == b08_src.res
