"""Build the gallery assets, samples.js and the gallery part of asset-provenance.json from the unmodified model outputs.
Every tile is the full 512x512 output of the labelled model for the row's prompt and seed, re-encoded as WebP (no crop,
no retouching). Run: /mnt/data/zhiqili/venvs/cosmos_post-training/bin/python tools/build_gallery.py
Sources (read-only):
  FLUX.1  base + three specialists: appx_gallery_src/qualitative/<task>_<idx>_<seed>/{base,teacher_*}.png
          student (lambda_c 0.001, update 300 EMA; the checkpoint of the paper's tables): setup/fig3_tr3/out_all/<id>_velocity.png
          student (lambda_c 0, update 300 EMA) for ids without the former: appx_gallery_src/qualitative/<id>/velocity.png
          FlowMap-GRPO / MeanFlowNFT on three rewards (three ids): setup/fig3_tr3/out/<id>_{grpo3,mfnft3}.png
          prompts: causal_paper_experiment/arxiv_eval/prompts.json (the evaluation prompt file, keyed by id)
  SD3.5   OCR (t0) and GenEval (t2) test prompts: wm_post-training_figsd/[b_]<model>/<t>/NNNNNN.png with scores_*.jsonl / pref_*.jsonl
          preference: DrawBench dumps wm_post-training_dbench_<model>/images/NNNNNN.png with per-image PickScore
"""
import json, os, shutil
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1]
W = Path("/mnt/data/zhiqili/wm_post-training")
QUAL, STU, X3 = W / "appx_gallery_src/qualitative", W / "setup/fig3_tr3/out_all", W / "setup/fig3_tr3/out"
FS, DB = W / "wm_post-training_figsd", str(W / "wm_post-training_dbench_")
PROMPTS = {q["id"]: q["prompt"] for t in json.load(open("/mnt/home/zhiqili/causal/causal_paper_experiment/arxiv_eval/prompts.json")).values() for q in t}
SDM = {"base": "base", "ocr": "txt1000", "pick": "pref1500", "geneval": "comp1220", "grpo": "tr3_1500", "nft": "tr3_mfn750", "opd": "t3d300"}
FXM = {"base": "base", "ocr": "teacher_ocr", "pick": "teacher_pickscore", "geneval": "teacher_geneval"}

# ---- curated lists (selected examples) ----
FLUX = {
 "ocr": ["ocr_073_1701", "ocr_244_1701", "ocr_079_1701", "ocr_1016_2903", "ocr_123_2903", "ocr_320_2903", "ocr_927_1701",
         "ocr_370_1701", "ocr_414_2903", "ocr_498_2903", "ocr_506_1701", "ocr_073_2903", "ocr_1016_1701", "ocr_244_2903"],
 "pickscore": ["pickscore_493_1701", "pickscore_1282_1701", "pickscore_1656_1701", "pickscore_2027_2903", "pickscore_1480_1701",
               "pickscore_1992_1701", "pickscore_292_2903", "pickscore_1282_2903", "pickscore_2027_1701", "pickscore_493_2903",
               "pickscore_1656_2903", "pickscore_1992_2903", "pickscore_437_1701"],
 "geneval": ["geneval_079_1701", "geneval_320_1701", "geneval_506_1701", "geneval_123_2903", "geneval_073_2903", "geneval_414_1701",
             "geneval_498_1701", "geneval_079_2903", "geneval_072_2903", "geneval_109_2903", "geneval_318_2903", "geneval_123_1701",
             "geneval_320_2903", "geneval_506_2903"],
}
SD = {  # test-set / DrawBench row indices
 "ocr": [964, 65, 157, 623, 219, 983, 512, 755, 11, 239, 519, 663, 462, 321, 371],
 "pickscore": [456, 307, 35, 949, 170, 835, 178, 257, 503, 182, 829, 66, 981, 438],
 "geneval": [195, 2021, 1360, 1652, 1979, 1209, 2201, 837, 843, 1142, 2127, 1280, 1022, 1359],
}
WALL = [("sd35", "pickscore", 307), ("flux", "ocr", "ocr_244_1701"), ("sd35", "pickscore", 170), ("flux", "pickscore", "pickscore_1282_1701"),
        ("sd35", "ocr", 623), ("flux", "pickscore", "pickscore_493_1701"), ("sd35", "pickscore", 456), ("flux", "ocr", "ocr_414_2903"),
        ("sd35", "pickscore", 949), ("flux", "pickscore", "pickscore_2027_2903"), ("sd35", "ocr", 219), ("flux", "geneval", "geneval_320_1701"),
        ("sd35", "pickscore", 35), ("flux", "ocr", "ocr_073_1701"), ("sd35", "pickscore", 835), ("flux", "pickscore", "pickscore_1656_1701"),
        ("sd35", "ocr", 512), ("flux", "ocr", "ocr_370_1701"), ("sd35", "pickscore", 182), ("flux", "pickscore", "pickscore_1480_1701"),
        ("sd35", "ocr", 755), ("flux", "geneval", "geneval_079_1701"), ("sd35", "pickscore", 66), ("flux", "ocr", "ocr_1016_2903")]

