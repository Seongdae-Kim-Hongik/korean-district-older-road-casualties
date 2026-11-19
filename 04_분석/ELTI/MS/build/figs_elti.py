# -*- coding: utf-8 -*-
# figs_elti.py — ELTI figures(figs_sknd.py 이식). 컬러, 패널 문자 fig.text 상수(소문자 '(a)'), 방위표 3배, 그림 안 설명문 없음, 시군구 코드 결합. TIFF: 지도 600 dpi, 선화 1200 dpi.
#  Fig 1 전국 (a) 연간 노인 부상자 2011–2025 (b) 65+ 10만 명당 (c) 전체 경찰 집계 사고 100건당 노인 부상자 · Fig 2 지도 (a) 노인 인구 기준 SMR (b) 사고 기준 비 (c) 핫·콜드스팟 · Fig 3 모형별 RR
import os, sys, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_elti import load, DESC, B, CAR, TCI, TE, HYP
SHP = os.environ.get("ST_SHP", os.path.expandvars("$ST_DATA_ROOT") + "/기타/R_Studio/FBD_DATA_ZIP/final.shp")
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 170 * MM; DPI = 600; LW = 0.3
PANEL_LABEL_PT = 54
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "legend.fontsize": 8, "legend.title_fontsize": 8.5, "axes.linewidth": 0.6, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
ONLY = set(sys.argv[1:]) or {"1", "2", "3"}
if "3" in ONLY: N = load()
else:
    import json as _j
    _s6 = pd.read_csv(os.path.join(B, "results_std3", "S6_spatial_RR.csv"), dtype={"sigungu_cd": str})
    N = dict(nat=pd.read_csv(os.path.join(DESC, "D1_national.csv")).set_index("year"), s6=_s6, n_hot=int((_s6["class"] == "hotspot").sum()), n_cold=int((_s6["class"] == "coldspot").sum()))
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["region"] = G.region.map(NFC); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
assert G.region.is_unique and len(G) == 229
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def label(fig, ax, ch, dx=-0.02, dy=0.01):
    bb = ax.get_position(); fig.text(max(bb.x0 + dx, 0.012), bb.y1 + dy, f"({ch.lower()})", fontsize=PANEL_LABEL_PT, fontweight="bold", va="bottom", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#303030", linewidth=0.5); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by, bh = x0 + 0.55 * W_, y0 + 0.03 * H_, 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + k, by + bh + 0.01 * H_, t, ha="center", va="bottom", fontsize=6.5)
    ax.text(bx + 100000 + 0.015 * W_, by + bh / 2, "km", ha="left", va="center", fontsize=6.5)
    nx, ny, nw, nh = x0 + 0.93 * W_, y0 + 0.40 * H_, 0.06 * W_, 0.20 * H_
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=22, fontweight="bold")
def save(fig, k, dpi=DPI):
    p = os.path.join(FIG, f"ELTI_Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size

if "1" in ONLY:
    D = N["nat"]; yrs = list(range(2011, 2026)); D = D.reindex(yrs)
    fig = plt.figure(figsize=(W, 3.6)); axs = [fig.add_axes([0.085 + i * 0.325, 0.16, 0.245, 0.62]) for i in range(3)]
    a = axs[0]; a.bar(yrs, D.injured / 1000, color=["#B2182B" if y == 2025 else "#2166AC" for y in yrs], width=0.75)
    assert D.injured.max() / 1000 < 50; a.set_ylim(0, 50); a.set_ylabel("Injured people aged ≥ 65 years (thousands)")
    a = axs[1]; a.plot(yrs, D.rate_per100k_65, color="#000000", marker="o", ms=2.8, lw=1.0)
    assert 350 < D.rate_per100k_65.min() and D.rate_per100k_65.max() < 650; a.set_ylim(300, 650); a.set_ylabel("Per 100,000 people aged ≥ 65 years")
    a = axs[2]; a.plot(yrs, D.injured_per_crash100, color="#8073AC", marker="s", ms=2.8, lw=1.0)
    assert D.injured_per_crash100.max() < 30; a.set_ylim(0, 30); a.set_ylabel("Per 100 police-reported crashes")
    for a in axs: a.set_xticks([2011, 2015, 2020, 2025]); a.spines[["top", "right"]].set_visible(False); a.tick_params(labelsize=8); a.axvspan(2019.5, 2020.5, color="#EFEFEF", zorder=0)
    for a, ch in zip(axs, "abc"): label(fig, a, ch, dx=-0.08, dy=0.03)
    s = save(fig, 1, dpi=1200); print("Fig1", s)

if "2" in ONLY:
    P = pd.read_csv(os.path.join(B, "panel_ELTI_std3.csv")); E = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(B)), "02_패널", "ELTI_E69.csv"), dtype={"sigungu_cd": str})
    E = E[E.year <= 2024]; R2C = dict(zip(G.region, G.cd))
    S6 = N["s6"].copy(); S6["cd"] = S6.sigungu_cd.astype(str); assert S6.cd.nunique() == 229 and set(S6.cd) == set(G.cd); d = S6.set_index("cd")
    sm = P.groupby("fbd_region").agg(c=("cases", "sum"), e=("E", "sum")); sm.index = sm.index.map(NFC).map(R2C); assert sm.index.notna().all() and sm.index.nunique() == 229
    d["SMR"] = (sm.c / sm.e).reindex(d.index)
    sc = E.groupby("sigungu_cd").agg(c=("cases", "sum"), e=("E_crash", "sum")); assert set(sc.index) == set(G.cd); d["CR"] = (sc.c / sc.e).reindex(d.index)
    BR = [0, 0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0, 99]; LB = ["< 0.50", "0.50–0.66", "0.67–0.79", "0.80–0.99", "1.00–1.24", "1.25–1.49", "1.50–1.99", "≥ 2.00"]
    PAL = ["#053061", "#2166AC", "#67A9CF", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
    for c in ("SMR", "CR"): assert d[c].min() >= BR[0] and d[c].max() < BR[-1]
    fig = plt.figure(figsize=(W, 4.6)); pos = [[0.00, 0.20, 0.33, 0.70], [0.335, 0.20, 0.33, 0.70], [0.67, 0.20, 0.33, 0.70]]
    for (col, ch), p in zip((("SMR", "a"), ("CR", "b")), pos[:2]):
        ax = fig.add_axes(p); gg = G.copy(); gg["v"] = gg.cd.map(d[col]); assert gg.v.notna().all()
        gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, ch, dx=0.0, dy=-0.005)
    fig.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)], title="Observed/expected ((a) per older resident; (b) per crash)", loc="upper center", bbox_to_anchor=(0.335, 0.20), ncol=4, frameon=False, columnspacing=0.9, handlelength=1.2, fontsize=7)
    ax = fig.add_axes(pos[2]); gg = G.copy(); gg["k"] = gg.cd.map(d["class"]); assert gg.k.notna().all()
    CK = {"hotspot": "#B2182B", "coldspot": "#2166AC", "neutral": "#EFEFEF"}; gg.plot(ax=ax, color=gg.k.map(CK), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, "c", dx=0.0, dy=-0.005)
    fig.legend(handles=[Patch(facecolor=CK[k], edgecolor="#777777", linewidth=LW, label=l) for k, l in (("hotspot", f"Hot spot ({N['n_hot']})"), ("coldspot", f"Cold spot ({N['n_cold']})"), ("neutral", "Neither"))],
               loc="upper center", bbox_to_anchor=(0.835, 0.20), ncol=1, frameon=False, fontsize=7.5, handlelength=1.2)
    s = save(fig, 2); print("Fig2", s)

