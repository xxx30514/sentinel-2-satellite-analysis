
import argparse
import csv
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


# ==================================================
# 1. 專案設定
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent

DEFAULT_IMAGE_DIR = (
    PROJECT_DIR
    / "data"
    / "real_satellite"
    / "T50RRN_20261011T022619"
)

DEFAULT_REPORT_DIR = PROJECT_DIR / "reports"

DEFAULT_OUTPUT_CSV = (
    DEFAULT_REPORT_DIR / "pixel_quality_report.csv"
)

BANDS = ("B02", "B03", "B04", "B08")

WINDOW_SIZE = 512


# ==================================================
# 2. 命令列參數
# ==================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="分析 Sentinel-2 波段像素品質並輸出 CSV。"
    )

    parser.add_argument(
        "--image-dir",
        type=Path,
        default=DEFAULT_IMAGE_DIR,
        help="包含 Sentinel-2 波段影像的資料夾",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_CSV,
        help="CSV 報告輸出路徑",
    )

    parser.add_argument(
        "--window-size",
        type=int,
        default=WINDOW_SIZE,
        help="分塊處理的視窗大小，預設 512",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允許覆蓋已存在的 CSV 報告",
    )

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("--window-size 必須大於 0")

    return args


# ==================================================
# 3. 分析單一波段
# ==================================================

def analyze_band(
    band_name: str,
    file_path: Path,
    window_size: int = WINDOW_SIZE,
) -> dict:
    """以分塊方式計算單一波段的像素統計資訊。"""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"找不到 {band_name} 影像：{file_path}"
        )

    valid_count = 0
    zero_count = 0
    value_sum = 0.0

    min_value = None
    max_value = None

    with rasterio.open(file_path) as src:
        width = src.width
        height = src.height
        total_pixels = width * height

        for row in range(0, height, window_size):
            for col in range(0, width, window_size):

                window_width = min(
                    window_size, width - col
                )
                window_height = min(
                    window_size, height - row
                )

                window = Window(
                    col_off=col,
                    row_off=row,
                    width=window_width,
                    height=window_height,
                )

                data = src.read(1, window=window)

                mask = (
                    src.read_masks(1, window=window) > 0
                )

                valid_mask = mask & np.isfinite(data)

                if not np.any(valid_mask):
                    continue

                values = data[valid_mask]

                valid_count += int(values.size)

                zero_count += int(
                    np.count_nonzero(values == 0)
                )

                value_sum += float(
                    np.sum(values, dtype=np.float64)
                )

                current_min = int(np.min(values))
                current_max = int(np.max(values))

                if min_value is None:
                    min_value = current_min
                    max_value = current_max
                else:
                    min_value = min(
                        min_value, current_min
                    )
                    max_value = max(
                        max_value, current_max
                    )

        valid_ratio = (
            valid_count / total_pixels * 100
            if total_pixels > 0
            else 0.0
        )

        zero_ratio = (
            zero_count / valid_count * 100
            if valid_count > 0
            else 0.0
        )

        mean_value = (
            value_sum / valid_count
            if valid_count > 0
            else None
        )

        return {
            "band": band_name,
            "file_name": file_path.name,
            "width": width,
            "height": height,
            "crs": str(src.crs) if src.crs else "",
            "resolution_x": src.res[0],
            "resolution_y": src.res[1],
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "total_pixels": total_pixels,
            "valid_pixels": valid_count,
            "valid_ratio_percent": round(
                valid_ratio, 6
            ),
            "zero_count": zero_count,
            "zero_ratio_percent": round(
                zero_ratio, 8
            ),
            "min": min_value,
            "max": max_value,
            "mean": (
                round(mean_value, 4)
                if mean_value is not None
                else None
            ),
        }


# ==================================================
# 4. 執行分析並輸出 CSV
# ==================================================

def main(
    image_dir: Path,
    output_csv: Path,
    window_size: int = WINDOW_SIZE,
    overwrite: bool = False,
):
    image_dir = Path(image_dir)
    output_csv = Path(output_csv)

    # 先檢查輸出檔案，避免不必要的影像分析
    if output_csv.exists() and not overwrite:
        raise FileExistsError(
            f"輸出檔案已存在：{output_csv}\n"
            "若要覆蓋，請加上 --overwrite。"
        )

    # 確認影像資料夾存在
    if not image_dir.is_dir():
        raise NotADirectoryError(
            f"找不到影像資料夾：{image_dir}"
        )

    results = []

    for band_name in BANDS:
        # 由波段名稱自動尋找對應檔案
        pattern = f"*_B{band_name[1:]}_10m.jp2"
        matches = list(image_dir.glob(pattern))

        if not matches:
            raise FileNotFoundError(
                f"找不到 {band_name} 波段："
                f"{image_dir / pattern}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"找到多個 {band_name} 波段檔案，"
                f"請確認資料夾內容：{matches}"
            )

        file_path = matches[0]

        print("=" * 60)
        print(f"正在分析波段：{band_name}")
        print(f"檔案：{file_path.name}")

        result = analyze_band(
            band_name,
            file_path,
            window_size,
        )

        results.append(result)

        print(
            f"有效像素比例："
            f"{result['valid_ratio_percent']}%"
        )
        print(f"零值數量：{result['zero_count']}")
        print(f"最小值：{result['min']}")
        print(f"最大值：{result['max']}")
        print(f"平均值：{result['mean']}")

    # 確保輸出資料夾存在
    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 使用 UTF-8 BOM，讓 Excel 正確讀取中文
    with output_csv.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=list(results[0].keys()),
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 60)
    print("所有波段分析完成！")
    print(f"共分析 {len(results)} 個波段")
    print(f"CSV 報告：{output_csv}")


if __name__ == "__main__":
    args = parse_args()

    main(
        image_dir=args.image_dir,
        output_csv=args.output,
        window_size=args.window_size,
        overwrite=args.overwrite,
    )