G = R / "assets/gallery"
if G.exists(): shutil.rmtree(G)
def put(src, bb, name):
    im = Image.open(src).convert("RGB"); assert im.size == (512, 512), (src, im.size)
    out = G / bb / f"{name}.webp"; out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=84, method=6)
    return im
def thumb(im, bb, sid):
    im.resize((120, 120), Image.LANCZOS).save(G / bb / f"{sid}_thumb.webp", "WEBP", quality=78, method=6)

gallery = {"flux": {}, "sd35": {}}; prov = {"flux": [], "sd35": []}
# ---- FLUX.1 ----
for task, ids in FLUX.items():
    rows = []
    for sid in ids:
        pid, seed = sid.rsplit("_", 1); cols = ["base", "ocr", "pick", "geneval"]; src = {m: QUAL / sid / f"{FXM[m]}.png" for m in cols}
        if (X3 / f"{sid}_grpo3.png").exists():
            pass  # the reward-trained columns are not shown on the page
        main = (STU / f"{sid}_velocity.png").exists()
        cols.append("opd"); src["opd"] = STU / f"{sid}_velocity.png" if main else QUAL / sid / "velocity.png"
        for m in cols:
            im = put(src[m], "flux", f"{sid}_{m}")
            if m == "opd": thumb(im, "flux", sid)
        lc = "0.001" if main else "0"
        rows.append({"id": sid, "prompt": PROMPTS[pid], "seed": int(seed), "cols": cols, "lc": lc})
        prov["flux"].append({"id": sid, "task": task, "prompt_id": pid, "seed": int(seed), "prompt": PROMPTS[pid],
                             "student_checkpoint": f"update 300 EMA, lambda_c={lc}", "sources": {m: str(src[m]) for m in cols}})
    gallery["flux"][task] = rows

# ---- SD3.5-Medium ----
def load(tag):
    data = {}
    for m in SDM.values():
        for sub in ("", "b_"):
            for kind in ("scores", "pref"):
                f = FS / f"{sub}{m}" / f"{kind}_{tag}.jsonl"
                if f.exists():
                    for line in open(f):
                        r = json.loads(line); data.setdefault(r["index"], {}).setdefault(m, {}).update(r)
    return data
def loaddb():
    data = {}
    for m in SDM.values():
        for line in open(f"{DB}{m}/scores/wm_post-training_dbench_scores.jsonl"):
            r = json.loads(line); r["file"] = f"{DB}{m}/images/{r['index']:06d}.png"; r["seed"] = 42 + r["index"]; data.setdefault(r["index"], {})[m] = r
    return data
RULE = {"ocr": "OCR reward of the OCR teacher and of the student >= 0.999 on this sample",
        "geneval": "GenEval accuracy of the GenEval teacher and of the student = 1 on this sample",
        "pickscore": "PickScore: teacher >= base + 1.0, student >= teacher - 0.3 and student >= both models trained on the three rewards"}
for task, tag, key in (("ocr", "t0", "ocr"), ("pickscore", "db", "pickscore"), ("geneval", "t2", "accuracy")):
    data = loaddb() if tag == "db" else load(tag); rows = []
    for i in SD[task]:
        r = data[i]; sc = {m: r[SDM[m]][key] for m in SDM}
        prompts = {r[SDM[m]]["prompt"] for m in SDM}; seeds = {r[SDM[m]].get("seed", 42 + i) for m in SDM}
        assert len(prompts) == 1 and len(seeds) == 1, (task, i)
        if task == "ocr": assert sc["ocr"] >= .999 and sc["opd"] >= .999, (i, sc)
        elif task == "geneval": assert sc["geneval"] == 1 and sc["opd"] == 1, (i, sc)
        else: assert sc["pick"] >= sc["base"] + 1 and sc["opd"] >= sc["pick"] - .3 and sc["opd"] >= max(sc["grpo"], sc["nft"]), (i, sc)
        sid = f"{task}_{i:06d}"
        for m in SDM:
            im = put(r[SDM[m]]["file"], "sd35", f"{sid}_{m}")
            if m == "opd": thumb(im, "sd35", sid)
        rows.append({"id": sid, "prompt": prompts.pop(), "seed": seeds.pop(), "cols": list(SDM)})
        prov["sd35"].append({"id": sid, "task": task, "set": {"t0": "OCR test set", "t2": "GenEval test set", "db": "DrawBench"}[tag], "index": i,
                             "seed": rows[-1]["seed"], "prompt": rows[-1]["prompt"], "score_name": {"ocr": "OCR reward", "accuracy": "GenEval accuracy", "pickscore": "PickScore"}[key],
                             "scores": {m: round(float(sc[m]), 3) for m in SDM}, "sources": {m: r[SDM[m]]["file"] for m in SDM}})
    gallery["sd35"][task] = rows

