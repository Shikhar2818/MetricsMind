"""Explain a flag: which signal actually made this minute look unusual.

Isolation Forest returns a score but no reason.  For every flagged minute we re-score the row
once per feature, each time replacing that single feature with the server's normal value.
If the score drops a lot, that feature is what pushed the row over the threshold.  The result
is attached to the row as a short, human-readable "drivers" string.

    python explain.py        # show real explanations from the test period
"""

import numpy as np
import pandas as pd

SUFFIX = {
    "mean5": "5-min average", "mean15": "15-min average", "mean60": "1-hour average",
    "std5": "5-min variability", "std15": "15-min variability", "std60": "1-hour variability",
    "diff": "1-min change", "diff60": "1-hour change",
    "dev": "deviation from its 1-hour baseline",
    "dev360": "deviation from its 6-hour baseline",
    "dev1440": "deviation from its 24-hour baseline",
    "hour_sin": "time of day", "hour_cos": "time of day",
}


def label(name):
    """('cpu_dev1440') -> ('cpu', 'deviation from its 24-hour baseline')."""
    if name.startswith("hour_"):
        return "time of day", SUFFIX[name]
    metric, _, suffix = name.partition("_")
    return metric.replace("_", " "), SUFFIX.get(suffix, suffix)


def attribute(model, values, normal, cols, chunk=256):
    """values: (n, d) rows to explain, normal: (d,) typical values.

    Returns (n, d) contributions in anomaly-score units; positive means the feature made the
    row look more abnormal than it would with that feature at its typical value.
    """
    values = np.asarray(values, dtype=float)
    n, d = values.shape
    out = np.zeros((n, d))
    for i in range(0, n, chunk):
        block = values[i:i + chunk]
        k = len(block)
        perturbed = np.repeat(block, d, axis=0)
        for j in range(d):
            perturbed[j::d, j] = normal[j]
        base = -model.decision_function(pd.DataFrame(block, columns=cols))
        drop = -model.decision_function(pd.DataFrame(perturbed, columns=cols)).reshape(k, d)
        out[i:i + k] = base[:, None] - drop
    return out


def phrase(contrib, z, cols, top=2):
    order = np.argsort(contrib)[::-1]
    parts = []
    for j in order[:top]:
        if contrib[j] <= 1e-4:
            break
        metric, aspect = label(cols[j])
        parts.append(f"{metric} {aspect} ({z[j]:+.1f} sigma)")
    return ", ".join(parts)


def explain(part, model, train, cols, top=2):
    """Fill a 'drivers' column: empty for normal rows, a short reason for flagged ones."""
    out = np.full(len(part), "", dtype=object)
    flag = part.if_flag.to_numpy() == 1
    if not flag.any():
        return out
    idx = np.flatnonzero(flag)
    mean = train[cols].mean().to_numpy()
    std = train[cols].std().replace(0, 1).to_numpy()
    values = part[cols].to_numpy(dtype=float)
    contrib = attribute(model, values[idx], train[cols].median().to_numpy(), cols)
    z = (values[idx] - mean) / std
    for r, row in enumerate(idx):
        out[row] = phrase(contrib[r], z[r], cols, top)
    return out


if __name__ == "__main__":
    from anomaly import detect

    scored, _ = detect()
    test = scored[(scored.split == "test") & (scored.if_flag == 1)]
    print(f"{len(test)} flagged test minutes, {test.drivers.ne('').mean():.1%} with an explanation\n")
    for kind, g in test.groupby("anomaly_type"):
        r = g.iloc[0]
        print(f"{kind:12s} {r.server} {str(r.timestamp)[:16]}  score {r.anomaly_score:.2f}")
        print(f"             -> {r.drivers or 'no single dominant signal'}")
