from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshot.png"


def get_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/DENGB.TTF" if bold else "C:/Windows/Fonts/DENG.TTF",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


W, H = 1700, 900
image = Image.new("RGB", (W, H), "#f5f6f8")
draw = ImageDraw.Draw(image)

f12 = get_font(12)
f13 = get_font(13)
f14 = get_font(14)
f16b = get_font(16, True)
f18b = get_font(18, True)
f20b = get_font(20, True)
f24b = get_font(24, True)


def rect(x1, y1, x2, y2, fill, outline="#dfe3ea", radius=8):
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline)


def text(x, y, value, fill="#20242c", font=f14):
    draw.text((x, y), value, fill=fill, font=font)


def label(x, y, value):
    text(x, y, value, "#405066", f12)


def input_box(x, y, width, height, value, masked=False):
    rect(x, y, x + width, y + height, "#ffffff", "#c8d0dc", 6)
    text(x + 9, y + 9, "●" * 30 if masked else value, "#111827", f14)


def button(x, y, width, height, value, fill="#1f6feb", fg="#ffffff", font=f14):
    rect(x, y, x + width, y + height, fill, fill, 6)
    tw = draw.textlength(value, font=font)
    text(x + (width - tw) / 2, y + 8, value, fg, font)


rect(0, 0, W, 50, "#ffffff", "#dfe3ea", 0)
text(28, 14, "AIPerf GUI v0.12.0", "#111827", f20b)
label(1370, 18, "语言")
input_box(1410, 8, 130, 36, "中文")
button(1550, 8, 86, 36, "帮助", "#e8edf5", "#223044")

mx, y = 28, 66
mw = W - 56
rect(mx, y, mx + mw, y + 275, "#ffffff", "#dfe3ea", 8)
text(mx + 14, y + 14, "基准测试", "#111827", f18b)

x0, yy = mx + 14, y + 48
colw = int((mw - 42) / 2)
label(x0, yy, "Base URL")
input_box(x0, yy + 18, colw, 36, "https://apihub.agnes-ai.com/v1")
label(x0 + colw + 14, yy, "API Key")
input_box(x0 + colw + 14, yy + 18, colw, 36, "", masked=True)

yy += 74
label(x0, yy, "模型")
input_box(x0, yy + 18, 230, 36, "agnes-2.0-flash")
button(x0 + 238, yy + 18, 44, 36, "▼", "#edf1f6", "#9aa5b5", f16b)
button(x0 + 292, yy + 18, 112, 36, "获取模型", "#e8edf5", "#223044")
for name, value, dx, width in [
    ("端点", "chat", 420, 130),
    ("并发", "1,2,4,8", 560, 130),
    ("输入", "128", 700, 130),
    ("输出", "32", 840, 130),
    ("请求数", "1", 980, 130),
    ("预热", "1", 1120, 130),
    ("超时", "120", 1260, 130),
]:
    label(x0 + dx, yy, name)
    input_box(x0 + dx, yy + 18, width, 36, value)

yy += 72
label(x0, yy, "操作")
button(x0, yy + 18, 64, 36, "开始")
button(x0 + 76, yy + 18, 110, 36, "检查 AIPerf", "#44546a", "#ffffff")
label(x0 + 210, yy, "选项")
for value, dx, width in [("☑ 流式", 210, 75), ("☑ 固定输出", 294, 108), ("☐ 服务端指标", 412, 126)]:
    rect(x0 + dx, yy + 18, x0 + dx + width, yy + 54, "#ffffff", "#dfe3ea", 6)
    text(x0 + dx + 9, yy + 27, value, "#2f3b4c", f13)
label(x0 + 940, yy, "代理")
rect(x0 + 940, yy + 18, x0 + 1014, yy + 54, "#ffffff", "#dfe3ea", 6)
text(x0 + 950, yy + 27, "☐ 代理", "#2f3b4c", f13)
label(x0 + 1030, yy, "代理地址")
input_box(x0 + 1030, yy + 18, 260, 36, "http://192.168.1.1:8080")
label(x0 + 1300, yy, "不走代理")
input_box(x0 + 1300, yy + 18, 320, 36, "127.0.0.1,localhost")
text(x0, yy + 70, "AIPerf 0.12.0 可用。", "#246b49", f13)

ry = y + 292
rect(mx, ry, mx + mw, ry + 230, "#ffffff", "#dfe3ea", 8)
text(mx + 14, ry + 14, "结果", "#111827", f18b)
button(mx + 70, ry + 10, 58, 26, "待命", "#e8f0fe", "#174ea6", f12)
cw = int((mw - 28 - 50) / 6)
for i, (name, value) in enumerate([
    ("TTFT P50", "- ms"),
    ("请求 P99", "- ms"),
    ("ITL P50", "- ms"),
    ("输出 TPS", "-"),
    ("RPS", "-"),
    ("输出长度", "-"),
]):
    cx = mx + 14 + i * (cw + 10)
    rect(cx, ry + 50, cx + cw, ry + 138, "#fbfcfe", "#dfe3ea", 8)
    text(cx + 10, ry + 60, name, "#607089", f12)
    text(cx + 10, ry + 82, value, "#172033", f24b)
    draw.rounded_rectangle((cx + 10, ry + 122, cx + cw - 10, ry + 129), 4, fill="#e5eaf2")
for i, chart_title in enumerate(["延迟 / 并发", "吞吐 / 并发"]):
    cx = mx + 14 + i * (int((mw - 38) / 2) + 10)
    rect(cx, ry + 150, cx + int((mw - 38) / 2), ry + 216, "#ffffff", "#dfe3ea", 8)
    text(cx + 10, ry + 160, chart_title, "#405066", f12)
    draw.line((cx + 30, ry + 198, cx + int((mw - 38) / 2) - 18, ry + 198), fill="#c8d0dc")
    draw.line((cx + 30, ry + 174, cx + 30, ry + 198), fill="#c8d0dc")

sy = ry + 246
rect(mx, sy, mx + mw, sy + 245, "#ffffff", "#dfe3ea", 8)
text(mx + 14, sy + 14, "运行状态", "#111827", f18b)
button(mx + 98, sy + 10, 58, 26, "待命", "#e8f0fe", "#174ea6", f12)
for i, (name, value) in enumerate([("Run ID", "-"), ("状态", "-"), ("AIPerf", "是"), ("结果数", "0")]):
    cx = mx + 14 + i * (int((mw - 58) / 4) + 10)
    rect(cx, sy + 50, cx + int((mw - 58) / 4), sy + 138, "#fbfcfe", "#dfe3ea", 8)
    text(cx + 10, sy + 60, name, "#607089", f12)
    text(cx + 10, sy + 84, value, "#172033", f24b)
rect(mx + 14, sy + 150, mx + mw - 14, sy + 222, "#101418", "#101418", 8)
text(mx + 28, sy + 164, "准备就绪。", "#d6deeb", f14)
text(W / 2 - 185, H - 28, "(C)Copyright BlueSkyGPT 2026.08. All rights reserved.", "#596579", f12)

OUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUT)
print(OUT)
