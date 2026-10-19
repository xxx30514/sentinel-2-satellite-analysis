
from pathlib import Path

import numpy as np
import rasterio

OUTPUT_NODATA = -9999.0


def calculate_ndvi_array(
    red: np.ndarray,
    nir: np.ndarray,
    red_mask: np.ndarray | None = None,
    nir_mask: np.ndarray | None = None,
    nodata: float = OUTPUT_NODATA,
) -> tuple[np.ndarray, np.ndarray]:
    """
    計算 NDVI，並回傳 NDVI 陣列與有效像素遮罩。

    Parameters
    ----------
    red:
        紅光波段 B04。
    nir:
        近紅外線波段 B08。
    red_mask:
        紅光波段的有效像素遮罩，True 表示有效。
    nir_mask:
        近紅外線波段的有效像素遮罩，True 表示有效。
    nodata:
        無效 NDVI 像素的輸出值。

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        NDVI float32 陣列與布林有效像素遮罩。
    """

    # 1. 驗證輸入陣列形狀
    if red.shape != nir.shape:
        raise ValueError(
            "B04 與 B08 的陣列形狀不同。"
        )

    if red_mask is None:
        red_mask = np.ones(
            red.shape,
            dtype=bool,
        )

    if nir_mask is None:
        nir_mask = np.ones(
            nir.shape,
            dtype=bool,
        )

    if red_mask.shape != red.shape:
        raise ValueError(
            "red_mask 的形狀與紅光陣列不同。"
        )

    if nir_mask.shape != nir.shape:
        raise ValueError(
            "nir_mask 的形狀與近紅外線陣列不同。"
        )

    # 2. 轉換為 float32，避免整數除法
    red = red.astype(
        np.float32,
        copy=False,
    )

    nir = nir.astype(
        np.float32,
        copy=False,
    )

    # 3. 計算 NDVI 分母
    denominator = nir + red

    # 4. 判斷可參與計算的有效像素
    valid_mask = (
        red_mask.astype(bool)
        & nir_mask.astype(bool)
        & np.isfinite(red)
        & np.isfinite(nir)
        & np.isfinite(denominator)
        & (denominator != 0)
    )

    # 5. 預設所有像素皆為 NoData
    ndvi = np.full(
        red.shape,
        nodata,
        dtype=np.float32,
    )

    # 6. 只計算有效像素
    with np.errstate(
        divide="ignore",
        invalid="ignore",
        over="ignore",
    ):
        np.divide(
            nir - red,
            denominator,
            out=ndvi,
            where=valid_mask,
        )

    # 7. 排除計算後仍為 NaN 或無限大的結果
    valid_mask &= np.isfinite(ndvi)
    ndvi[~valid_mask] = nodata

    return ndvi, valid_mask

def calculate_ndvi_from_files(
    red_path: str | Path,
    nir_path: str | Path,
    nodata: float = OUTPUT_NODATA,
) -> tuple[np.ndarray, np.ndarray]:
    """
    讀取 B04、B08 影像並計算 NDVI。

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        NDVI 陣列與有效像素遮罩。
    """

    red_path = Path(red_path)
    nir_path = Path(nir_path)

    if not red_path.is_file():
        raise FileNotFoundError(f"找不到紅光影像：{red_path}")

    if not nir_path.is_file():
        raise FileNotFoundError(
            f"找不到近紅外線影像：{nir_path}"
        )

    with (
        rasterio.open(red_path) as red_src,
        rasterio.open(nir_path) as nir_src,
    ):
        # 驗證影像是否相容
        if (
            red_src.count != 1
            or nir_src.count != 1
        ):
            raise ValueError("B04 與 B08 必須都是單波段影像。")

        if (
            red_src.width != nir_src.width
            or red_src.height != nir_src.height
        ):
            raise ValueError("B04 與 B08 的影像尺寸不同。")

        if red_src.crs != nir_src.crs:
            raise ValueError("B04 與 B08 的座標系統不同。")

        if red_src.transform != nir_src.transform:
            raise ValueError("B04 與 B08 的像素網格不同。")

        # 讀取整張影像至記憶體
        red = red_src.read(1)
        nir = nir_src.read(1)

        red_mask = red_src.read_masks(1) > 0
        nir_mask = nir_src.read_masks(1) > 0

    return calculate_ndvi_array(
        red=red,
        nir=nir,
        red_mask=red_mask,
        nir_mask=nir_mask,
        nodata=nodata,
    )
