import numpy as np
from ivy.func_wrapper import with_unsupported_dtypes
from typing import Optional
from .. import backend_version


@with_unsupported_dtypes({"1.23.0 and below": ("float16",)}, backend_version)
def l2_normalize(
    x: np.ndarray,
    /,
    *,
    axis: Optional[int] = None,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    if axis is None:
        denorm = np.linalg.norm(x.flatten(), 2, axis)
    else:
        denorm = np.linalg.norm(x, 2, axis, keepdims=True)
    denorm = np.maximum(denorm, 1e-12)
    return x / denorm


def batch_norm(
    x: np.ndarray,
    mean: np.ndarray,
    variance: np.ndarray,
    /,
    *,
    scale: Optional[np.ndarray] = None,
    offset: Optional[np.ndarray] = None,
    training: bool = False,
    eps: float = 1e-5,
    momentum: float = 1e-1,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    runningmean = mean
    runningvariance = variance
    n = x.size / x.shape[1]
    ndims = len(x.shape)
    if training:
        dims = (0, *range(2, ndims))
        mean = np.mean(x, axis=dims)
        variance = np.var(x, axis=dims)
        runningmean = (1 - momentum) * runningmean + momentum * mean
        runningvariance = (1 - momentum) * runningvariance + momentum * variance * n / (n - 1)
    x = np.transpose(x, (0, *range(2, ndims), 1))
    inv = 1.0 / np.sqrt(variance + eps)
    if scale is not None:
        inv *= scale
    ret = x * inv.astype(x.dtype, copy=False) + (
        offset - mean * inv if offset is not None else -mean * inv
    ).astype(x.dtype)
    result = np.transpose(ret, (0, ndims - 1, *range(1, ndims - 1)))
    return result, runningmean, runningvariance


def instance_norm(
    x: np.ndarray,
    mean: np.ndarray,
    variance: np.ndarray,
    /,
    *,
    scale: Optional[np.ndarray] = None,
    offset: Optional[np.ndarray] = None,
    training: bool = False,
    eps: float = 1e-5,
) -> np.ndarray:
    ndims = len(x.shape)
    if training:
        dims = (*range(2, ndims),)
        mean = np.mean(x, axis=dims)
        variance = np.var(x, axis=dims)
    x = np.transpose(x, (*range(2, ndims), 1, 0))
    inv = 1.0 / np.sqrt(variance + eps)
    if scale is not None:
        inv *= scale
    ret = x * inv.astype(x.dtype, copy=False) + (
        offset - mean * inv if offset is not None else -mean * inv
    ).astype(x.dtype)
    return np.transpose(ret, (ndims - 1, ndims - 2, *range(0, ndims - 2)))


def lp_normalize(
    x: np.ndarray,
    /,
    *,
    p: float = 2,
    axis: Optional[int] = None,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    if axis is None:
        denorm = np.linalg.norm(x.flatten(), axis=axis, ord=p)
    else:
        denorm = np.linalg.norm(x, axis=axis, ord=p, keepdims=True)
    denorm = np.maximum(denorm, 1e-12)
    return np.divide(x, denorm, out=out)