if "3" in ONLY:
    import content_elti as C
    LAB = {CAR: "Motor vehicles\nper resident", TCI: "Traffic culture\nindex", TE: "Tertiary-educated\nadults"}
    ORD = [CAR, TCI, TE]
    MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "o", "#000000"),
           ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)][:3], "D", "#B2182B"),
           ("Knorr-Held type III", lambda v: N["s43"][("KH_typeIII", v)][:3], "D", "#F4A582"),
           ("Spatial+-type", lambda v: N["s41"][("D1_spatial_plus", v)][:3], "v", "#8073AC"),
           ("Excluding top tenth by crash rate", lambda v: C.X(C.TOP, v)[:3], "s", "#2166AC"),
           ("Adding all-crash rate", lambda v: C.X("plus_all_crash_rate", v)[:3], "^", "#E08214"),
           ("Expected counts from all crashes", C.CR, "^", "#1B7837")]
    VALS = [f(v) for v in ORD for _, f, _, _ in MOD]; lo_all = min(t[1] for t in VALS); hi_all = max(t[2] for t in VALS)
    fig, ax = plt.subplots(figsize=(W, 4.4)); fig.subplots_adjust(left=0.19, right=0.98, top=0.97, bottom=0.30)
    off = np.linspace(-0.36, 0.36, len(MOD))
    for i, v in enumerate(ORD):
        for (lab, f, mk, fc), o in zip(MOD, off):
            e, lo_, hi_ = f(v); ax.plot([lo_, hi_], [i + o] * 2, color=fc, lw=0.9); ax.plot(e, i + o, marker=mk, mfc=fc, mec=fc, ms=3.8, ls="none")
    ax.axvline(1, color="#808080", lw=0.6); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
    ax.set_xscale("log"); xt = [0.8, 0.9, 1.0, 1.1]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
    ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
    ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(handles=[Line2D([0], [0], color=fc, marker=m, mfc=fc, mec=fc, lw=0.9, ms=3.8, label=l) for l, _, m, fc in MOD], loc="upper center", bbox_to_anchor=(0.42, -0.15), ncol=3, frameon=False, fontsize=7.5)
    s = save(fig, 3); print("Fig3", s)
