# FlowMap-OPD project page

Static research project page for FlowMap-OPD ([arXiv:2609.37851](https://arxiv.org/abs/2609.37851)). Code: [ZhiqiLi-CG/Flowmap_OPD_source](https://github.com/ZhiqiLi-CG/Flowmap_OPD_source).

GitHub Pages: deploy from the `main` branch, `/ (root)` directory. No build step required.

Preview locally: `python3 -m http.server 8000`.

Figures and results are drawn from the accompanying manuscript. Interactive examples are the manuscript’s paired qualitative comparisons (consistency coefficient 0); quantitative results use the separately reported coefficient 0.001 student.

## Interactive comparisons

25 paired examples (125 model images) from the manuscript and appendix. The base model, the three specialist teachers and the student are shown side by side; switch tasks and examples, or click an image to enlarge it. `asset-provenance.json` records the paper figure for each image, including the method overview (Figure 2) and the comparison with mixed-reward Flow-Map GRPO.
