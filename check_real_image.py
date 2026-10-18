
from pathlib import Path
import argparse
import re

import rasterio
from rasterio.errors import RasterioError

PROJECT_DIR = Path(__file__).parent
TARGET_BANDS = {"B02", "B03", "B04", "B08"}


def get_band_name(filename: str) -> str | None:
    match = re.search(
        r"_(B02|B03|B04|B08)_",
        filename.upper()
    )
    return match.group(1) if match else None


def inspect_image(image_path: Path) -> dict:
    result = {
        "file": str(image_path),
        "band": get_band_name(image_path.name),
        "passed": False,
        "error": None,
        "width": None,
        "height": None,
        "count": None,
        "dtypes": None,
        "crs": None,
        "nodata": None,
        "resolution": None,
        "bounds": None,
    }

    try:
        with rasterio.open(image_path) as dataset:
            result.update({
                "width": dataset.width,
                "height": dataset.height,
                "count": dataset.count,
                "dtypes": dataset.dtypes,
                "crs": str(dataset.crs) if dataset.crs else None,
                "nodata": dataset.nodata,
                "resolution": dataset.res,
                "bounds": tuple(dataset.bounds),
            })

            result["passed"] = (
                dataset.width > 0
                and dataset.height > 0
                and dataset.crs is not None
            )

            if not result["passed"]:
                result["error"] = "尺寸不正確或缺少座標系統"

    except (RasterioError, OSError) as exc:
        result["error"] = str(exc)

    return result


def print_report(result: dict) -> None:
    print("\n" + "=" * 50)
    print("檔案：", result["file"])
    print("波段：", result["band"])
    print("基本檢查：", "通過" if result["passed"] else "未通過")

    if result["error"]:
        print("錯誤：", result["error"])
        return

    print("尺寸：", result["width"], "x", result["height"])
    print("波段數量：", result["count"])
    print("資料型別：", result["dtypes"])
    print("座標系統：", result["crs"])
    print("NoData：", result["nodata"])
    print("像素大小：", result["resolution"])
    print("影像範圍：", result["bounds"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="檢查指定資料夾中的 Sentinel-2 波段"
    )
    parser.add_argument(
        "input_dir",
        help="指定單一產品或 Tile 的資料夾路徑"
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)

    # 相對路徑以專案根目錄為基準
    if not input_dir.is_absolute():
        input_dir = PROJECT_DIR / input_dir

    if not input_dir.is_dir():
        parser.error(f"資料夾不存在：{input_dir}")

    image_paths = sorted(
        path
        for path in input_dir.rglob("*.jp2")
        if get_band_name(path.name) in TARGET_BANDS
    )

    if not image_paths:
        print("指定資料夾內找不到目標波段。")
        return

    print(f"檢查資料夾：{input_dir}")
    print(f"找到 {len(image_paths)} 個目標波段檔案。")

    for image_path in image_paths:
        print_report(inspect_image(image_path))


if __name__ == "__main__":
    main()
