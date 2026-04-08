#!/usr/bin/env python3
import html as h
import re
from pathlib import Path

md = Path("production/storyboard/ep01.md").read_text()
lines = md.split("\n")

out = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>你被解雇了 — EXP-1058</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#e0e0e0;font-family:'PingFang SC','Noto Sans SC',sans-serif;line-height:1.8;padding:20px;max-width:500px;margin:0 auto}
h1{color:#f0c040;text-align:center;font-size:28px;margin:30px 0 10px;text-shadow:0 0 20px rgba(240,192,64,0.3)}
.sub{text-align:center;color:#888;font-size:14px;margin-bottom:30px}
h2{color:#60a0ff;font-size:18px;margin:20px 0 8px;border-left:3px solid #60a0ff;padding-left:10px}
.chr{background:#151520;border-radius:10px;padding:14px;margin:8px 0;border-left:3px solid #f0c040}
.chr b{color:#f0c040}
.scn{background:#101025;border-radius:10px;padding:14px;margin:8px 0;border-left:3px solid #40d0a0}
.scn b{color:#40d0a0}
.seg{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:16px;margin:25px 0 15px;border:1px solid #30305a}
.seg h2{border:none;color:#fff;font-size:20px;margin:0}
.seg .m{color:#888;font-size:13px;margin-top:6px}
.prt{background:#12121e;border-radius:10px;padding:16px;margin:12px 0;border-left:3px solid #8060ff}
.prt-l{color:#8060ff;font-weight:bold;font-size:14px;margin-bottom:6px}
.dl{margin:8px 0;padding:10px 14px;border-radius:8px;background:#1a1a30}
.dl-n{border-left:3px solid #60a0ff}
.dl-i{border-left:3px solid #f0a040;font-style:italic}
.dl-s{border-left:3px solid #f04040;font-family:monospace}
.dl b{margin-right:6px}
.dir{color:#999;font-size:14px;margin:4px 0}
.ps{background:#0e0e1a;border-radius:8px;padding:12px;margin:10px 0;border:1px dashed #30305a;font-size:13px;color:#aaa}
.cam{color:#e08040;font-size:13px;margin-top:6px;font-style:italic}
</style>
</head>
<body>
<h1>\U0001f3ac 你被解雇了</h1>
<div class="sub">EXP-1058 | 15秒短剧分镜 | S-Format v7.5</div>
"""

section = ""
in_physical = False
in_part = False

for line in lines:
    line = line.rstrip()
    if not line:
        continue

    if line.startswith("# PART 1"):
        section = "assets"
        continue
    elif line.startswith("# PART 2"):
        section = "storyboard"
        continue
    elif line.startswith("## Characters"):
        out += "<h2>\U0001f3ad 角色</h2>\n"
        continue
    elif line.startswith("## Scenes"):
        out += "<h2>\U0001f3d9\ufe0f 场景</h2>\n"
        continue

    if line.startswith("- [") and section == "assets":
        m = re.match(r"- \[(.+?)\]: (.+)", line)
        if m:
            name, desc = h.escape(m.group(1)), h.escape(m.group(2))
            cls = "scn" if any(k in m.group(2) for k in ["办公","走廊","会议"]) else "chr"
            out += f'<div class="{cls}"><b>[{name}]</b> {desc}</div>\n'
        continue

    if line.startswith("## Segment"):
        m = re.match(r"## (Segment \d+) \| (\d+s)", line)
        if m:
            out += f'<div class="seg"><h2>\U0001f3ac {m.group(1)}</h2><div class="m">\u23f1\ufe0f {m.group(2)}</div></div>\n'
        continue

    if line.startswith("**Location**") or line.startswith("**Cast**") or line.startswith("**图片引用**"):
        out += f'<div class="dir">{h.escape(line.replace("**",""))}</div>\n'
        continue

    if line.startswith("**Physical State:**"):
        if in_part:
            out += "</div>\n"
            in_part = False
        out += '<div class="ps"><b>Physical State:</b><br>\n'
        in_physical = True
        continue

    if line.startswith("- [") and section == "storyboard":
        out += f"{h.escape(line)}<br>\n"
        continue

    if line.startswith("[Part"):
        m = re.match(r"\[Part (\d+)\] (.+)", line)
        if m:
            if in_physical:
                out += "</div>\n"
                in_physical = False
            if in_part:
                out += "</div>\n"
            out += f'<div class="prt"><div class="prt-l">Part {m.group(1)}</div><p>{h.escape(m.group(2))}</p>\n'
            in_part = True
        continue

    if line.startswith("[") and "]:" in line:
        m = re.match(r"\[(.+?)\]\s*(\(.+?\))?\s*:\s*(.+)", line)
        if not m:
            m = re.match(r"\[(.+?)\](.*?):\s*(.+)", line)
        if m:
            char_name = h.escape(m.group(1))
            note = h.escape((m.group(2) or "").strip().strip("()"))
            text = h.escape(m.group(3).strip().strip('""\u201c\u201d'))
            if "内心" in note:
                cls = "dl dl-i"
            elif "系统" in m.group(1) or "电子" in note:
                cls = "dl dl-s"
            else:
                cls = "dl dl-n"
            out += f'<div class="{cls}"><b>[{char_name}]</b>'
            if note:
                out += f' <span style="color:#888;font-size:12px">({note})</span>'
            out += f"<br>{text}</div>\n"
        continue

    if line.startswith("运镜"):
        out += f'<div class="cam">\U0001f3a5 {h.escape(line)}</div>\n'
        continue

if in_part:
    out += "</div>\n"
if in_physical:
    out += "</div>\n"

out += "</body></html>"
Path("index.html").write_text(out)
print("HTML rendered OK")