wall = []
for bb, task, key in WALL:
    sid = key if bb == "flux" else f"{task}_{key:06d}"
    i = [r["id"] for r in gallery[bb][task]].index(sid); wall.append({"bb": bb, "task": task, "i": i})
(R / "samples.js").write_text("// Generated by tools/build_gallery.py; do not edit by hand.\nwindow.GALLERY = " +
                              json.dumps({"flux": gallery["flux"], "sd35": gallery["sd35"], "wall": wall}, ensure_ascii=False, indent=1) + ";\n")
STATIC = {
 "paper": "FlowMap-OPD: On-Policy Distillation for Few-Step Flow-Map Generators, arXiv:2609.37851 (preprint source: Flowmap_OPD_arxiv/main.tex)",
 "text_and_numbers": {
  "abstract, method paragraphs, captions": "main.tex (abstract, Sections 1, 3, 4, 5) and appendices/{baselines,imagenet,diagnostics}.tex",
  "stat tiles": "abstract and contributions list of main.tex (3 specialists, 300 updates, OCR 0.883 vs 0.850 on FLUX, ImageNet FID 22.68 to 18.23)",
  "FLUX.1 table": "Table tab:three-teacher, task-score columns",
  "SD3.5 table": "Table tab:three-teacher-sd, task-score columns",
  "ImageNet table": "sections/imagenet_selected_table.tex (Table tab:imagenet)",
  "rollout table": "Table tab:rollout", "multi-step table": "Table tab:multistep-teachers", "supervision table": "Table tab:interfaces"},
 "figures": [
  {"asset": "assets/teaser.webp", "source": "Flowmap_OPD_arxiv/figures/flowmap_opd_teaser_v2.jpg", "paper_figure": "fig:teaser", "edit": "re-encoded as WebP"},
  {"asset": "assets/og.jpg", "source": "Flowmap_OPD_arxiv/figures/flowmap_opd_teaser_v2.jpg", "edit": "resized to 1200 px wide for link previews"},
  *[{"asset": f"assets/separation_overview_{i}.webp", "source": f"Flowmap_OPD_arxiv/figures/separation_overview_{i}.pdf", "paper_figure": "fig:separation", "edit": "rasterized at 1400 px wide (PyMuPDF)"} for i in (1, 2, 3)]],
 "charts": {"generator": "tools/make_charts.py (light and dark SVG per chart; same data and encodings as the paper's plotting scripts in Flowmap_OPD/figures/plot_src)",
  "assets/fig/consolidation_gain_*.svg": "consolidation_gain.py, fig:consolidation-gain; values of the two three-teacher tables and the FLUX student's EMA evaluations",
  "assets/fig/mechanism_curves_*.svg": "mechanism_curves.py, fig:mechanism",
  "assets/fig/two_teacher_grpo_*.svg": "two_teacher_grpo.py, fig:two-teacher-grpo; data resolved once from /mnt/data/zhiqili/wm_post-training/setup/plot_data into tools/data/two_teacher_grpo.json",
  "assets/fig/imagenet_three_rewards_*.svg": "imagenet_three_rewards.py (first figure), fig:imagenet-design-selection; tools/data/imagenet_three_rewards.json",
  "assets/fig/consistency_monitor_*.svg": "consistency_monitor.py, fig:consistency-monitor"}}
GAL = {"generator": "tools/build_gallery.py",
       "selection": "Selected examples. FLUX.1: chosen by eye among the 66 paired samples. SD3.5: chosen by eye among the samples that pass the recorded-score rule of their task.",
       "processing": "each tile is the full 512x512 output re-encoded as WebP (quality 84); thumbnails are 120 px copies of the student image; no crop, no retouching",
       "models": {"flux": {"base": "FLUX.1-lite-8B MeanFlow base", "ocr/pick/geneval": "FlowMap-GRPO specialists", "grpo": "FlowMap-GRPO on three rewards, EMA update 1500 (tr3_pfs_fx)",
                           "nft": "MeanFlowNFT on three rewards, EMA update 750 (tr3_mfn_fx)", "opd": "FlowMap-OPD student, EMA update 300; lambda_c per example in student_checkpoint"},
                  "sd35": SDM},
       "sd35_rules": RULE, "wall": "student tiles reuse the gallery images listed below", **prov}
json.dump({**STATIC, "gallery": GAL}, open(R / "asset-provenance.json", "w"), ensure_ascii=False, indent=1)
n = sum(1 for _ in G.rglob("*.webp")); size = sum(f.stat().st_size for f in G.rglob("*.webp"))
print({bb: {t: len(v) for t, v in g.items()} for bb, g in gallery.items()}, n, "files", round(size / 1e6, 1), "MB")
