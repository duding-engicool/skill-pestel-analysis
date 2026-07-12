#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PESTEL 报告生成脚本
读取结构化 JSON，生成 MD 文档 + 精美网页版 HTML（含内嵌响应式 CSS）。
输入 JSON 结构见 assets/PESTEL分析_输出大纲.md。
"""
import argparse
import json
import sys
import datetime

DIM_LABELS = {
    "P": "政治 Political",
    "E": "经济 Economic",
    "S": "社会 Social",
    "T": "技术 Technological",
    "Env": "环境 Environmental",
    "L": "法律 Legal",
}
DIM_COLORS = {
    "P": "#C0392B",
    "E": "#E67E22",
    "S": "#27AE60",
    "T": "#2980B9",
    "Env": "#16A085",
    "L": "#8E44AD",
}


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_md(d):
    obj = d.get("object", "（未提供）")
    scope = d.get("scope", "（未提供）")
    strategy = d.get("strategy_text", "").strip()
    strat_note = "（用户未提供战略，以下相关性标注为「待提供战略后复核」）" if not strategy else ""
    dims = d.get("dimensions", {})
    trends = d.get("trends", [])
    impacts = d.get("impacts", [])
    opp = d.get("opportunities", [])
    thr = d.get("threats", [])
    mon = d.get("monitoring", [])

    lines = []
    lines.append(f"# PESTEL 宏观环境分析报告\n")
    lines.append(f"- **分析对象**：{esc(obj)}")
    lines.append(f"- **范围**：{esc(scope)}")
    if strategy:
        lines.append(f"- **关联战略**：{esc(strategy)}")
    else:
        lines.append(f"- **关联战略**：未提供 {strat_note}")
    lines.append(f"- **生成时间**：{datetime.date.today().isoformat()}\n")

    lines.append("## 一、六维度环境要素\n")
    for key in ["P", "E", "S", "T", "Env", "L"]:
        items = dims.get(key, [])
        lines.append(f"### {DIM_LABELS[key]}\n")
        if not items:
            lines.append("_（未提供，标注「供参考·待确认」）_\n")
            continue
        for it in items:
            if isinstance(it, dict):
                txt = it.get("text", "")
                note = it.get("note", "")
                suffix = f"  _{esc(note)}_" if note else ""
                lines.append(f"- {esc(txt)}{suffix}")
            else:
                lines.append(f"- {esc(it)}")
        lines.append("")

    if trends:
        lines.append("## 二、关键趋势汇总\n")
        for t in trends:
            lines.append(f"- **[{esc(t.get('dim',''))}]** {esc(t.get('text',''))}（依据：{esc(t.get('basis',''))}）")
        lines.append("")

    if impacts:
        lines.append("## 三、影响评估（提示性）\n")
        lines.append("> 影响强度为提示性，最终判定请结合贵方实际确认。\n")
        for im in impacts:
            lines.append(f"- {esc(im.get('text',''))}：方向 {esc(im.get('direction',''))} / 强度 {esc(im.get('level',''))} {('（'+esc(im.get('note',''))+'）') if im.get('note') else ''}")
        lines.append("")

    if opp or thr:
        lines.append("## 四、机会 / 威胁初步映射（建议性，请用户确认）\n")
        lines.append("**机会（O）：**")
        for o in opp:
            lines.append(f"- {esc(o)}")
        lines.append("\n**威胁（T）：**")
        for t in thr:
            lines.append(f"- {esc(t)}")
        lines.append("")

    if mon:
        lines.append("## 五、关键监测点\n")
        for m in mon:
            lines.append(f"- {esc(m)}")
        lines.append("")

    return "\n".join(lines)


def build_html(d):
    obj = esc(d.get("object", "（未提供）"))
    scope = esc(d.get("scope", "（未提供）"))
    strategy = d.get("strategy_text", "").strip()
    strat_line = esc(strategy) if strategy else "未提供（相关性标注为「待提供战略后复核」）"
    dims = d.get("dimensions", {})
    trends = d.get("trends", [])
    impacts = d.get("impacts", [])
    opp = d.get("opportunities", [])
    thr = d.get("threats", [])
    mon = d.get("monitoring", [])

    dim_cards = ""
    for key in ["P", "E", "S", "T", "Env", "L"]:
        color = DIM_COLORS[key]
        items = dims.get(key, [])
        lis = ""
        if not items:
            lis = '<li class="placeholder">未提供 · 供参考·待确认</li>'
        else:
            for it in items:
                if isinstance(it, dict):
                    txt = esc(it.get("text", ""))
                    note = it.get("note", "")
                    tag = f'<span class="note">{esc(note)}</span>' if note else ''
                    lis += f"<li>{txt}{tag}</li>"
                else:
                    lis += f"<li>{esc(it)}</li>"
        dim_cards += f'''
        <div class="qcard" style="border-top:4px solid {color}">
          <div class="qhead" style="color:{color}">{key} · {esc(DIM_LABELS[key].split(' ')[0])}</div>
          <div class="qsub">{esc(DIM_LABELS[key].split(' ',1)[1] if ' ' in DIM_LABELS[key] else '')}</div>
          <ul>{lis}</ul>
        </div>'''

    trend_html = "".join(
        f'<li><b>[{esc(t.get("dim",""))}]</b> {esc(t.get("text",""))} <span class="note">依据：{esc(t.get("basis",""))}</span></li>'
        for t in trends
    ) or '<li class="placeholder">未提供</li>'

    impact_html = "".join(
        f'<li>{esc(im.get("text",""))} — 方向 <b>{esc(im.get("direction",""))}</b> / 强度 <b>{esc(im.get("level",""))}</b> {("<span class=\"note\">"+esc(im.get("note",""))+"</span>") if im.get("note") else ""}</li>'
        for im in impacts
    ) or '<li class="placeholder">未提供</li>'

    opp_html = "".join(f"<li>{esc(o)}</li>" for o in opp) or '<li class="placeholder">未提供</li>'
    thr_html = "".join(f"<li>{esc(t)}</li>" for t in thr) or '<li class="placeholder">未提供</li>'
    mon_html = "".join(f"<li>{esc(m)}</li>" for m in mon) or '<li class="placeholder">未提供</li>'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PESTEL 宏观环境分析报告</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; margin:0; background:#f4f6f9; color:#1f2933; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 60px; }}
  header {{ background: linear-gradient(135deg,#2c3e50,#4b6584); color:#fff; padding:28px 32px; border-radius:14px; }}
  header h1 {{ margin:0 0 8px; font-size:26px; }}
  header .meta {{ font-size:14px; opacity:.9; line-height:1.7; }}
  .grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin:28px 0; }}
  .qcard {{ background:#fff; border-radius:12px; padding:16px 18px; box-shadow:0 2px 10px rgba(0,0,0,.06); }}
  .qhead {{ font-size:18px; font-weight:700; }}
  .qsub {{ font-size:12px; color:#7b8794; margin-bottom:10px; }}
  .qcard ul {{ margin:0; padding-left:18px; font-size:14px; line-height:1.7; }}
  .note {{ color:#c0392b; font-size:12px; margin-left:4px; }}
  section {{ background:#fff; border-radius:12px; padding:20px 24px; margin:18px 0; box-shadow:0 2px 10px rgba(0,0,0,.06); }}
  section h2 {{ font-size:19px; border-left:5px solid #4b6584; padding-left:10px; margin-top:0; }}
  ul.flist {{ line-height:1.9; font-size:14px; }}
  .placeholder {{ color:#b0b8c1; font-style:italic; }}
  .twocol {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  footer {{ text-align:center; color:#9aa5b1; font-size:12px; margin-top:30px; }}
  @media (max-width:780px) {{ .grid,.twocol {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>PESTEL 宏观环境分析报告</h1>
    <div class="meta">
      分析对象：{obj}<br>
      范围：{scope}<br>
      关联战略：{strat_line}<br>
      生成时间：{datetime.date.today().isoformat()}
    </div>
  </header>

  <div class="grid">{dim_cards}</div>

  <section>
    <h2>关键趋势汇总</h2>
    <ul class="flist">{trend_html}</ul>
  </section>

  <section>
    <h2>影响评估（提示性）</h2>
    <ul class="flist">{impact_html}</ul>
  </section>

  <div class="twocol">
    <section>
      <h2>机会（O）</h2>
      <ul class="flist">{opp_html}</ul>
    </section>
    <section>
      <h2>威胁（T）</h2>
      <ul class="flist">{thr_html}</ul>
    </section>
  </div>

  <section>
    <h2>关键监测点</h2>
    <ul class="flist">{mon_html}</ul>
  </section>

  <footer>本报告由 PESTEL宏观环境分析技能生成 · 内容由用户交互提供，Agent 不替用户撰写结论</footer>
</div>
</body>
</html>'''
    return html


def main():
    parser = argparse.ArgumentParser(description="PESTEL 报告生成（MD + HTML）")
    parser.add_argument("--input", required=True, help="结构化 JSON 路径")
    parser.add_argument("--md-out", help="MD 输出路径")
    parser.add_argument("--html-out", help="HTML 输出路径")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"读取输入失败: {e}"}, ensure_ascii=False))
        sys.exit(1)

    md = build_md(data)
    html = build_html(data)

    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(md)
    if args.html_out:
        with open(args.html_out, "w", encoding="utf-8") as f:
            f.write(html)

    print(json.dumps({
        "status": "ok",
        "md_out": args.md_out,
        "html_out": args.html_out,
        "dimensions": {k: len(data.get("dimensions", {}).get(k, [])) for k in ["P", "E", "S", "T", "Env", "L"]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
