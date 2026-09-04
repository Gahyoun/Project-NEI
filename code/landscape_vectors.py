#!/usr/bin/env python3
"""landscape_vectors.py — 저장된 run-distance matrix의 cloud spectrum을 계산한다.

NEI 는 세 번 접힌다.

    X^(m)  --(1)-->  D^(m)  --(2)-->  {r_ij}  --(3)-->  I
    배치            거리행렬          쌍 위의 장         스칼라

(3) 은 '어느 쌍이 문제인가'를, (2) 는 '갈라진 것인가 퍼진 것인가'를 버린다.
현재 artifact의 Delta에는 raw distance cloud의 구조가 남아 있다.

    Delta_{mm'} = || D^(m) - D^(m') ||_F / scale

는 쌍공간 R^{N_+}에서의 **유클리드** 거리이므로, 이중중심화하면 run 구름의
Gram 행렬이 정확히 복원된다 (Schoenberg):

    G = -1/2 C Delta^2 C ,   C = I - 11^T/M ,   tr G = sum_{i<j} sigma^2_ij / scale^2

그러나 기존 scale은 하나의 global Frobenius scale이다. NEI는 pair마다
1/bar(d_ij)^2를 적용하므로, 이 Gram은 NEI와 같은 covariance operator가 아니다.
NEI-compatible spectrum에는

    z_m,ij = d_m,ij / (bar(d_ij) sqrt(N_+))

의 run distances가 필요하며, 그때 I=tr(G_z)/M이다. artifact에 Delta_kind가
"nei_standardized"라고 명시되지 않으면 이 스크립트의 trace와 d_eff는
raw-cloud diagnostic으로만 출력한다.

측정하는 것
-----------
  * 전체 고유값 스펙트럼 lam_1 >= ... >= lam_{M-1} >= 0
  * d_eff = (tr G)^2 / tr(G^2)        covariance effective rank
  * p1, p2                            상위 방향 분산 점유율
  * 이봉성                            PC1 위에서 1성분 대 2성분 GMM 의 dBIC 를
                                      **동일 스펙트럼의 가우스 구름**으로 모수
                                      부트스트랩해 보정한 p 값. PC1 을 분산최대
                                      방향으로 고른 선택편향이 널에도 똑같이
                                      들어가므로 편향이 상쇄된다.
  * out_lev                            sample-size-normalized leave-one-out dispersion loss.
                                      크면 '두 덩어리'가 아니라 '이상치 하나'.
  * gap2                              PC1 위 2-means 의 between/total (기술통계로만;
                                      단독으로는 basin 증거가 아니다 -- singleton
                                      분할에서 항등적으로 1 이 되기 때문)

이 스크립트는 임베딩을 다시 돌리지 않는다. 따라서 기존 raw Delta만 있는 경우
NEI-standardized covariance를 사후 복원할 수 없다.
"""
from __future__ import annotations

import argparse
import glob
import os

import numpy as np


# ---------------------------------------------------------------- run cloud
def gram_from_delta(D: np.ndarray) -> np.ndarray:
    """Delta (M,M) -> run 구름의 Gram 행렬. Schoenberg 이중중심화."""
    M = D.shape[0]
    C = np.eye(M) - 1.0 / M
    G = -0.5 * (C @ (D.astype(np.float64) ** 2) @ C)
    return 0.5 * (G + G.T)


