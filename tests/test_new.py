
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from new import inspect_image, print_report


DATA_DIR = Path(__file__).parent / "data"


def test_normal_image():
    """測試一般影像的波段品質檢查。"""

    image_path = DATA_DIR / "sample_multi_band.tif"

    result = inspect_image(image_path)

    # 檢查影像基本資訊
    assert result["error"] is None
    assert result["band_count"] == 3
    assert len(result["bands"]) == 3

    # 檢查第一個波段
    band1 = result["bands"][0]

    assert band1["band"] == 1
    assert band1["total_pixels"] == 12
    assert band1["valid_pixels"] == 10
    assert band1["invalid_pixels"] == 2
    assert band1["valid_ratio"] == pytest.approx(83.333333)
    assert band1["mean"] == pytest.approx(61.0)
    assert band1["min"] == pytest.approx(10.0)
    assert band1["max"] == pytest.approx(120.0)
    assert band1["passed"] is False

    # 檢查第二個波段
    band2 = result["bands"][1]

    assert band2["valid_pixels"] == 11
    assert band2["invalid_pixels"] == 1
    assert band2["valid_ratio"] == pytest.approx(91.666667)
    assert band2["passed"] is True

    # 檢查第三個波段
    band3 = result["bands"][2]

    assert band3["valid_pixels"] == 11
    assert band3["invalid_pixels"] == 1
    assert band3["valid_ratio"] == pytest.approx(91.666667)
    assert band3["passed"] is True

    # 第一個波段未通過，因此整張影像未通過
    assert result["passed"] is False


def test_invalid_values_image():
    """測試 NoData、NaN、inf 與 -inf 的排除功能。"""

    image_path = DATA_DIR / "sample_invalid_values.tif"

    result = inspect_image(image_path)

    assert result["error"] is None
    assert len(result["bands"]) == 3

    # 第一個波段
    band1 = result["bands"][0]

    assert band1["valid_pixels"] == 8
    assert band1["invalid_pixels"] == 4
    assert band1["valid_ratio"] == pytest.approx(66.666667)
    assert band1["mean"] == pytest.approx(62.5)
    assert band1["min"] == pytest.approx(10.0)
    assert band1["max"] == pytest.approx(120.0)

    # 第二個波段
    band2 = result["bands"][1]

    assert band2["valid_pixels"] == 9
    assert band2["invalid_pixels"] == 3
    assert band2["valid_ratio"] == pytest.approx(75.0)
    assert band2["mean"] == pytest.approx(71.666667)

    # 第三個波段
    band3 = result["bands"][2]

    assert band3["valid_pixels"] == 8
    assert band3["invalid_pixels"] == 4
    assert band3["valid_ratio"] == pytest.approx(66.666667)
    assert band3["mean"] == pytest.approx(587.5)

    assert result["passed"] is False


def test_missing_image(tmp_path):
    """測試影像檔案不存在時的處理。"""

    image_path = tmp_path / "missing.tif"

    result = inspect_image(image_path)

    assert result["error"] is not None
    assert "找不到影像檔案" in result["error"]
    assert result["passed"] is False
    assert result["bands"] == []


def test_all_nodata_band(tmp_path):
    """測試波段全部都是 NoData 的情況。"""

    image_path = tmp_path / "all_nodata.tif"

    image_data = np.full(
        (1, 3, 4),
        -9999,
        dtype=np.float32,
    )

    with rasterio.open(
        image_path,
        "w",
        driver="GTiff",
        height=3,
        width=4,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(121.0, 25.0, 0.001, 0.001),
        nodata=-9999,
    ) as dataset:
        dataset.write(image_data)

    result = inspect_image(image_path)

    band = result["bands"][0]

    assert result["error"] is None
    assert result["band_count"] == 1
    assert band["total_pixels"] == 12
    assert band["valid_pixels"] == 0
    assert band["invalid_pixels"] == 12
    assert band["valid_ratio"] == pytest.approx(0.0)

    # 沒有有效像素，因此統計值應該是 None
    assert band["mean"] is None
    assert band["min"] is None
    assert band["max"] is None

    assert band["passed"] is False
    assert result["passed"] is False


def test_print_report(capsys):
    """測試報告輸出函式是否正確顯示文字。"""

    image_path = DATA_DIR / "sample_multi_band.tif"

    result = inspect_image(image_path)

    print_report(result)

    output = capsys.readouterr().out

    assert "影像路徑：" in output
    assert "波段數量：3" in output
    assert "有效像素比例：83.33%" in output
    assert "整體檢查結果：未通過" in output
