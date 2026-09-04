#!/usr/bin/env python3
"""representability.py — (Delta,p)가 정해지면 최적화기와 무관한 진단량.

그래프 거리 delta 가 R^p 에서 실현되는가를 임베딩 없이 잰다. Schoenberg 판정:

    G = -1/2 C Delta^(2) C ,  C = I - 11^T/N
    delta 가 R^r 에서 실현 가능  <=>  G >= 0 이고 rank G <= r

따라서 결손

    D_p = [ sum_{a>p} max(mu_a,0) + sum_a max(-mu_a,0) ] / sum_a |mu_a|   in [0,1]

이 0 인 것과 정확 실현이 동치이다. D_p 는 (Delta,p)만의 함수라 optimizer,
초기화, stopping rule과 무관하지만, graph-to-dissimilarity map과 p에는 의존한다.
또한 0-level set은 Schoenberg 정리로 canonical하지만, 양의 결손을 정규화하는 이
L1 spectral ratio 자체가 유일한 representability 척도인 것은 아니다. 전역 scale에는
불변이고 p에 대해 비증가한다.

노트의 kappa_+ 는 projected Hessian 의 positive spectral scale 로 이미 쓰이므로
여기서는 D_p 를 쓴다.
"""
from __future__ import annotations

import numpy as np


def gram_cmds(Delta: np.ndarray) -> np.ndarray:
    """이중중심화. G = -1/2 C Delta^(2) C."""
    N = Delta.shape[0]
    D2 = Delta.astype(np.float64) ** 2
    rm = D2.mean(axis=1, keepdims=True)
    G = -0.5 * (D2 - rm - rm.T + D2.mean())
    return 0.5 * (G + G.T)


def deficiency(mu: np.ndarray, p: int) -> float:
    """D_p. mu 는 내림차순 고유값."""
    tot = np.abs(mu).sum()
    if tot <= 0:
        return 0.0
    excess = np.maximum(mu[p:], 0.0).sum()          # 차원 초과 성분
    nonEuc = np.maximum(-mu, 0.0).sum()             # 비유클리드 성분
    return float((excess + nonEuc) / tot)


def node_frustration(G: np.ndarray, mu: np.ndarray, V: np.ndarray, p: int) -> np.ndarray:
    """노드별 spectral residual magnitude (이름은 하위호환 때문에 유지).

    G = sum_a mu_a v_a v_a^T 에서 p 차원으로 유지되는 부분을 빼고 남은 잔차의
    대각원소의 절댓값. 이는 D_p의 가법 분해도, 물리적 frustration의 국소 밀도도
    아니므로 탐색적 localization diagnostic으로만 사용한다.
    """
    keep = np.zeros_like(mu)
    idx = np.argsort(mu)[::-1][:p]
    keep[idx] = np.maximum(mu[idx], 0.0)
    Gp = (V * keep) @ V.T
    return np.abs(np.diag(G - Gp))


def analyze(Delta: np.ndarray, p_list=(1, 2, 3, 5, 10)) -> dict:
    G = gram_cmds(Delta)
    mu, V = np.linalg.eigh(G)
    mu = mu[::-1]
    V = V[:, ::-1]
    tot = np.abs(mu).sum()
    out = {
        "mu_top": mu[: min(50, mu.size)].astype(np.float32),
        "mu_bot": mu[-min(50, mu.size):].astype(np.float32),
        "mu_abs_sum": float(tot),
        "neg_frac": float(np.maximum(-mu, 0.0).sum() / tot) if tot > 0 else 0.0,
    }
    for p in p_list:
        if p < mu.size:
            out[f"D_{p}"] = deficiency(mu, p)
    out["phi_node"] = node_frustration(G, mu, V, 2).astype(np.float32)
    # p=2 cMDS 가 설명하는 관성 비율 (표준적인 '설명된 분산')
    pos = np.maximum(mu, 0.0)
    out["cmds_explained_2"] = float(pos[:2].sum() / pos.sum()) if pos.sum() > 0 else 0.0
    return out
