
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

# def create_test_image() -> None:
#     """建立一張供測試使用的 GeoTIFF 影像。"""

#     # 取得目前 Python 檔案所在的專案目錄
#     project_dir = Path(__file__).resolve().parent

#     # 建立 data 資料夾（如果尚不存在）
#     data_dir = project_dir / "data"
#     data_dir.mkdir(parents=True, exist_ok=True)

#     # 設定輸出影像路徑
#     image_path = data_dir / "sample.tif"

#     # 建立 3 列、4 欄的測試影像
#     image_data = np.array(
#         [
#             [10, 20, 30, 40],
#             [50, -9999, 70, 80],
#             [90, 100, -9999, 120],
#         ],
#         dtype=np.float32,
#     )

#     # 設定 GeoTIFF 的地理空間資訊
#     transform = from_origin(
#         west=121.0,
#         north=25.0,
#         xsize=0.001,
#         ysize=0.001,
#     )

#     # 寫入 GeoTIFF 檔案
#     with rasterio.open(
#         image_path,
#         "w",
#         driver="GTiff",
#         height=image_data.shape[0],
#         width=image_data.shape[1],
#         count=1,
#         dtype=image_data.dtype,
#         crs="EPSG:4326",
#         transform=transform,
#         nodata=-9999,
#     ) as dataset:
#         dataset.write(image_data, 1)

#     print("測試影像建立成功！")
#     print(f"檔案位置：{image_path}")
#     print(f"影像尺寸：{image_data.shape}")
#     print("波段數量：1")
#     print("NoData 值：{-9999}")
#     print("座標系統：EPSG:4326")

def create_test_image() -> None:
    """建立一張具有三個波段的 GeoTIFF 測試影像。"""

    project_dir = Path(__file__).resolve().parent

    data_dir = project_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    image_path = data_dir / "sample_multi_band.tif"

    # 建立第 1 個波段：模擬紅光波段
    band1 = np.array(
        [
            [10, 20, 30, 40],
            [50, -9999, 70, 80],
            [90, 100, -9999, 120],
        ],
        dtype=np.float32,
    )

    # 建立第 2 個波段：模擬綠光波段
    band2 = np.array(
        [
            [15, 25, 35, 45],
            [55, 65, -9999, 85],
            [95, 105, 115, 125],
        ],
        dtype=np.float32,
    )

    # 建立第 3 個波段：模擬近紅外波段
    band3 = np.array(
        [
            [100, 200, 300, 400],
            [500, 600, 700, -9999],
            [900, 1000, 1100, 1200],
        ],
        dtype=np.float32,
    )

    # 將三個波段組合成一個三維陣列
    image_data = np.stack(
        [band1, band2, band3],
        axis=0,
    )

    # 設定地理空間資訊
    transform = from_origin(
        west=121.0,
        north=25.0,
        xsize=0.001,
        ysize=0.001,
    )

    # 建立三波段 GeoTIFF
    with rasterio.open(
        image_path,
        "w",
        driver="GTiff",
        height=image_data.shape[1],
        width=image_data.shape[2],
        count=image_data.shape[0],
        dtype=image_data.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999,
    ) as dataset:
        dataset.write(image_data)

        dataset.set_band_description(1, "Red")
        dataset.set_band_description(2, "Green")
        dataset.set_band_description(3, "Near Infrared")

    print("三波段測試影像建立成功！")
    print(f"檔案位置：{image_path}")
    print(f"影像陣列形狀：{image_data.shape}")
    print("波段數量：3")
    print("每個波段尺寸：3 列 × 4 欄")
    print("NoData 值：-9999")


if __name__ == "__main__":
    create_test_image()
