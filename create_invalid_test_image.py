
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def create_invalid_test_image() -> None:
    """建立包含 NoData、NaN、inf、-inf 的測試影像。"""

    # 建立測試資料夾
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "sample_invalid_values.tif"

    # 第 1 波段：1 個 NoData、1 個 NaN、1 個 inf、1 個 -inf
    band1 = np.array(
        [
            [10, 20, np.nan, 40],
            [50, -9999, 70, np.inf],
            [90, 100, -np.inf, 120],
        ],
        dtype=np.float32,
    )

    # 第 2 波段：1 個 NaN、1 個 inf、1 個 -inf
    band2 = np.array(
        [
            [15, np.nan, 35, 45],
            [55, 65, np.inf, 85],
            [-np.inf, 105, 115, 125],
        ],
        dtype=np.float32,
    )

    # 第 3 波段：1 個 NoData、1 個 NaN、1 個 inf、1 個 -inf
    band3 = np.array(
        [
            [100, 200, 300, np.inf],
            [np.nan, 600, 700, 800],
            [900, -np.inf, 1100, -9999],
        ],
        dtype=np.float32,
    )

    # 組合成三維陣列，形狀為 (波段數, 高度, 寬度)
    image_data = np.stack([band1, band2, band3], axis=0)

    # 設定 GeoTIFF 基本資訊
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=image_data.shape[1],
        width=image_data.shape[2],
        count=image_data.shape[0],
        dtype=image_data.dtype,
        crs="EPSG:4326",
        transform=from_origin(121.0, 25.0, 0.001, 0.001),
        nodata=-9999,
    ) as dataset:
        dataset.write(image_data)

        dataset.set_band_description(1, "Red")
        dataset.set_band_description(2, "Green")
        dataset.set_band_description(3, "Near Infrared")

    print(f"測試影像建立成功：{output_path}")


if __name__ == "__main__":
    create_invalid_test_image()
