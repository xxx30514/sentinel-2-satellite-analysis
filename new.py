from pathlib import Path
import argparse

import numpy as np
import rasterio


MIN_VALID_RATIO = 90.0


def inspect_image(image_path: Path) -> dict:
    """分析 GeoTIFF 影像，回傳結構化的檢查結果。分析與輸出分離"""

    image_path = Path(image_path)

    # 1. 檢查檔案是否存在
    if not image_path.is_file():
        return {
            "image_path": str(image_path),
            "error": f"找不到影像檔案：{image_path}",
            "passed": False,
            "bands": [],
        }

    try:
        # 2. 開啟影像並讀取中繼資料
        with rasterio.open(image_path) as dataset:

            result = {
                "image_path": str(image_path),
                "error": None,
                "width": dataset.width,
                "height": dataset.height,
                "band_count": dataset.count,
                "crs": str(dataset.crs) if dataset.crs else None,
                "nodata": dataset.nodata,
                "passed": dataset.count > 0,
                "bands": [],
            }

            # 3. 逐一檢查每個波段
            for band_index in range(1, dataset.count + 1):
                band = dataset.read(band_index, masked=True)

                # 排除 NoData
                unmasked_pixels = band.compressed()

                # 排除 NaN、正無限大、負無限大
                valid_pixels = unmasked_pixels[
                    np.isfinite(unmasked_pixels)
                ]

                total_count = band.size
                valid_count = valid_pixels.size
                invalid_count = total_count - valid_count

                # 4. 計算有效像素比例
                if total_count > 0:
                    valid_ratio = (
                        valid_count / total_count * 100
                    )
                else:
                    valid_ratio = 0.0

                # 5. 判斷這個波段是否通過
                band_passed = (
                    total_count > 0
                    and valid_ratio >= MIN_VALID_RATIO
                )

                # 6. 計算統計值
                if valid_count > 0:
                    mean_value = float(np.mean(valid_pixels))
                    min_value = float(np.min(valid_pixels))
                    max_value = float(np.max(valid_pixels))
                else:
                    mean_value = None
                    min_value = None
                    max_value = None

                # 7. 將波段結果存入字典
                band_result = {
                    "band": band_index,
                    "total_pixels": int(total_count),
                    "valid_pixels": int(valid_count),
                    "invalid_pixels": int(invalid_count),
                    "valid_ratio": float(valid_ratio),
                    "passed": bool(band_passed),
                    "mean": mean_value,
                    "min": min_value,
                    "max": max_value,
                }

                result["bands"].append(band_result)

                # 8. 只要有一個波段未通過，整張影像就不通過
                if not band_passed:
                    result["passed"] = False

            return result

    except rasterio.errors.RasterioError as exc:
        return {
            "image_path": str(image_path),
            "error": f"無法讀取影像：{exc}",
            "passed": False,
            "bands": [],
        }


def print_report(result: dict) -> None:
    """將影像分析結果輸出為中文報告。"""

    # 1. 如果有錯誤，顯示錯誤並結束
    if result["error"] is not None:
        print(f"錯誤：{result['error']}")
        return

    # 2. 顯示影像基本資訊
    print(f"影像路徑：{result['image_path']}")
    print(f"影像寬度：{result['width']}")
    print(f"影像高度：{result['height']}")
    print(f"波段數量：{result['band_count']}")
    print(f"座標系統：{result['crs']}")
    print(f"NoData 值：{result['nodata']}")

    # 3. 顯示每個波段的檢查結果
    for band in result["bands"]:
        print(f"\n--- Band {band['band']} ---")
        print(f"像素總數：{band['total_pixels']}")
        print(f"有效像素數：{band['valid_pixels']}")
        print(f"無效像素數：{band['invalid_pixels']}")
        print(f"有效像素比例：{band['valid_ratio']:.2f}%")

        if band["valid_pixels"] > 0:
            print(f"有效像素平均值：{band['mean']:.2f}")
            print(f"有效像素最小值：{band['min']:.2f}")
            print(f"有效像素最大值：{band['max']:.2f}")
        else:
            print("警告：此波段沒有可用的有效像素。")

        if band["passed"]:
            print("波段檢查結果：通過")
        else:
            print("波段檢查結果：未通過")

    # 4. 顯示整體檢查結果
    if result["passed"]:
        print("\n整體檢查結果：通過")
    else:
        print("\n整體檢查結果：未通過")


def main() -> None:
    """處理命令列參數並執行影像檢查。"""

    parser = argparse.ArgumentParser(
        description="衛星影像品質檢查工具"
    )

    parser.add_argument(
        #位置參數 不可省略
        "image_path",
        type=Path,
        help="要檢查的 GeoTIFF 影像路徑",
    )

    args = parser.parse_args()

    result = inspect_image(args.image_path)
    print_report(result)


if __name__ == "__main__":
    main()