def spectrum(G: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    w, V = np.linalg.eigh(G)
    return w[::-1], V[:, ::-1]


def coords(w: np.ndarray, V: np.ndarray, k: int) -> np.ndarray:
    """상위 k 주방향 위의 run 좌표 (M,k)."""
    k = min(k, (w > 0).sum())
    if k == 0:
        return np.zeros((V.shape[0], 0))
    return V[:, :k] * np.sqrt(w[:k])


# ---------------------------------------------------------------- 이봉성
def _gmm_dbic(x: np.ndarray) -> float:
    """1성분 대 2성분 가우스혼합의 BIC 차. 양수면 2성분 선호."""
    from sklearn.mixture import GaussianMixture

    x = x.reshape(-1, 1)
    s = x.std()
    if s <= 0 or not np.isfinite(s):
        return 0.0
    x = x / s
    try:
        b1 = GaussianMixture(1, covariance_type="full", random_state=0).fit(x).bic(x)
        b2 = GaussianMixture(
            2, covariance_type="full", n_init=5, random_state=0
        ).fit(x).bic(x)
    except Exception:
        return 0.0
    return float(b1 - b2)


def bimodality_p(w: np.ndarray, V: np.ndarray, n_boot: int, rng) -> tuple[float, float]:
    """PC1 이봉성의 부트스트랩 p 값.

    널은 '같은 고유값 스펙트럼을 가진 가우스 구름'이다. 널 표본마다 PCA 를
    다시 해서 PC1 을 뽑으므로, 분산최대 방향을 고르는 선택편향이 관측과 널에
    동일하게 들어간다. 이 보정을 빼면 어떤 구름이든 이봉으로 보인다.
    """
    M = V.shape[0]
    pos = w[w > 0]
    if pos.size == 0:
        return 0.0, 1.0
    obs = _gmm_dbic(coords(w, V, 1)[:, 0])
    if n_boot <= 0:
        return obs, float("nan")
    sd = np.sqrt(pos)
    ge = 0
    for _ in range(n_boot):
        Z = rng.standard_normal((M, pos.size)) * sd          # 같은 스펙트럼
        Z -= Z.mean(0)
        Gn = Z @ Z.T
        wn, Vn = spectrum(Gn)
        if _gmm_dbic(coords(wn, Vn, 1)[:, 0]) >= obs:
            ge += 1
    return obs, (ge + 1.0) / (n_boot + 1.0)


# ---------------------------------------------------------------- 이상치
def outlier_leverage(D: np.ndarray) -> float:
    """run 하나를 빼면 per-run dispersion이 최대 몇 비율로 주는가.

    두 덩어리로 갈라진 구름은 어느 run 을 빼도 총분산이 거의 그대로다.
    이상치 하나가 끌고 있는 구름은 그 run 을 빼면 총분산이 무너진다.
    """
    M = D.shape[0]
    tr_all = np.trace(gram_from_delta(D))
    if tr_all <= 0:
        return 0.0
    best = 0.0
    idx = np.arange(M)
    for m in range(M):
        sub = D[np.ix_(idx != m, idx != m)]
        t = np.trace(gram_from_delta(sub))
        # trace scales with sample count, so compare trace/M rather than raw trace.
        loss = 1.0 - (t / max(M - 1, 1)) / (tr_all / M)
        best = max(best, loss)
    return float(best)


def gap_2means(x: np.ndarray) -> float:
    """PC1 위 최적 2분할의 between/total. 기술통계일 뿐 basin 증거가 아니다."""
    s = np.sort(x)
    n = s.size
    if n < 4:
        return 0.0
    tot = ((s - s.mean()) ** 2).sum()
    if tot <= 0:
        return 0.0
    c = np.cumsum(s)
    k = np.arange(1, n)
    m1 = c[:-1] / k
    m2 = (c[-1] - c[:-1]) / (n - k)
    between = k * (m1 - s.mean()) ** 2 + (n - k) * (m2 - s.mean()) ** 2
    return float(between.max() / tot)


# ---------------------------------------------------------------- 분류
def classify(rec: dict, floor: float) -> str:
    """세 유형으로 가른다. 판정 못 하면 그렇다고 말한다."""
    if rec["trace"] <= floor:
        return "rigid"                       # 강체형: 구름 자체가 없다
    if rec["out_lev"] > 0.5:
        return "outlier"                     # 한 run 이 끌고 있다. 분리형이 아니다
    if rec["bimod_p"] < 0.05 and rec["d_eff"] < 5:
        return "split_cand"                  # 분리형 후보. 배치 재현성 확인 필요
    if rec["d_eff"] > 10 and rec["bimod_p"] > 0.20:
        return "diffuse_cloud_cand"           # support topology/softness는 아직 미판정
    return "unresolved"


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default=os.path.expanduser(
        "~/Real_network_NEI/referee_round/artifacts"))
    ap.add_argument("--out", default=os.path.expanduser(
        "~/Real_network_NEI/referee_round/out/landscape_vectors"))
    ap.add_argument("--n-boot", type=int, default=200)
    ap.add_argument("--floor", type=float, default=1e-12)
    a = ap.parse_args()
    rng = np.random.default_rng(20260904)

    recs, spectra = [], {}
    files = sorted(glob.glob(os.path.join(a.art, "*.npz")))
    for i, f in enumerate(files, 1):
        try:
            z = np.load(f, allow_pickle=True)
        except Exception as e:
            print(f"  [skip] {os.path.basename(f)}: {e}", flush=True)
            continue
        if "Delta" not in z.files:
            continue
        D = z["Delta"].astype(np.float64)
        M = D.shape[0]
        if M < 8:
            continue
        G = gram_from_delta(D)
        w, V = spectrum(G)
        pos = w[w > 1e-12 * max(w[0], 1e-300)]
        if pos.size == 0:
            continue
        tr = float(pos.sum())
        Y = coords(w, V, 3)
        dbic, pval = bimodality_p(w, V, a.n_boot, rng)
        name = os.path.basename(f)[:-4]
        delta_kind = str(z["Delta_kind"]) if "Delta_kind" in z.files else "raw_global_scale"
        rec = dict(
            name=name, N=int(z["N"]), E=int(z["E"]), M=M,
            delta_kind=delta_kind,
            trace=tr,
            d_eff=float(tr ** 2 / np.square(pos).sum()),
            p1=float(pos[0] / tr),
            p2=float(pos[1] / tr) if pos.size > 1 else 0.0,
            rank=int(pos.size),
            neg=float(-w[-1] / tr) if w[-1] < 0 else 0.0,
            kurt=float((((Y[:, 0] - Y[:, 0].mean()) / (Y[:, 0].std() + 1e-300)) ** 4).mean()),
            dbic=dbic, bimod_p=pval,
            gap2=gap_2means(Y[:, 0]),
            out_lev=outlier_leverage(D),
            frac_maxiter=float(np.mean(z["n_iter"] >= int(z["max_iter"])))
            if "n_iter" in z.files else float("nan"),
            lam_min_rel_med=float(np.median(z["lam_min_rel"]))
            if "lam_min_rel" in z.files else float("nan"),
        )
        rec["kind"] = classify(rec, a.floor)
        recs.append(rec)
        spectra[name] = pos.astype(np.float32)
        spectra[name + "__pc"] = Y.astype(np.float32)
        print(f"  [{i:3d}/{len(files)}] {name[:44]:<45} d_eff={rec['d_eff']:7.2f} "
              f"p={rec['bimod_p']:.3f} out={rec['out_lev']:.2f} {rec['kind']}", flush=True)

    if not recs:
        print("아티팩트 없음")
        return 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    import csv
    with open(a.out + ".csv", "w", newline="") as fh:
        wcsv = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(recs)
    np.savez_compressed(a.out + "_spectra.npz", **spectra)
    print(f"\n{len(recs)} 개 -> {a.out}.csv / _spectra.npz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
