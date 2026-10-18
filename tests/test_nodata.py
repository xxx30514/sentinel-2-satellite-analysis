import numpy as np

# 模擬一張 3 列、4 欄的衛星影像
# 假設 -9999 是這份測試資料的 NoData 值
band1 = np.array([
    [10, 20, 30, 40],
    [50, -9999, 70, 80],
    [90, 100, -9999, 120]
])

nodata_value = -9999

# 判斷每個像素是否為有效資料
valid_mask = band1 != nodata_value

# 計算有效與無效像素數量
valid_count = np.count_nonzero(valid_mask)
invalid_count = band1.size - valid_count

# 計算有效像素比例
valid_ratio = valid_count / band1.size * 100

print("===== 模擬影像檢查 =====")
print(f"影像形狀：{band1.shape}")
print(f"像素總數：{band1.size}")
print(f"有效像素數：{valid_count}")
print(f"無效像素數：{invalid_count}")
print(f"有效像素比例：{valid_ratio:.2f}%")

# 只保留有效像素，再計算統計值
valid_pixels = band1[valid_mask]

print(f"有效像素平均值：{np.mean(valid_pixels):.2f}")
print(f"有效像素最小值：{np.min(valid_pixels)}")
print(f"有效像素最大值：{np.max(valid_pixels)}")
