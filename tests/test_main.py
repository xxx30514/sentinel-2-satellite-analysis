
from pathlib import Path

from main import inspect_image


# 取得專案中的測試影像路徑
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def test_normal_image(capsys):
    """測試一般影像的波段品質檢查。"""

    image_path = DATA_DIR / "sample_multi_band.tif"

    inspect_image(image_path)
    # 捕捉print的內容 將取得的內容存入output
    output = capsys.readouterr().out
    # assert = 要成立的條件
    # output的文字中要有 "有效像素比例：83.33%"
    # 第 1 波段有效比例為 83.33%，應未通過
    assert "有效像素比例：83.33%" in output
    # count() 會計算指定子字串出現的次數
    # 第 2、3 波段有效比例為 91.67%，應通過
    assert output.count("有效像素比例：91.67%") == 2

    # 整張影像因為第 1 波段未通過，應判定未通過
    assert "整體檢查結果：未通過" in output


def test_invalid_values_image(capsys):
    """測試 NaN、inf、-inf 與 NoData 的排除功能。"""

    image_path = DATA_DIR / "sample_invalid_values.tif"

    inspect_image(image_path)

    output = capsys.readouterr().out

    # 驗證三個波段的有效像素數量
    assert "有效像素數：8" in output
    assert "有效像素數：9" in output

    # 驗證無效像素數量
    assert "無效像素數：4" in output
    assert "無效像素數：3" in output

    # 驗證統計值不會因 NaN 或無限大而失效
    assert "有效像素平均值：62.50" in output
    assert "有效像素平均值：71.67" in output
    assert "有效像素平均值：587.50" in output

    # 整張影像應判定未通過
    assert "整體檢查結果：未通過" in output

def test_missing_image(capsys, tmp_path):
    """測試影像檔案不存在時的處理。"""

    image_path = tmp_path / "missing.tif"

    inspect_image(image_path)

    output = capsys.readouterr().out

    assert "錯誤：找不到影像檔案" in output

def test_all_nodata_band(capsys, tmp_path):
    """測試波段全部都是 NoData 的情況。"""

    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    image_path = tmp_path / "all_nodata.tif"

    # 建立一個 3 x 4、只有 1 個波段的影像
    image_data = np.full(
        (1, 3, 4),
        -9999,
        dtype=np.float32,
    )

    # 寫入測試用 GeoTIFF
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

    # 執行影像檢查
    inspect_image(image_path)

    output = capsys.readouterr().out

    # 12 個像素全部都是無效像素
    assert "像素總數：12" in output
    assert "有效像素數：0" in output
    assert "無效像素數：12" in output
    assert "有效像素比例：0.00%" in output

    # 不應計算平均值、最小值或最大值
    assert "警告：此波段沒有可用的有效像素。" in output
    assert "有效像素平均值：" not in output

    # 整體品質應判定為未通過
    assert "整體檢查結果：未通過" in output    