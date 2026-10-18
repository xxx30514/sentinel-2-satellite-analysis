
from pathlib import Path
import argparse
import rasterio
import numpy as np
# 影像品質檢查門檻（百分比）
MIN_VALID_RATIO = 90.0

def inspect_image(image_path: Path) -> None:
    """讀取 GeoTIFF 基本資訊，並檢查各個波段的資料品質。分析與輸出混在一起"""

    if not image_path.is_file():
        print(f"錯誤：找不到影像檔案：{image_path}")
        return

    try:
        with rasterio.open(image_path) as dataset:
            print("\n===== 衛星影像基本資訊 =====")
            print(f"檔案名稱：{image_path.name}")
            print(f"影像格式：{dataset.driver}")
            print(f"影像寬度：{dataset.width} pixels")
            print(f"影像高度：{dataset.height} pixels")
            print(f"波段數量：{dataset.count}")
            print(f"座標系統：{dataset.crs}")
            print(f"NoData值：{dataset.nodata}")
            print(f"像素解析度：{dataset.res}")
            print(f"資料型別：{dataset.dtypes}")
            print(f"影像範圍：{dataset.bounds}")
            
            # 讀取第一個波段，並套用影像本身的遮罩資訊   
            # 1.dataset.read(1)：讀取第 1 個波段的像素資料。
            # 2.masked=True：依據 Rasterio 辨識到的遮罩與 NoData 資訊，將無效像素標記起來。
            # 3.band：是一個 NumPy masked array，可同時保留像素值與遮罩資訊。
            # band = dataset.read(1, masked=True)
            # band1 = dataset.read(1)

            # 預設所有波段都通過
            all_bands_passed = True
            # 逐一檢查每個波段
            # #1開始 count+1前結束 range(1,5)-> 1開始 5之前停止 所以會檢查1-4
            # Rasterio 的波段編號從1開始 故使用 range(start, stop, step) 1開始
            for band_index in range(1, dataset.count + 1): 
                # 讀取目前波段，並套用遮罩資訊
                band = dataset.read(band_index, masked=True)
                # 取出未被遮罩的像素
                unmasked_pixels = band.compressed()
                # 排除 NaN、正無限大與負無限大
                valid_pixels = unmasked_pixels[np.isfinite(unmasked_pixels)]
                # 計算像素數量
                total_count = band.size
                valid_count = valid_pixels.size
                invalid_count = total_count - valid_count

                print(f"\n===== 第 {band_index} 波段資料品質檢查 =====")
                print(f"像素總數：{total_count}")
                print(f"有效像素數：{valid_count}")
                print(f"無效像素數：{invalid_count}")
                if total_count > 0:
                    valid_ratio = valid_count / total_count * 100
                    print(f"有效像素比例：{valid_ratio:.2f}%")
                    # 判斷目前波段是否符合品質門檻
                    if valid_ratio >= MIN_VALID_RATIO:
                        print("品質檢查結果：通過")
                    else:
                        # 只要有一個波段未通過，整張影像就不合格
                        all_bands_passed = False
                        print( f"品質檢查結果：未通過，"f"有效像素比例低於 {MIN_VALID_RATIO:.2f}%")
                else:
                    all_bands_passed = False
                    print("品質檢查結果：未通過，影像沒有像素資料")        
                if valid_count > 0:
                    print(f"有效像素平均值：{np.mean(valid_pixels):.2f}")
                    print(f"有效像素最小值：{np.min(valid_pixels)}")
                    print(f"有效像素最大值：{np.max(valid_pixels)}")
                else:
                    print("警告：此波段沒有可用的有效像素。")

            print("============================")
            # 所有波段檢查完成
            print("\n===== 所有波段檢查完成 =====")

            # 判斷整張影像的品質
            print("\n===== 整張影像品質判定 =====")

            if all_bands_passed:
                print("整體檢查結果：通過")
            else:
                print("整體檢查結果：未通過，至少有一個波段不符合品質門檻")
            print()

            # 顯示 NumPy 陣列的基本資訊
            # print("\n===== 第一波段像素統計 =====")
            # print(f"陣列型別：{type(band1)}")
            # print(f"陣列形狀：{band1.shape}")
            # print(f"陣列維度：{band1.ndim}")
            # print(f"像素資料型別：{band1.dtype}")
            # print(f"像素總數：{band1.size}")

            # 計算像素統計資訊
            # print(f"像素平均值：{np.mean(band1)}")
            # print(f"像素最小值：{np.min(band1)}")
            # print(f"像素最大值：{np.max(band1)}")
            # print("============================\n")

    except rasterio.errors.RasterioError as exc:
        print(f"讀取影像失敗：{exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Satellite Image Checker"
    )
    parser.add_argument(
        ##位置參數 不可省略
        "image",
        type=Path,
        help="要檢查的 GeoTIFF 影像路徑",
    )

    args = parser.parse_args()
    inspect_image(args.image)


if __name__ == "__main__":
    main()
