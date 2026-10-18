
# Sentinel-2 Satellite Image Quality Assessment & NDVI Analysis

以 Python、Rasterio 與 NumPy 建立的 Sentinel-2 衛星影像分析工具，
包含波段品質統計、NDVI 計算、GeoTIFF 輸出及自動化測試。

## Features

- Inspect raster dimensions, CRS, spatial resolution and data types.
- Calculate pixel statistics for Sentinel-2 B02, B03, B04 and B08.
- Process large raster images using window-based reading.
- Export per-band statistics to CSV.
- Calculate NDVI from the red band (B04) and near-infrared band (B08).
- Export NDVI as a georeferenced Float32 GeoTIFF.
- Validate core calculations and output metadata with pytest.

## Technology Stack

- Python
- Rasterio
- NumPy
- pytest
- QGIS

## Data

The project uses four Sentinel-2 bands:

| Band | Description | Resolution |
|---|---|---|
| B02 | Blue | 10 m |
| B03 | Green | 10 m |
| B04 | Red | 10 m |
| B08 | Near Infrared | 10 m |

Source image dimensions: 10980 × 10980 pixels.

Coordinate reference system: EPSG:32650.

Place the four JP2 files in:

`data/real_satellite/T50RRN_20261011T022619/`

The source imagery is not included in this repository.

## Installation

Create and activate a Python virtual environment, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

### 1. Export band quality statistics

```bash
python export_quality_report.py
```

Output:

`reports/pixel_quality_report.csv`

### 2. Calculate NDVI

```bash
python calculate_ndvi.py
```

Output:

`outputs/ndvi/ndvi_T50RRN_20261011.tif`

Open the GeoTIFF in QGIS to visualize the NDVI raster.

### 3. Run tests

```bash
python -m pytest tests/test_ndvi.py -v
```

## NDVI

The Normalized Difference Vegetation Index is calculated as:

NDVI = (B08 - B04) / (B08 + B04)

The output is a single-band Float32 GeoTIFF with a NoData value of -9999.

## Validation

The current test suite covers:

- NDVI formula correctness.
- Zero-denominator handling.
- Invalid pixel masks.
- Non-finite input values.
- Mismatched input array shapes.
- Output raster metadata.

The current test suite contains six passing tests.

## Limitations

- Cloud, cloud-shadow and snow masking has not been implemented.
- Source imagery has no explicit NoData value configured.
- Pixel validity checks do not establish that every pixel represents valid land-surface observations.
- NDVI values should be interpreted with these limitations in mind.

## Future Improvements

- Add Sentinel-2 Scene Classification Layer (SCL) masking.
- Expand automated tests for raster processing and edge cases.
- Improve progress reporting and analysis summaries.
- Add reproducible sample data and result visualizations.


# Sentinel-2 衛星影像品質檢查與 NDVI 植生指數分析

本專案使用 Python 建立 Sentinel-2 衛星影像分析工具，整合多波段影像品質統計、NDVI 植生指數計算、GeoTIFF 輸出與自動化測試，並透過 QGIS 驗證地理空間資料及視覺化分析結果。

## 一、專案功能

- **影像資訊檢查：** 檢查衛星影像尺寸、座標參考系統（CRS）、空間解析度及資料型別。
- **多波段品質統計：** 分析 B02、B03、B04、B08 波段的有效像素數量、零值數量、最小值、最大值與平均值。
- **大型影像分塊處理：** 使用 Rasterio Window 分塊讀取影像，降低大型 Raster 資料處理時的記憶體需求。
- **品質報告匯出：** 將各波段的統計結果輸出為 CSV，方便檢視與後續分析。
- **NDVI 植生指數計算：** 利用紅光波段 B04 與近紅外光波段 B08 計算 NDVI。
- **GeoTIFF 輸出：** 將 NDVI 結果輸出為具有地理參考資訊的單波段 Float32 GeoTIFF。
- **自動化測試：** 使用 pytest 驗證 NDVI 計算、無效資料處理、分母為零的情況及輸出影像的地理資訊。
- **GIS 視覺化：** 使用 QGIS 顯示 NDVI 分析結果，檢查影像空間資訊與視覺化成果。

## 二、使用技術

| 技術 | 用途 |
|---|---|
| Python | 資料處理與分析程式 |
| Rasterio | Raster 影像讀取、分塊處理及 GeoTIFF 輸出 |
| NumPy | 陣列運算與 NDVI 計算 |
| pytest | 自動化測試 |
| QGIS | 地理空間資料檢視與 NDVI 視覺化 |

