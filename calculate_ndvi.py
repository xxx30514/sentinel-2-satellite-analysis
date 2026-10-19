from pathlib import Path
import argparse

import numpy as np
import rasterio
from ndvi_utils import calculate_ndvi_array
from rasterio.windows import Window


# ==================================================
# 1. 基本設定
# ==================================================

# 專案根目錄：calculate_ndvi.py 所在的位置
PROJECT_DIR = Path(__file__).resolve().parent

# 預設輸入資料夾
DEFAULT_IMAGE_DIR = (
    PROJECT_DIR
    / "data"
    / "real_satellite"
    / "T50RRN_20261011T022619"
)

# 預設輸出資料夾
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "outputs" / "ndvi"

# 保留原本的預設路徑，方便既有測試或其他模組引用
B04_PATH = (
    DEFAULT_IMAGE_DIR
    / "T50RRN_20261011T022619_B04_10m.jp2"
)

B08_PATH = (
    DEFAULT_IMAGE_DIR
    / "T50RRN_20261011T022619_B08_10m.jp2"
)

OUTPUT_PATH = (
    DEFAULT_OUTPUT_DIR
    / "ndvi_T50RRN_20261011.tif"
)

# 預設分塊大小
WINDOW_SIZE = 512

# 無效 NDVI 像素的標記值
OUTPUT_NODATA = -9999.0


# ==================================================
# 2. 命令列參數
# ==================================================

def parse_args():
    """解析輸入資料夾、輸出路徑與分塊大小。"""

    parser = argparse.ArgumentParser(
        description=(
            "計算 Sentinel-2 NDVI，"
            "並輸出 GeoTIFF 與像素統計資料。"
        )
    )

    parser.add_argument(
        "--image-dir",
        type=Path,
        default=DEFAULT_IMAGE_DIR,
        help="包含 B04 與 B08 影像的資料夾。",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="輸出 GeoTIFF 路徑；省略時自動產生檔名。",
    )

    parser.add_argument(
        "--window-size",
        type=int,
        default=WINDOW_SIZE,
        help="分塊處理的邊長，預設為 512。",
    )
    parser.add_argument(
    "--overwrite",
    action="store_true",
    help="允許覆蓋已存在的輸出檔案",
    )   

    args = parser.parse_args()

    # 驗證輸入資料夾
    if not args.image_dir.is_dir():
        parser.error(
            f"影像資料夾不存在：{args.image_dir}"
        )

    # 驗證分塊大小
    if args.window_size <= 0:
        parser.error(
            "--window-size 必須大於 0。"
        )

    # 自動尋找 B04、B08
    args.b04_path = find_band_file(
        args.image_dir,
        "04",
    )

    args.b08_path = find_band_file(
        args.image_dir,
        "08",
    )

    # 沒有指定輸出路徑時，自動依資料夾名稱產生
    if args.output is None:
        args.output = (
            DEFAULT_OUTPUT_DIR
            / f"ndvi_{args.image_dir.name}.tif"
        )

    return args


# ==================================================
# 3. 自動尋找指定波段
# ==================================================

def find_band_file(
    image_dir: Path,
    band: str,
) -> Path:
    """尋找指定波段的 Sentinel-2 10m JP2 影像。"""

    pattern = f"*_B{band}_10m.jp2"

    matches = sorted(image_dir.glob(pattern))

    if not matches:
        raise FileNotFoundError(
            f"找不到 B{band} 影像。\n"
            f"搜尋位置：{image_dir}\n"
            f"搜尋條件：{pattern}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"找到多個 B{band} 影像，無法自動判斷：\n"
            + "\n".join(str(path) for path in matches)
        )

    return matches[0]


# ==================================================
# 4. 驗證影像是否相容
# ==================================================

def validate_rasters(
    b04: rasterio.io.DatasetReader,
    b08: rasterio.io.DatasetReader,
) -> None:
    """確認 B04 與 B08 可以逐像素進行 NDVI 計算。"""

    if b04.count != 1 or b08.count != 1:
        raise ValueError(
            "預期 B04 與 B08 都是單波段影像。"
        )

    if b04.width != b08.width:
        raise ValueError(
            "B04 與 B08 的影像寬度不同。"
        )

    if b04.height != b08.height:
        raise ValueError(
            "B04 與 B08 的影像高度不同。"
        )

    if b04.crs != b08.crs:
        raise ValueError(
            "B04 與 B08 的座標系統不同。"
        )

    if b04.transform != b08.transform:
        raise ValueError(
            "B04 與 B08 的像素網格或地理參考不同。"
        )


