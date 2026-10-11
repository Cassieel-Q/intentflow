# Scripts

Small repository-maintenance scripts live here.

## IntentFlow local review tools

Formal PRD, acceptance checklist and analytics report files remain Markdown. The
review HTML is generated on demand and can be discarded. Python 3.11+ and
`markdown-it-py` are required for rendering. Browser screenshots additionally
need `playwright` and an available Chromium/Edge browser.

需求挖掘的正式记录是 `research/demand-brief.md`、
`research/demand-findings.md` 和根目录 `source.md`。反馈逐条记录放在
`research/feedback.csv`，公开产品机制放在可追溯的 `research/products.csv`。
没有真实反馈时，可用 `research/demo-feedback.csv` 测试案例整理和洞察页，
但页面会明确标注为模拟演示数据；HTML 只在需要评审或演示时生成。

```powershell
py -3 -m pip install -r scripts/requirements-review.txt
py -3 scripts/intentflow.py doctor --requirement requirements/<name>
py -3 scripts/intentflow.py render --requirement requirements/<name> --kind prd
py -3 scripts/intentflow.py validate --requirement requirements/<name> --kind prd
py -3 scripts/intentflow.py analyze-funnel --requirement requirements/<name> --csv analytics/events.csv --key person_id --stage stage --stages 进入,完成 --window "2026-10-01 to 2026-10-07 Asia/Shanghai"
py -3 scripts/intentflow.py demand-report --requirement requirements/<name> --csv research/demo-feedback.csv --findings research/demand-findings.md --products research/products.csv
py -3 scripts/intentflow.py demand-gate --requirement requirements/<name>
py -3 scripts/intentflow.py serve --requirement requirements/<name> --kind prd
py -3 scripts/intentflow.py capture --requirement requirements/<name> --html design/prototype.html --page default
```

Use `scripts/intentflow-start.bat` on Windows and
`scripts/intentflow-start.command` on macOS with the same arguments. `init`
creates only missing requirement records; existing files are preserved. `serve`
binds to `127.0.0.1` and chooses a free port by default. Editing in a served
review page writes only the corresponding formal Markdown with revision checks;
an offline page downloads a modification draft. Acceptance execution results
are saved separately in `qa/results.md`.

## check-temporary-test-artifacts.sh

Run this before commit or delivery to find temporary TDD and probe markers:

```sh
./scripts/check-temporary-test-artifacts.sh .
```

If it finds `TEMP_TDD`, `SCRATCH_TEST`, `TEMP_TEST`, `临时测试`, or
`探针测试`, remove the temporary artifact or promote it to a retained test
and remove the temporary marker.
