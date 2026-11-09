"""Unchanged pooled-statistic functions from the approved revision."""
import numpy as np
SEED, REPS = 20261014, 10000

def measures(matrix, weighted=False):
    n = matrix.sum(axis=(-1, -2))
    row, col = matrix.sum(axis=-1)/n[..., None], matrix.sum(axis=-2)/n[..., None]
    obs = np.trace(matrix, axis1=-2, axis2=-1)/n
    k = matrix.shape[-1]
    pe = (row*col).sum(axis=-1)
    if weighted:
        distance = np.abs(np.arange(k)[:, None]-np.arange(k)[None, :])/(k-1)
        do = (matrix*distance).sum(axis=(-1, -2))/n
        de = (row[..., :, None]*col[..., None, :]*distance).sum(axis=(-1, -2))
        kappa = 1-do/de
    else:
        kappa = (obs-pe)/(1-pe)
    pooled = (row+col)/2
    pac1 = (pooled*(1-pooled)).sum(axis=-1)/(k-1)
    return {'agreement': obs, 'kappa': kappa, 'ac1': (obs-pac1)/(1-pac1)}

def bootstrap(mats, groups=None, weighted=False, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(mats)
    weights = np.zeros((REPS, n), dtype=int)
    strata = [np.arange(n)] if groups is None else [np.flatnonzero(np.array(groups)==g) for g in sorted(set(groups))]
    for idx in strata:
        samples = rng.integers(0, len(idx), size=(REPS, len(idx)))
        for b in range(REPS):
            weights[b, idx] = np.bincount(samples[b], minlength=len(idx))
    flat = weights @ mats.reshape(n, -1)
    distribution = measures(flat.reshape(REPS, *mats.shape[1:]), weighted)
    point = measures(mats.sum(axis=0), weighted)
    return {key: {'estimate': float(point[key]), 'ci95': list(map(float, np.quantile(vals[np.isfinite(vals)], [.025, .975]))),
                  'valid_replicates': int(np.isfinite(vals).sum())} for key, vals in distribution.items()}

def matrices(rows, categories):
    idx = {x: i for i, x in enumerate(categories)}
    m = np.zeros((len(rows), len(categories), len(categories)), dtype=int)
    for i, row in enumerate(rows):
        for a, b in row:
            m[i, idx[a], idx[b]] += 1
    return m
