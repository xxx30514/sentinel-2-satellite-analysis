
import argparse
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


def check_pixel_quality(image_path: Path) -> None:
    print(f"\n{'=' * 60}")
    print(f"影像：{image_path.name}")
    print("=" * 60)

    with rasterio.open(image_path) as src:
        print(f"尺寸：{src.width} x {src.height}")
        print(f"波段數：{src.count}")
        print(f"CRS：{src.crs}")
        print(f"解析度：{src.res}")
        print(f"NoData：{src.nodata}")

        total_pixels = src.width * src.height

        for band_index in range(1, src.count + 1):
            valid_count = 0
            zero_count = 0
            min_value = None
            max_value = None
            value_sum = 0.0

            # 分區塊讀取，降低記憶體使用量
            block_size = 512

            for row in range(0, src.height, block_size):
                for col in range(0, src.width, block_size):
                    height = min(block_size, src.height - row)
                    width = min(block_size, src.width - col)

                    window = Window(col, row, width, height)

                    data = src.read(
                        band_index,
                        window=window,
                        masked=True
                    )

                    values = np.asarray(data.data)
                    mask = np.ma.getmaskarray(data)

                    valid = (~mask) & np.isfinite(values)
                    valid_values = values[valid]

                    if valid_values.size == 0:
                        continue

                    valid_count += valid_values.size
                    zero_count += np.count_nonzero(
                        valid_values == 0
                    )

                    block_min = valid_values.min().item()
                    block_max = valid_values.max().item()

                    if min_value is None or block_min < min_value:
                        min_value = block_min

                    if max_value is None or block_max > max_value:
                        max_value = block_max

                    value_sum += np.sum(
                        valid_values,
                        dtype=np.float64
                    )

            valid_ratio = valid_count / total_pixels * 100
            zero_ratio = (
                zero_count / valid_count * 100
                if valid_count else 0
            )

            mean_value = (
                value_sum / valid_count
                if valid_count else None
            )

            print(f"\n--- Band {band_index} ---")
            print(f"有效像素數：{valid_count:,}")
            print(f"有效比例：{valid_ratio:.4f}%")
            print(f"零值像素數：{zero_count:,}")
            print(f"零值像素比例：{zero_ratio:.8f}%")
            print(f"最小值：{min_value}")
            print(f"最大值：{max_value}")

            if mean_value is not None:
                print(f"平均值：{mean_value:.4f}")
            else:
                print("平均值：無有效像素")

            print("檢查完成")


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel-2 像素品質檢查"
    )

    parser.add_argument(
        "image",
        type=Path,
        help="輸入 VRT 或 JP2 影像路徑"
    )

    args = parser.parse_args()

    if not args.image.is_file():
        parser.error(f"找不到影像檔案：{args.image}")

    check_pixel_quality(args.image)


if __name__ == "__main__":
    main()
