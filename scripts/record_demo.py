"""Generate demo assets for the IntentFlow interactive analytics view.

Builds a generic example case (a subscription app, clearly labelled as demo
data), renders the interactive analytics dashboard, and produces two assets
under docs/demo/:
  - demo.webm : a screen recording of the full interaction
  - demo.gif  : a smaller GIF (key frames) for inline README display

The temporary case is discarded; only the assets are kept.
"""

from __future__ import annotations

import io
import shutil
import tempfile
from pathlib import Path

from intentflow_runtime.analytics_report import build_analytics_html

REPORT = """# 订阅管理 App 数据复盘报告

## 1. 复盘问题与产品决策

### 复盘问题

订阅流程的转化与续费是否足以支撑下一步的定价页改版？

### 本报告支持的决策

决定是否优先投入定价页改版，还是先补事件质量。以下数字均为演示数据，用于验证复盘视图的格式与交互。

## 2. 数据契约

| 项目 | 本轮记录 |
| --- | --- |
| 提取日期 | 2026-10-11（Asia/Shanghai） |
| 观察窗口 | 2026-09-01 ~ 2026-09-30 |
| 分析单位 | 会话 / 用户 |
| 主要来源 | events.csv（演示） |
| 来源版本 | v1.2 |
| 样本量 | 12,480 会话；3,204 用户 |
| 缺失字段 | 无 |
| 排除项 | 内部测试账号 |

## 3. 指标与可计算性

| 指标 | 目标口径 | 本轮结果 | 原因 |
| --- | --- | --- | --- |
| 订阅转化完成率 | 完成订阅 / 进入订阅流程 | 24.3% | 可复算 |
| 7 日续费率 | 7 日内续费 / 首次订阅 | 58.1% | 可复算 |
| 退款率 | 退款 / 订阅 | 4.6% | 可复算 |

## 4. 已观察事实

1. 订阅转化完成率为 24.3%，进入订阅流程后有明显的流失。
2. 7 日续费率为 58.1%，高于行业常见区间。
3. 退款率 4.6%，主要集中在新用户首月。

## 5. 观察、推断与反例

### 观察

- 定价页到支付成功之间流失最集中。
- 续费用户多来自年度套餐。

### 推断（待验证）

- 定价页的信息密度过高可能是流失主因，需用 A/B 测试验证。

### 其他解释

- 流失也可能是支付方式不全或移动端加载慢导致。

## 6. 可执行选项（均为助手建议）

1. **优化定价页**：简化信息层级，突出年度套餐，先跑小流量 A/B。
2. **补支付方式**：新增常用支付渠道，观察完成率变化。
3. **建立事件质量校验**：先确认漏斗各阶段去重与顺序无误，再下结论。

## 7. 最小下一步验证

对定价页做一次小流量 A/B，只观察订阅转化完成率与退款率两个指标。

## 8. 局限与复盘结论

- 本报告为演示数据，不代表真实产品结果。

**结论：**优先做定价页小流量 A/B，同时补齐事件质量校验。
"""

METRICS = """# 指标定义

| 指标 | 单位 | 分子 | 分母 | 资格条件 | 时间窗/时区 | 去重键 | 当前基线 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 订阅转化完成率 | 会话 | 完成订阅的会话数 | 进入订阅流程的会话数 | 进入订阅流程 | 30 天；Asia/Shanghai | session_id | 24.3% |
| 7 日续费率 | 用户 | 7 日内续费的用户数 | 首次订阅的用户数 | 有首订记录 | 7 天；Asia/Shanghai | user_id | 58.1% |
| 退款率 | 订阅 | 发生退款的订阅数 | 完成订阅的总数 | 订阅已生效 | 30 天；Asia/Shanghai | subscription_id | 4.6% |

## 口径约束

- 会话级与用户级指标分开统计，不混用分母。
- 退款按订阅去重，同一订阅多次退款只计一次。
- 以上数字为演示数据，仅用于验证视图格式。
"""


def _capture_key_frames(page, frames: list[bytes]) -> None:
    """Scroll through panels and exercise interactions, capturing key frames."""
    page.wait_for_timeout(800)
    frames.append(page.screenshot())

    page.locator("#panel-2").scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())
    page.locator('[data-funnel-base="previous"]').click()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())
    page.locator('[data-funnel-base="first"]').click()
    page.wait_for_timeout(400)

    page.locator("#panel-3").scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    frames.append(page.screenshot())

    page.locator("#panel-4").scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    frames.append(page.screenshot())

    page.locator("#panel-5").scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())
    page.locator('.attribution-block[data-kind="hypothesis"] summary').click()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())

    page.locator("#panel-6").scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())
    page.locator('input[data-action]').first.click()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())

    page.locator("#panel-7").scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())
    page.locator('[data-quality="no"]').click()
    page.wait_for_timeout(600)
    frames.append(page.screenshot())


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    demo_dir = root / "docs" / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        analytics = tmp / "demo" / "analytics"
        analytics.mkdir(parents=True)
        report = analytics / "report.md"
        metrics = analytics / "metric-definitions.md"
        report.write_text(REPORT, encoding="utf-8")
        metrics.write_text(METRICS, encoding="utf-8")
        html = analytics / "report-review.html"
        build_analytics_html(report, metrics, html)

        from playwright.sync_api import sync_playwright

        video_dir = tmp / "video"
        video_dir.mkdir()
        frames: list[bytes] = []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                record_video_dir=str(video_dir),
                record_video_size={"width": 1440, "height": 900},
            )
            page = context.new_page()
            page.goto(html.as_uri(), wait_until="networkidle")
            _capture_key_frames(page, frames)
            page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            page.wait_for_timeout(1200)
            context.close()
            browser.close()

        videos = list(video_dir.glob("*.webm"))
        if videos:
            shutil.copy(videos[0], demo_dir / "demo.webm")

        _write_gif(frames, demo_dir / "demo.gif")

    print(f"webm: {(demo_dir / 'demo.webm').stat().st_size if (demo_dir / 'demo.webm').exists() else 0} bytes")
    print(f"gif:  {(demo_dir / 'demo.gif').stat().st_size} bytes")


def _write_gif(frames: list[bytes], target: Path) -> None:
    from PIL import Image

    images = []
    for raw in frames:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        image.thumbnail((800, 800))
        images.append(image)
    durations = [900] * len(images)
    if durations:
        durations[-1] = 1400
    images[0].save(
        target,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )


if __name__ == "__main__":
    main()
