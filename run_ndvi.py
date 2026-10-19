
from pathlib import Path
import argparse

import numpy as np

from ndvi_utils import calculate_ndvi_from_files


# ==================================================
# 1. 預設設定
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent

DEFAULT_IMAGE_DIR = (
    PROJECT_DIR
    / "data"
    / "real_satellite"
    / "T50RRN_20261011T022619"
)

DEFAULT_RED_PATH = (
    DEFAULT_IMAGE_DIR
    / "T50RRN_20261011T022619_B04_10m.jp2"
)

DEFAULT_NIR_PATH = (
    DEFAULT_IMAGE_DIR
    / "T50RRN_20261011T022619_B08_10m.jp2"
)

DEFAULT_NODATA = -9999.0


# ==================================================
# 2. 命令列參數
# ==================================================

def parse_args():
    """解析紅光、近紅外線影像路徑與 NoData 設定。"""

    parser = argparse.ArgumentParser(
        description="讀取 B04、B08 影像並計算 NDVI，不輸出影像檔案。"
    )

    parser.add_argument(
        "--red",
        type=Path,
        default=DEFAULT_RED_PATH,
        help="紅光 B04 影像路徑。",
    )

    parser.add_argument(
        "--nir",
        type=Path,
        default=DEFAULT_NIR_PATH,
        help="近紅外線 B08 影像路徑。",
    )

    parser.add_argument(
        "--nodata",
        type=float,
        default=DEFAULT_NODATA,
        help="無效 NDVI 像素的標記值，預設為 -9999。",
    )

    args = parser.parse_args()

    # 在開始讀取影像前先檢查檔案
    if not args.red.is_file():
        parser.error(f"找不到紅光影像：{args.red}")

    if not args.nir.is_file():
        parser.error(f"找不到近紅外線影像：{args.nir}")

    return args


# ==================================================
# 3. 執行 NDVI 計算
# ==================================================

def main():
    args = parse_args()

    ndvi, valid_mask = calculate_ndvi_from_files(
        red_path=args.red,
        nir_path=args.nir,
        nodata=args.nodata,
    )

    print("========== NDVI 計算完成 ==========")
    print(f"B04 紅光影像：{args.red}")
    print(f"B08 近紅外線影像：{args.nir}")
    print(f"陣列尺寸：{ndvi.shape}")
    print(f"有效像素數：{np.count_nonzero(valid_mask):,}")
    print(f"無效像素數：{np.count_nonzero(~valid_mask):,}")

    if valid_mask.any():
        values = ndvi[valid_mask]

        print(f"最小 NDVI：{values.min():.4f}")
        print(f"最大 NDVI：{values.max():.4f}")
        print(f"平均 NDVI：{values.mean():.4f}")
    else:
        print("沒有有效像素，無法計算 NDVI 統計值。")


if __name__ == "__main__":
    main()
