"""Web versions of the paper's charts (SVG, transparent background, one light and one dark variant each).
Adapted from the paper's plotting scripts (Flowmap_OPD/figures/plot_src: paper_style.py, consolidation_gain.py,
mechanism_curves.py, two_teacher_grpo.py, imagenet_three_rewards.py, consistency_monitor.py); same data, same encodings.
Run: /mnt/data/zhiqili/venvs/cosmos_post-training/bin/python tools/make_charts.py"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1]; OUT = R / "assets/fig"; DATA = Path(__file__).parent / "data"
THEMES = {
 "light": dict(fg="#1b2430", mute="#5b6675", grid="#e4e8ee", ours="#0072B2", vel0="#56B4E9", source="#CC79A7", detmap="#D55E00",
               stomap="#E69F00", grpo="#D55E00", nft="#009E73", ties="#E69F00", avg="#CC79A7", base="#555555", dest="#009E73", edge="#ffffff", warn="#B4480A"),
 "dark": dict(fg="#e6eaf0", mute="#a3adba", grid="#2b3442", ours="#4aa8e8", vel0="#8fd0f5", source="#e19bc3", detmap="#f0854a",
              stomap="#f2b632", grpo="#f0854a", nft="#35c49a", ties="#f2b632", avg="#e19bc3", base="#9aa3ae", dest="#35c49a", edge="#11161d", warn="#f0a070"),
}
T = None
def use(theme):
    global T; T = THEMES[theme]
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans", "font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
        "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6, "legend.frameon": False,
        "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": T["grid"], "grid.linewidth": 0.5, "lines.linewidth": 1.2, "lines.markersize": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "text.color": T["fg"], "axes.labelcolor": T["fg"], "axes.edgecolor": T["mute"], "xtick.color": T["mute"], "ytick.color": T["mute"],
        "xtick.labelcolor": T["fg"], "ytick.labelcolor": T["fg"], "axes.titlecolor": T["fg"],
        "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none", "savefig.transparent": True, "svg.fonttype": "path"})
def save(fig, name, theme):
    fig.savefig(OUT / f"{name}_{theme}.svg"); plt.close(fig)

def consolidation(theme):
    TASKS = ["GenEval", "OCR", "PickScore"]
    D = {"FLUX.1-lite-8B": {"base": [0.504, 0.349, 20.98], "spec": [0.845, 0.850, 23.08], "ours": [0.858, 0.883, 23.15], "grpo": [0.733, 0.795, 22.92],
                            "nft": [0.635, 0.717, 21.69], "ties": [0.823, 0.652, 21.99], "avg": [0.742, 0.657, 22.12]},
         "SD3.5-Medium": {"base": [0.726, 0.569, 21.69], "spec": [0.868, 0.912, 23.52], "ours": [0.872, 0.905, 23.40], "grpo": [0.713, 0.824, 23.11],
                          "nft": [0.732, 0.865, 22.18], "ties": [0.816, 0.779, 22.49], "avg": [0.789, 0.755, 22.38]}}
    METHODS = [("avg", "Merge (avg)", "v"), ("ties", "TIES", "^"), ("nft", "MeanFlowNFT", "D"), ("grpo", "FlowMap-GRPO", "s"), ("ours", "FlowMap-OPD (ours)", "o")]
    steps = [40, 80, 120, 160, 200, 240, 280, 300]
    ocr = [0.6222, 0.7641, 0.8173, 0.8347, 0.8452, 0.8693, 0.8860, 0.8830]
    pick = [21.9587, 22.3719, 22.6574, 22.8454, 22.9794, 23.0653, 23.1367, 23.1502]
    B = {"ocr": 0.349, "pick": 20.98}; SP = {"ocr": 0.8504, "pick": 23.0772}
    fig = plt.figure(figsize=(6.2, 2.05))
    gs = fig.add_gridspec(1, 3, left=.075, right=.99, top=.78, bottom=.2, wspace=.42)
    a = fig.add_subplot(gs[0]); b = fig.add_subplot(gs[1]); c = fig.add_subplot(gs[2], sharey=b)
    pos = b.get_position(); pc = c.get_position(); c.set_position([pos.x1 + .02, pc.y0, pc.x1 - pos.x1 - .02, pc.height])
    a.axhspan(100, 112, color=T["ours"], alpha=.1, lw=0); a.axhline(100, color=T["fg"], lw=.8, ls=(0, (4, 2)))
    for v, k, col, mk, lab, off, i in [(pick, "pick", T["vel0"], "s", "PickScore", (4, -11), 3), (ocr, "ocr", T["ours"], "o", "OCR", (-18, 6), 1)]:
        y = [100 * (x - B[k]) / (SP[k] - B[k]) for x in v]
        a.plot(steps, y, "-", color=col, lw=1.6, solid_capstyle="round"); a.plot(steps, y, mk, color=col, ms=3.2, mec=T["edge"], mew=.5)
        a.annotate(lab, (steps[i], y[i]), xytext=off, textcoords="offset points", color=col, fontsize=6.5, fontweight="bold")
    a.set_xlim(25, 315); a.set_ylim(40, 112); a.set_xticks([40, 170, 300]); a.set_yticks([50, 75, 100]); a.set_yticklabels(["50%", "75%", "100%"])
    a.set_xlabel("Training update", labelpad=2); a.grid(axis="x", visible=False); a.set_title("FLUX student during distillation", pad=4)
    for ax, (name, d) in zip((b, c), D.items()):
        gain = lambda k: [100 * (v - b0) / (s - b0) for v, b0, s in zip(d[k], d["base"], d["spec"])]
        ax.axvspan(100, 125, color=T["ours"], alpha=.1, lw=0)
        ax.axvline(100, color=T["fg"], lw=.8, ls=(0, (4, 2)), zorder=1); ax.axvline(0, color=T["mute"], lw=.6, zorder=1)
        for k, lab, mk in METHODS:
            ours = k == "ours"
            ax.scatter(gain(k), range(3), marker=mk, s=46 if ours else 20, color=T[k], zorder=5 if ours else 3,
                       edgecolor=T["edge"] if ours else "none", linewidth=.7, label=lab, alpha=1 if ours else .92)
        ax.set_xlim(-18, 122); ax.set_ylim(2.6, -.6); ax.set_xticks([0, 100]); ax.set_xticklabels(["base", "specialist"])
        ax.grid(axis="y", visible=False); ax.set_title(name, pad=4); ax.tick_params(axis="y", length=0)
    b.set_yticks(range(3)); b.set_yticklabels(TASKS); plt.setp(c.get_yticklabels(), visible=False)
    h, l = b.get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="upper center", ncol=5, columnspacing=1.2, handletextpad=.2, fontsize=6.5, bbox_to_anchor=(.5, 1.02))
    fig.text(.69, .02, "Share of the specialist's gain over the base", ha="center", fontsize=7)
    save(fig, "consolidation_gain", theme)

def mechanism(theme):
    EPOCH = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300]
    CURVES = {"velocity_consistency_0.01": [22.68, 18.65, 18.84, 18.82, 18.71, 18.64, 18.34, 18.76, 18.26, 18.85, 18.03, 18.14, 18.23], "velocity_consistency_0": [22.68, 18.5, 19.76, 20.8, 21.48, 22.04, 22.38, 21.54, 22.57, 21.23, 20.6, 22.03, 21.72], "source_induced": [22.68, 21.47, 22.18, 21.75, 20.36, 20.5, 20.32, 20.98, 20.2, 20.34, 20.29, 20.24, 20.04], "deterministic_map": [22.68, 29.83, 29.06, 31.98, 28.97, 32.76, 30.98, 27.45, 30.25, 30.68, 29.5, 28.76, 32.84], "stochastic_map_0.8": [22.68, 24.67, 29.39, 28.72, 27.48, 26.37, 29.5, 26.92, 27.01, 32.29, 30.26, 27.46, 27.89]}
    BASE = 22.68; KS = [3, 4, 7, 15]
    SWEEP = {'base': [22.48, 22.72, 22.88, 22.87], 'deterministic_map': [36.92, 32.31, 28.35, 27.53], 'source_induced': [20.42, 19.99, 19.77, 19.71], 'velocity_consistency_0': [23.58, 21.44, 19.29, 19.17], 'velocity_consistency_0.01': [18.14, 18.33, 18.33, 18.56]}
    STYLE = {'detmap': ('deterministic_map', 'Det. map', 32.84), 'stomap': ('stochastic_map_0.8', 'Stoch. map', 27.89),
             'vel0': ('velocity_consistency_0', 'Velocity, $\\lambda_c=0$', 22.6), 'source': ('source_induced', 'Source induced', 20.35),
             'ours': ('velocity_consistency_0.01', 'Ours, $\\lambda_c=0.01$', 17.9)}
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.4, 2.25), sharey=True, gridspec_kw={'width_ratios': [1.75, 1]})
    fig.subplots_adjust(left=.09, right=.995, top=.9, bottom=.17, wspace=.07)
    def draw(ax, x, y, k):
        ours = k == 'ours'; c = T[k]
        ax.plot(x, y, '-', color=c, lw=2.0 if ours else 1.0, alpha=1 if ours else .9, zorder=5 if ours else 2, solid_capstyle='round')
        ax.plot(x, y, 'o', color=c, ms=3.6 if ours else 2.4, mec=T["edge"], mew=.5, zorder=6 if ours else 3)
    for ax in (a, b):
        ax.axhspan(BASE, 39, color=T["detmap"], alpha=.06, lw=0, zorder=0)
        ax.set_ylim(16, 38.5); ax.grid(axis='x', visible=False)
    a.plot([0, 300], [BASE, BASE], color=T['base'], ls=(0, (4, 2)), lw=.8, zorder=1)
    b.plot(range(4), SWEEP['base'], ls=(0, (4, 2)), color=T['base'], lw=.8, zorder=1)
    for k, (key, lab, ylab) in STYLE.items():
        draw(a, EPOCH, CURVES[key], k)
        if key in SWEEP: draw(b, range(4), SWEEP[key], k)
        a.text(308, ylab, lab, color=T[k], fontsize=6.5, va='center', ha='left', fontweight='bold' if k == 'ours' else 'normal', clip_on=False)
    a.text(118, BASE + .45, 'base student', color=T['base'], fontsize=6, va='bottom')
    a.text(150, 37.2, 'worse than the base', color=T["warn"], fontsize=6, ha='center', va='center', style='italic')
    a.set_xlim(-8, 430); a.set_xticks([0, 100, 200, 300]); a.set_xlabel('Student epoch', x=.35); a.set_ylabel('FID $\\downarrow$', labelpad=2)
    a.spines['bottom'].set_bounds(-8, 300)
    a.set_title('During distillation, $K=3$', pad=4, x=.36)
    b.set_xlim(-.25, 3.25); b.set_xticks(range(4)); b.set_xticklabels(KS); b.set_xlabel('Sampling steps $K$')
    b.set_title('Epoch 300, varying $K$', pad=4); b.tick_params(axis='y', length=0)
    save(fig, "mechanism_curves", theme)

def two_teacher_data():
    f = DATA / "two_teacher_grpo.json"
    if f.exists(): return json.loads(f.read_text())
    D = "/mnt/data/zhiqili/wm_post-training/setup/plot_data/"   # as in the paper's two_teacher_grpo.py
    dig = json.load(open(D + "two_teacher_from_pdf.json")); opd = {}
    for l in open(D + "full_eval_metrics.jsonl"):
        r = json.loads(l)
        if r.get("eval_weight_type", "ema") != "ema": continue
        for k, n in (("eval_ocr_reward_ocr", "ocr"), ("eval_pickscore_reward_pickscore", "pick")):
            if k in r: opd.setdefault(n, {})[int(r["step"])] = r[k]
    BASE = {"ocr": 0.3491, "pick": 20.9758}; FINAL = {"ocr": 0.8629, "pick": 23.1677}; out = {}
    for n in ("ocr", "pick"):
        g = [(x, y) for x, y in dig[n]["grpo"] if 15 <= x <= 1450 and abs(x - 20 * round(x / 20)) < 1.5 and y > (0.3 if n == "ocr" else 20.5)]
        g = sorted({round(x / 20) * 20: y for x, y in g}.items())
        out[n] = {"grpo_x": [0] + [x for x, _ in g], "grpo_y": [BASE[n]] + [y for _, y in g],
                  "opd_x": [0] + sorted(opd[n]) + [300], "opd_y": [BASE[n]] + [opd[n][s] for s in sorted(opd[n])] + [FINAL[n]]}
    f.write_text(json.dumps(out)); return out
def two_teacher(theme):
    d = two_teacher_data(); SPEC = {"ocr": 0.8504, "pick": 23.0772}; FINAL = {"ocr": 0.8629, "pick": 23.1677}
    fig, axes = plt.subplots(1, 2, figsize=(4.4, 2.1))
    for ax, n, lab in zip(axes, ("ocr", "pick"), ("OCR accuracy", "PickScore")):
        ax.plot(d[n]["grpo_x"], d[n]["grpo_y"], color=T["grpo"], lw=1.1, label="FlowMap-GRPO")
        ax.plot(d[n]["opd_x"], d[n]["opd_y"], "-", color=T["ours"], lw=1.8, label="FlowMap-OPD (ours)", zorder=5)
        ax.plot(d[n]["opd_x"], d[n]["opd_y"], "o", color=T["ours"], ms=3.2, mec=T["edge"], mew=.5, zorder=6)
        ax.axhline(SPEC[n], color=T["fg"], ls=(0, (4, 2)), lw=0.9, label="specialist")
        ax.annotate(("%.3f" if n == "ocr" else "%.2f") % FINAL[n], (300, FINAL[n]), xytext=(9, -15), textcoords="offset points", color=T["ours"], fontsize=7, fontweight="bold")
        ax.set_xlabel("Training update"); ax.set_ylabel(lab); ax.set_xticks([0, 700, 1400]); ax.grid(axis="x", visible=False)
    axes[1].legend(loc="lower right", frameon=False, fontsize=6.5)
    fig.tight_layout(pad=0.4, w_pad=1.2)
    save(fig, "two_teacher_grpo", theme)

def imagenet(theme):
    d = json.loads((DATA / "imagenet_three_rewards.json").read_text()); EP = d["comparison_epoch"]
    REW = ["mmd", "classifier", "dino_prototype"]; NAME = {"mmd": "MMD", "classifier": "Classifier", "dino_prototype": "DINO"}
    YL = {"mmd": "FID $\\downarrow$", "classifier": "Target log-probability $\\uparrow$", "dino_prototype": "Cosine similarity $\\uparrow$"}
    SEL = [("velocity_consistency_0.01", "Ours, $\\lambda_c=0.01$", T["ours"]), ("velocity_consistency_0", "Velocity, $\\lambda_c=0$", T["vel0"]),
           ("source_induced", "Source induced", T["source"]), ("destination_induced", "Destination induced", T["dest"]),
           ("deterministic_map", "Deterministic map", T["detmap"]), ("stochastic_map_0.4", "Stochastic map", T["stomap"])]
    fig, axs = plt.subplots(1, 3, figsize=(6.875, 2.3)); fig.subplots_adjust(left=.06, right=.995, top=.91, bottom=.33, wspace=.3)
    for ax, r in zip(axs, REW):
        for k, lab, c in SEL:
            pts = [p for p in d["students"][r][k] if p["epoch"] <= EP]; ours = k == "velocity_consistency_0.01"
            x = [p["epoch"] for p in pts]; y = [p["4step"] for p in pts]
            ax.plot(x, y, "-", color=c, lw=2.0 if ours else 1.0, zorder=5 if ours else 2, solid_capstyle="round", label=lab)
            ax.plot(x, y, "o", color=c, ms=3.2 if ours else 2.1, mec=T["edge"], mew=.45, zorder=6 if ours else 3)
        ax.axhline(d["teachers"][r]["4step"], color=T["fg"], ls=(0, (4, 2)), lw=.9, label="XL/2 teacher")
        ax.axhline(d["bases"][r]["4step"], color=T["base"], ls=(0, (1, 2)), lw=.9, label="B/2 base")
        ax.set_title(NAME[r], pad=3); ax.set_xlabel("Student epoch"); ax.set_ylabel(YL[r], labelpad=2); ax.grid(axis="x", visible=False); ax.set_xticks([0, 100, 200, 300])
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, columnspacing=1.6, handlelength=1.8, handletextpad=.5, fontsize=6.6)
    save(fig, "imagenet_three_rewards", theme)

def consistency(theme):
    LAM = ["0", "0.001", "0.01", "0.1", "1"]; RES = [0.8, 0.6493258535861969, 0.763, 0.401, 0.179]
    MAP = [0.003607218960674273, 0.0036769225796239296, 0.005003561784161088, 0.006981714117434076, 0.010472571176151114]
    C1, C2 = T["ours"], T["detmap"]
    f, ax = plt.subplots(figsize=(3.0, 2.3)); right = ax.twinx()
    ax.axvspan(.5, 1.5, color=C1, alpha=.1, lw=0); ax.text(1, .86, "chosen", ha="center", va="top", fontsize=6.2, color=C1)
    ax.plot(range(5), RES, "-", color=C1, lw=1.5); ax.plot(range(5), RES, "o", color=C1, ms=3.6, mec=T["edge"], mew=.5)
    right.plot(range(5), [1e3 * v for v in MAP], "--", color=C2, lw=1.3); right.plot(range(5), [1e3 * v for v in MAP], "s", color=C2, ms=3.4, mec=T["edge"], mew=.5)
    ax.set_xlabel("$\\lambda_c$"); ax.set_ylabel("Consistency residual", color=C1); ax.set_ylim(0, .9); ax.set_xticks(range(5)); ax.set_xticklabels(LAM)
    right.set_ylabel("Teacher map MSE ($\\times10^{-3}$)", color=C2); right.set_ylim(0, 12)
    ax.tick_params(axis="y", labelcolor=C1); right.tick_params(axis="y", labelcolor=C2); right.spines["right"].set_visible(True); right.grid(False); ax.grid(axis="x", visible=False)
    f.subplots_adjust(left=.17, right=.83, bottom=.18, top=.96)
    save(f, "consistency_monitor", theme)

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        use(theme)
        for fn in (consolidation, mechanism, two_teacher, imagenet, consistency): fn(theme)
    print(sorted(p.name for p in OUT.glob("*.svg")), round(sum(p.stat().st_size for p in OUT.glob("*.svg")) / 1e3), "kB")
