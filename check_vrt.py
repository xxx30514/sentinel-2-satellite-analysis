
import argparse
from pathlib import Path

import rasterio


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_VRT_PATH = (
    PROJECT_DIR
    / "data"
    / "real_satellite"
    / "T50RRN_rgb.vrt"
)


def inspect_vrt(vrt_path: Path) -> dict:
    """檢查三波段 VRT 的基本資訊與可讀取性。"""

    with rasterio.open(vrt_path) as src:
        # 讀取部分像素，確認資料可以實際讀取
        window = rasterio.windows.Window(
            0, 0, min(100, src.width), min(100, src.height)
        )
        sample = src.read(window=window, masked=True)

        checks = {
            "file_exists": vrt_path.is_file(),
            "band_count_is_3": src.count == 3,
            "crs_exists": src.crs is not None,
            "resolution_is_10m": all(
                abs(value - 10) < 0.01
                for value in src.res
            ),
            "dimensions_are_valid": (
                src.width > 0 and src.height > 0
            ),
            "sample_readable": sample.size > 0,
        }

        return {
            "path": str(vrt_path),
            "width": src.width,
            "height": src.height,
            "band_count": src.count,
            "dtypes": src.dtypes,
            "crs": str(src.crs),
            "resolution": src.res,
            "bounds": tuple(src.bounds),
            "checks": checks,
            "passed": all(checks.values()),
        }


def parse_args():
    """解析命令列參數。"""

    parser = argparse.ArgumentParser(
        description="檢查 Sentinel-2 三波段 VRT 的基本資訊與可讀取性。"
    )

    parser.add_argument(
        "--vrt",
        type=Path,
        default=DEFAULT_VRT_PATH,
        help=(
            "指定要檢查的 VRT 檔案路徑。"
            "預設為 data/real_satellite/T50RRN_rgb.vrt"
        ),
    )

    return parser.parse_args()


def main():
    args = parse_args()
    vrt_path = args.vrt

    if not vrt_path.is_file():
        print(f"找不到 VRT：{vrt_path}")
        return 1

    try:
        result = inspect_vrt(vrt_path)

        print("=== Sentinel-2 VRT 檢查報告 ===")
        print(f"檔案：{result['path']}")
        print(
            f"影像尺寸：{result['width']} x {result['height']}"
        )
        print(f"波段數：{result['band_count']}")
        print(f"資料型別：{result['dtypes']}")
        print(f"CRS：{result['crs']}")
        print(f"解析度：{result['resolution']}")
        print(f"範圍：{result['bounds']}")

        print("\n=== 品質檢查項目 ===")
        for name, passed in result["checks"].items():
            status = "PASS" if passed else "FAIL"
            print(f"{status}: {name}")

        print(
            "\n最終結果：",
            "PASS" if result["passed"] else "FAIL",
        )

        return 0 if result["passed"] else 1

    except Exception as exc:
        print(f"VRT 檢查失敗：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
