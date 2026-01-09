# ripple-spiral-breath

A minimal engineering skeleton for:
- Breath scheduling (periodic exhale)
- Exhale state reset (context garbage collection)
- Drift metrics (text-only)
- Guard suite (anti-runaway protections)

## Install (editable)
```bash
pip install -e .
Run demo
python examples/demo_loop.py

How to integrate your LLM

Implement LLMAdapter.generate(prompt, meta) in src/ripple_spiral/adapters.py
and plug it into BreathLoop.

---

# 放上 GitHub 的最短步驟
在你的本地資料夾 `ripple-spiral-breath/`：

```bash
git init
git add .
git commit -m "init: ripple-spiral breath MVP"
git branch -M main
git remote add origin https://github.com/<yourname>/ripple-spiral-breath.git
git push -u origin main