## 三、使用的衛星影像

本專案使用 Sentinel-2 影像的四個波段：

| 波段 | 波段名稱 | 空間解析度 |
|---|---|---|
| B02 | 藍光（Blue） | 10 公尺 |
| B03 | 綠光（Green） | 10 公尺 |
| B04 | 紅光（Red） | 10 公尺 |
| B08 | 近紅外光（Near Infrared） | 10 公尺 |

原始影像尺寸為 `10980 × 10980` 像素，座標參考系統為 `EPSG:32650`。

請將四個 JP2 波段檔案放入以下目錄：

`data/real_satellite/T50RRN_20261011T022619/`

原始衛星影像因檔案容量較大，不包含於本專案的 Git 儲存庫中。

## 四、安裝環境

建議使用 Python 虛擬環境管理專案依賴。

安裝所需套件：

```bash
python -m pip install -r requirements.txt
```

## 五、執行方式

### 1. 檢查影像資訊

```bash
python check_vrt.py
```

檢查 VRT 虛擬影像的波段數、座標系統、空間解析度、尺寸與資料讀取狀態。

### 2. 匯出波段品質統計報告

```bash
python export_quality_report.py
```

分析 B02、B03、B04、B08 四個波段，並產生：

`reports/pixel_quality_report.csv`

### 3. 計算 NDVI 植生指數

```bash
python calculate_ndvi.py
```

計算結果輸出至：

`outputs/ndvi/ndvi_T50RRN_20261011.tif`

可使用 QGIS 開啟 GeoTIFF，並透過單波段偽彩色（Singleband pseudocolor）顯示 NDVI 分布。

### 4. 執行自動化測試

```bash
python -m pytest tests/test_ndvi.py -v
```

目前已完成六項測試，涵蓋：

1. NDVI 公式計算正確性。
2. 分母為零時的處理。
3. 無效像素遮罩的處理。
4. NaN 與無限大等非有限數值的處理。
5. 輸入波段陣列尺寸不一致時的錯誤處理。
6. 輸出 GeoTIFF 的座標系統、解析度、尺寸、資料型別與 NoData 設定。

目前六項測試均已通過。

## 六、NDVI 計算方法

NDVI（Normalized Difference Vegetation Index，正規化差異植生指數）是一種常見的遙測植生指標，利用紅光與近紅外光的反射率差異，協助觀察地表植被的相對綠度。

計算公式如下：

\[
NDVI = \frac{B08-B04}{B08+B04}
\]

其中：

- B08：近紅外光波段。
- B04：紅光波段。

NDVI 一般介於 -1 至 1。較高的正值常見於較茂盛的植被，但實際解讀仍需考量地表類型、觀測條件及影像品質。

輸出影像使用 `Float32` 資料型別，並以 `-9999` 作為輸出 NoData 標記。當來源遮罩無效、輸入包含非有限數值或計算分母為零時，程式會將相應像素標記為無效。

## 七、目前成果與限制

### 已完成

- 四個 Sentinel-2 波段的像素統計與 CSV 報告。
- 以分塊方式處理大型衛星影像。
- NDVI 計算與 GeoTIFF 輸出。
- 輸出影像的座標系統、解析度與尺寸驗證。
- 六項 pytest 自動化測試。
- 透過 QGIS 成功顯示 NDVI 彩色圖層。

### 目前限制

- 尚未實作雲、雲影及雪的自動遮罩。
- 原始 JP2 影像目前沒有明確設定 NoData 值，因此現有有效像素比例不能直接代表所有像素都是有效的地表觀測。
- 目前的 NDVI 結果尚未排除雲與雲影的影響，不宜直接將整張影像的平均 NDVI 解讀為植被覆蓋率。
- 自動化測試目前以核心計算與既有輸出檔案的驗證為主，後續仍可擴充端到端處理測試。

## 八、未來改進方向

- 整合 Sentinel-2 Scene Classification Layer（SCL），進行雲、雲影與雪的品質遮罩。
- 擴充真實影像的無效資料判定與品質檢查。
- 增加 NDVI 統計報告與視覺化成果匯出。
- 擴充自動化測試及錯誤處理。
- 整理 QGIS 分析截圖與可重現的執行流程。

## 九、專案目的

本專案旨在建立一套可重現的衛星影像分析流程，展示 Python 在遙測資料處理、Raster 品質統計、植生指數計算、地理空間資料輸出及自動化測試上的實務應用。