# ==================================================
# 5. 將 NDVI 計算獨立封裝
# ==================================================

#已將計算NDVI方法封裝至ndvi_utils.py


# ==================================================
# 6. 產生分塊視窗
# ==================================================

def iter_windows(
    width: int,
    height: int,
    window_size: int = WINDOW_SIZE,
):
    """依照指定大小逐一產生影像 Window。"""

    if width <= 0 or height <= 0:
        raise ValueError(
            "影像寬度與高度必須大於 0。"
        )

    if window_size <= 0:
        raise ValueError(
            "window_size 必須大於 0。"
        )

    for row in range(
        0,
        height,
        window_size,
    ):
        for col in range(
            0,
            width,
            window_size,
        ):
            yield Window(
                col_off=col,
                row_off=row,
                width=min(
                    window_size,
                    width - col,
                ),
                height=min(
                    window_size,
                    height - row,
                ),
            )


# ==================================================
# 7. 執行 NDVI 計算
# ==================================================

def main(
    b04_path: Path,
    b08_path: Path,
    output_path: Path,
    window_size: int = WINDOW_SIZE,
    overwrite=False,
) -> None:
    """分塊計算 NDVI、輸出 GeoTIFF 並驗證結果。"""

    # 驗證檔案是否存在
    if not b04_path.is_file():
        raise FileNotFoundError(
            f"找不到 B04：{b04_path}"
        )

    if not b08_path.is_file():
        raise FileNotFoundError(
            f"找不到 B08：{b08_path}"
        )

    if window_size <= 0:
        raise ValueError(
            "window_size 必須大於 0。"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    if output_path.exists() and not overwrite:
        raise FileExistsError(
        f"輸出檔案已存在：{output_path}\n"
        "若要覆蓋，請加上 --overwrite。"
    )

    # 統計資訊
    valid_count = 0
    invalid_count = 0

    ndvi_min = None
    ndvi_max = None
    ndvi_sum = 0.0

    print("正在開啟 B04 與 B08...")

    with (
        rasterio.open(b04_path) as b04,
        rasterio.open(b08_path) as b08,
    ):
        # 驗證兩張影像
        validate_rasters(
            b04,
            b08,
        )

        # 先保存來源影像 metadata
        source_width = b08.width
        source_height = b08.height
        source_crs = b08.crs
        source_transform = b08.transform
        source_res = b08.res

        # 以 B08 的地理參考資訊作為輸出基準
        profile = b08.profile.copy()

        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=OUTPUT_NODATA,
            compress="deflate",
            BIGTIFF="IF_SAFER",
        )

        print(f"B04：{b04_path}")
        print(f"B08：{b08_path}")
        print(
            f"影像尺寸："
            f"{source_width} x {source_height}"
        )
        print(f"座標系統：{source_crs}")
        print(f"解析度：{source_res}")
        print(f"分塊大小：{window_size} x {window_size}")
        print(f"輸出位置：{output_path}")
        print("開始分塊計算 NDVI...")

        # 計算總共需要處理多少列區塊
        total_row_blocks = (
            source_height + window_size - 1
        ) // window_size

        with rasterio.open(
            output_path,
            "w",
            **profile,
        ) as dst:

            # 將分析資訊寫入 GeoTIFF metadata
            dst.update_tags(
                description="Sentinel-2 NDVI",
                formula="(B08 - B04) / (B08 + B04)",
                red_band="B04",
                nir_band="B08",
                source_b04=b04_path.name,
                source_b08=b08_path.name,
                cloud_masking="Not applied",
                cloud_shadow_masking="Not applied",
                snow_masking="Not applied",
            )

            # 每次處理一個 window
            for window in iter_windows(
                source_width,
                source_height,
                window_size,
            ):
                row = int(window.row_off)

                # 讀取相同位置的紅光與近紅外線
                red = b04.read(
                    1,
                    window=window,
                )

                nir = b08.read(
                    1,
                    window=window,
                )

                # 取得來源影像的像素遮罩
                red_mask = (
                    b04.read_masks(
                        1,
                        window=window,
                    ) > 0
                )

                nir_mask = (
                    b08.read_masks(
                        1,
                        window=window,
                    ) > 0
                )

                # 計算 NDVI
                ndvi, valid_mask = calculate_ndvi_array(
                    red=red,
                    nir=nir,
                    red_mask=red_mask,
                    nir_mask=nir_mask,
                    nodata=OUTPUT_NODATA,
                )

                # 寫入對應的輸出位置
                dst.write(
                    ndvi,
                    1,
                    window=window,
                )

                # 累計有效與無效像素
                current_count = int(
                    np.count_nonzero(valid_mask)
                )

                invalid_count += (
                    valid_mask.size - current_count
                )

                valid_count += current_count

                # 更新有效 NDVI 的統計數據
                if current_count > 0:
                    values = ndvi[valid_mask]

                    block_min = float(
                        np.min(values)
                    )

                    block_max = float(
                        np.max(values)
                    )

                    ndvi_min = (
                        block_min
                        if ndvi_min is None
                        else min(
                            ndvi_min,
                            block_min,
                        )
                    )

                    ndvi_max = (
                        block_max
                        if ndvi_max is None
                        else max(
                            ndvi_max,
                            block_max,
                        )
                    )

                    ndvi_sum += float(
                        np.sum(
                            values,
                            dtype=np.float64,
                        )
                    )

                # 每完成 10 列區塊或全部完成時回報
                row_block_index = (
                    row // window_size + 1
                )

                is_last_column = (
                    window.col_off + window.width >= source_width
                )

                if is_last_column and (
                    row_block_index % 10 == 0
                    or row_block_index == total_row_blocks
                ):
                    progress = (
                        min(
                            row + int(window.height),
                            source_height,
                        )
                        / source_height
                        * 100
                    )

                    print(
                        f"處理進度：{progress:.1f}%"
                    )

    # ==================================================
    # 8. 顯示 NDVI 統計結果
    # ==================================================

    total_pixels = valid_count + invalid_count

    mean_ndvi = (
        ndvi_sum / valid_count
        if valid_count > 0
        else None
    )

    print("\n========== NDVI 計算完成 ==========")
    print(f"輸出檔案：{output_path}")
    print(f"總像素數：{total_pixels:,}")
    print(f"有效 NDVI 像素：{valid_count:,}")
    print(f"無效像素：{invalid_count:,}")
    print(f"最小 NDVI：{ndvi_min}")
    print(f"最大 NDVI：{ndvi_max}")
    print(f"平均 NDVI：{mean_ndvi}")

    # ==================================================
    # 9. 驗證輸出的 GeoTIFF
    # ==================================================

    if not output_path.is_file():
        raise RuntimeError(
            f"輸出檔案不存在：{output_path}"
        )

    with rasterio.open(output_path) as result:
        print("\n========== 輸出檔案驗證 ==========")
        print(f"檔案存在：{output_path.is_file()}")
        print(f"波段數：{result.count}")
        print(f"資料型別：{result.dtypes[0]}")
        print(f"座標系統：{result.crs}")
        print(f"解析度：{result.res}")
        print(f"NoData：{result.nodata}")

        dimensions_correct = (
            result.width == source_width
            and result.height == source_height
        )

        print(f"尺寸正確：{dimensions_correct}")

        # 檢查主要地理參考資訊
        print(
            "CRS 正確：",
            result.crs == source_crs,
        )

        print(
            "Transform 正確：",
            result.transform == source_transform,
        )

        print(
            "解析度正確：",
            result.res == source_res,
        )

        if (
            not dimensions_correct
            or result.count != 1
            or result.dtypes[0] != "float32"
            or result.crs != source_crs
            or result.transform != source_transform
            or result.nodata != OUTPUT_NODATA
        ):
            raise RuntimeError(
                "輸出 GeoTIFF 驗證失敗，"
                "請檢查上方的 metadata。"
            )


# ==================================================
# 10. 程式進入點
# ==================================================

if __name__ == "__main__":
    args = parse_args()

    main(
        b04_path=args.b04_path,
        b08_path=args.b08_path,
        output_path=args.output,
        window_size=args.window_size,
        overwrite=args.overwrite,
    )