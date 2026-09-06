from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from typing import Iterable, Mapping

@dataclass(frozen=True, slots=True)
class FeatureScaler:
    features: tuple[str, ...]
    means: Mapping[str, float]
    scales: Mapping[str, float]
    fitted_until: datetime

    def transform(self, vector: Mapping[str,float]) -> dict[str,float]:
        out={}
        for f in self.features:
            mean=self.means.get(f,0.0)
            scale=self.scales.get(f,1.0) or 1.0
            out[f]=(float(vector.get(f,0.0))-mean)/scale
        return out

def fit_scaler(vectors: Iterable[Mapping[str,float]], *, fitted_until: datetime) -> FeatureScaler:
    rows=list(vectors)
    features=tuple(sorted({k for r in rows for k in r.keys()}))
    means={}
    scales={}
    for f in features:
        xs=[float(r.get(f,0.0)) for r in rows]
        if not xs:
            means[f]=0.0; scales[f]=1.0; continue
        mean=sum(xs)/len(xs)
        var=sum((x-mean)**2 for x in xs)/len(xs)
        means[f]=mean
        scales[f]=sqrt(var) or 1.0
    return FeatureScaler(features,means,scales,fitted_until)
