#!/usr/bin/env python3
"""IntentFlow local review, capture and diagnosis command line."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

from intentflow_runtime.capture import capture
from intentflow_runtime.core import InvalidTarget, resolve_requirement_path
from intentflow_runtime.doctor import diagnose
from intentflow_runtime.analytics import read_csv_rows, summarize_funnel
from intentflow_runtime.analytics_report import build_analytics_html
from intentflow_runtime.demand_report import build_insight_html
from intentflow_runtime.demand_gate import evaluate_demand_gate, write_gate_report
from intentflow_runtime.render import render_review
from intentflow_runtime.server import make_server
from intentflow_runtime.validate import validate_prd


SOURCES = {"prd": "prd/PRD.md", "acceptance": "qa/checklist.md", "analytics": "analytics/report.md"}
OUTPUTS = {"prd": "prd/PRD-review.html", "acceptance": "qa/checklist-review.html", "analytics": "analytics/report-review.html"}


def requirement_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--requirement", required=True, type=Path, help="active requirement directory")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="IntentFlow local tools")
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create missing requirement records without replacing files")
    requirement_arg(init)
    render = commands.add_parser("render", help="generate a review HTML from formal Markdown")
    requirement_arg(render)
    render.add_argument("--kind", choices=SOURCES, required=True)
    render.add_argument("--source", help="override only with this kind's formal Markdown path")
    render.add_argument("--prototype", help="optional prototype HTML inside the requirement")
    serve = commands.add_parser("serve", help="serve a guarded local review page")
    requirement_arg(serve)
    serve.add_argument("--kind", choices=SOURCES, required=True)
    serve.add_argument("--prototype")
    serve.add_argument("--port", type=int, default=0)
    serve.add_argument("--no-open", action="store_true")
    screenshot = commands.add_parser("capture", help="capture a rendered HTML prototype")
    requirement_arg(screenshot)
    screenshot.add_argument("--html", required=True, help="HTML path relative to requirement")
    screenshot.add_argument("--output", default="design/screenshots", help="output directory relative to requirement")
    screenshot.add_argument("--page", action="append", default=[], help="page ID or hash; repeat for multiple pages")
    screenshot.add_argument("--width", type=int, default=1440)
    screenshot.add_argument("--height", type=int, default=900)
    doctor = commands.add_parser("doctor", help="report runtime requirements")
    requirement_arg(doctor)
    doctor.add_argument("--json", action="store_true")
    validate = commands.add_parser("validate", help="check formal document structure")
    requirement_arg(validate)
    validate.add_argument("--kind", choices=["prd"], required=True)
    analyze = commands.add_parser("analyze-funnel", help="calculate a reproducible person funnel from CSV")
    requirement_arg(analyze)
    analyze.add_argument("--csv", required=True, help="CSV path relative to requirement")
    analyze.add_argument("--key", required=True, help="person identity column")
    analyze.add_argument("--stage", required=True, help="stage column")
    analyze.add_argument("--stages", required=True, help="ordered stages separated by comma")
    analyze.add_argument("--window", required=True, help="observation window and timezone")
    analyze.add_argument("--output", default="analytics/report.md")
    demand = commands.add_parser("demand-report", help="generate an optional demand-insight HTML view")
    requirement_arg(demand)
    demand.add_argument("--csv", default="research/demo-feedback.csv")
    demand.add_argument("--findings", default="research/demand-findings.md")
    demand.add_argument("--products", default="research/products.csv", help="optional public product reference CSV")
    demand.add_argument("--output", default="research/demand-insight.html")
    gate = commands.add_parser("demand-gate", help="check whether demand discovery can enter PRD work")
    requirement_arg(gate)
    gate.add_argument("--feedback", default="research/feedback.csv")
    gate.add_argument("--findings", default="research/demand-findings.md")
    gate.add_argument("--source", default="source.md")
    gate.add_argument("--products", default="research/products.csv")
    gate.add_argument("--output", default="research/demand-gate.md")
    return root


def initialize(requirement: Path) -> list[Path]:
    requirement.mkdir(parents=True, exist_ok=True)
    files = {
        "README.md": "# 需求目录\n\n- 需求目标：待补充\n- 当前阶段：需求挖掘\n- 正式产物：见本目录各 Markdown 文件\n",
        "source.md": "# 材料与来源\n\n| ID | 材料 | 来源位置 | 获取日期 | 适用范围 |\n| --- | --- | --- | --- | --- |\n",
        "requirement.md": "# 需求简述\n\n- 目标用户：待确认\n- 场景：待确认\n- 问题：待确认\n- 期望结果：待确认\n- 当前范围：待确认\n",
        "todo.md": "# 当前待办\n\n- [ ] 明确影响下一份产出的关键未决问题\n- [终审适用性确认] 最终验收前由主会话主动评估并向用户建议完整终审、轻量终审或不做专项终审；具体是否执行及深度由用户决定。\n",
        "decisions.md": "# 已确认决策\n\n| 日期 | 决策 | 依据 | 影响 |\n| --- | --- | --- | --- |\n",
        "open-questions.md": "# 待确认问题\n\n| ID | 问题 | 影响 | 当前处理 |\n| --- | --- | --- | --- |\n",
        "acceptance.md": "# 需求完成标准\n\n- [ ] 目标用户、场景和问题已确认\n- [ ] 证据与推断可追溯\n- [ ] 范围与下一步已记录\n",
        "links.md": "# 产物与外部链接\n\n| 名称 | 路径或链接 | 版本/日期 |\n| --- | --- | --- |\n",
    }
    created = []
    for relative, content in files.items():
        path = requirement / relative
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            created.append(path)
        except FileExistsError:
            pass
    return created


def run(args: argparse.Namespace) -> None:
    req = args.requirement.resolve(strict=False)
    if args.command == "init":
        created = initialize(req)
        print(json.dumps({"created": [str(path) for path in created], "preserved_existing": True}, ensure_ascii=False))
        return
    req = req.resolve(strict=True)
    if not req.is_dir():
        raise ValueError("requirement must be a directory")
    if args.command == "doctor":
        result = diagnose(req)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Requirement: {result['requirement']}")
            for name, check in result["checks"].items():
                print(f"{name}: {'OK' if check['ok'] else 'MISSING'} — {check['detail']}")
        return
    if args.command == "validate":
        result = validate_prd(resolve_requirement_path(req, SOURCES[args.kind]))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["ok"]:
            raise SystemExit(1)
        return
    if args.command == "analyze-funnel":
        rows = read_csv_rows(resolve_requirement_path(req, args.csv))
        result = summarize_funnel(rows, args.key, args.stage, [item.strip() for item in args.stages.split(",")], args.window)
        target = resolve_requirement_path(req, args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result["markdown"], encoding="utf-8", newline="\n")
        print(target)
        return
    if args.command == "demand-report":
        output = build_insight_html(
            resolve_requirement_path(req, args.csv),
            resolve_requirement_path(req, args.findings),
            resolve_requirement_path(req, args.output),
            products_path=resolve_requirement_path(req, args.products),
        )
        print(output)
        return
    if args.command == "demand-gate":
        products = resolve_requirement_path(req, args.products)
        result = evaluate_demand_gate(
            req,
            resolve_requirement_path(req, args.feedback),
            resolve_requirement_path(req, args.findings),
            resolve_requirement_path(req, args.source),
            products,
        )
        output = write_gate_report(result, resolve_requirement_path(req, args.output))
        print(json.dumps({"status": result["status"], "ready_for_prd": result["ready_for_prd"], "report": str(output)}, ensure_ascii=False))
        if result["status"] == "blocked":
            raise SystemExit(2)
        return
    if args.command in {"render", "serve"}:
        relative = getattr(args, "source", None) or SOURCES[args.kind]
        if relative != SOURCES[args.kind]:
            raise InvalidTarget("source must match the formal Markdown path for this kind")
        source = resolve_requirement_path(req, relative)
        if not source.is_file():
            raise FileNotFoundError(source)
        prototype = resolve_requirement_path(req, args.prototype) if args.prototype else None
        if prototype is not None and (not prototype.is_file() or prototype.suffix.lower() != ".html"):
            raise InvalidTarget("prototype must be an existing HTML file")
        if args.command == "render":
            target = resolve_requirement_path(req, OUTPUTS[args.kind])
            target.parent.mkdir(parents=True, exist_ok=True)
            if args.kind == "analytics":
                metrics = resolve_requirement_path(req, "analytics/metric-definitions.md")
                if not metrics.is_file():
                    raise FileNotFoundError(metrics)
                build_analytics_html(source, metrics, target)
            else:
                target.write_text(render_review(source, args.kind, prototype), encoding="utf-8", newline="\n")
            print(target)
            return
        server = make_server(req, port=args.port)
        query = {"path": relative, "kind": args.kind}
        if args.prototype:
            query["prototype"] = args.prototype
        url = f"http://127.0.0.1:{server.server_port}/review?{urlencode(query)}"
        print(url, flush=True)
        if not args.no_open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return
    if args.command == "capture":
        html = resolve_requirement_path(req, args.html)
        output = resolve_requirement_path(req, args.output)
        for path in capture(html, output, args.page or ["default"], viewport=(args.width, args.height)):
            print(path)


if __name__ == "__main__":
    try:
        run(parser().parse_args())
    except (ValueError, FileNotFoundError, RuntimeError, OSError) as exc:
        print(f"IntentFlow: {exc}", file=sys.stderr)
        sys.exit(2)
