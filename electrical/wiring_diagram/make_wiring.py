"""
Kiro / SO-101 electrical wiring diagram generator.

Source of truth: KIRO_FINAL.kicad_sch (Rev D) for topology, fuses and loads;
group_convo/markdown_source/power_calculation.md for wire gauges and connectors.

Run:  python make_wiring.py          -> kiro_wiring_diagram.svg
PNG:  rendered with headless Chrome/Edge (see render_png below).
"""
import os
import shutil
import subprocess

W, H = 2400, 1340
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

C = {
    "bg": "#f6f7fb", "card": "#ffffff", "line": "#d5dbe5", "ink": "#0f172a", "muted": "#64748b",
    "L": "#8b4513", "N": "#2563eb", "PE": "#16a34a", "PE2": "#eab308",
    "v12": "#dc2626", "v5": "#f59e0b", "gnd": "#111827", "usb": "#7c3aed", "ttl": "#0d9488",
    "ac": "#8b4513", "psu": "#475569", "fuse": "#334155", "jet": "#76b900", "servo": "#0d9488",
}
FUSE_COL = {"2 A": "#9ca3af", "5 A": "#d6b77a", "15 A": "#3b82f6", "spare": "#e5e7eb"}

out = []


def add(s):
    out.append(s)


def text(x, y, s, size=13, color=None, weight=400, anchor="start", family=FONT, italic=False):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color or C["ink"]}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{st}>{s}</text>')


def box(x, y, w, h, title, sub=None, accent="#334155", ref=None):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["card"]}" '
        f'stroke="{C["line"]}" stroke-width="1.5" filter="url(#shadow)"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="3" fill="{accent}"/>')
    if ref:
        tw = 9 * len(ref) + 14
        add(f'<rect x="{x + 12}" y="{y + 16}" width="{tw}" height="20" rx="10" fill="{accent}"/>')
        text(x + 12 + tw / 2, y + 31, ref, 12, "#fff", 700, "middle")
        text(x + 20 + tw, y + 31, title, 15, weight=700)
    else:
        text(x + 14, y + 31, title, 15, weight=700)
    if sub:
        for i, line in enumerate(sub if isinstance(sub, list) else [sub]):
            text(x + 14, y + 54 + i * 17, line, 12, C["muted"])


def wire(pts, color, width=4, dash=None, outline=True):
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
    if outline:
        add(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{width + 4}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{ds}/>')


def pe_wire(pts, width=4):
    wire(pts, C["PE"], width)
    wire(pts, C["PE2"], width, dash="10 10", outline=False)


def tag(x, y, s, color, anchor="middle"):
    w = 7.2 * len(s) + 16
    x0 = x - w / 2 if anchor == "middle" else x
    add(f'<rect x="{x0}" y="{y - 11}" width="{w}" height="22" rx="11" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
    text(x0 + w / 2, y + 4.5, s, 11.5, color, 600, "middle")


def term(x, y, label, side="right", color=None):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{color or C["ink"]}" stroke-width="2"/>')
    if label:
        if side == "right":
            text(x - 10, y + 4, label, 11.5, C["muted"], 600, "end")
        else:
            text(x + 10, y + 4, label, 11.5, C["muted"], 600)


def dot(x, y, color):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')


def gnd(x, y, length=18):
    wire([(x, y), (x, y + length)], C["gnd"], 3, outline=False)
    y2 = y + length
    for i, w in enumerate((18, 12, 6)):
        add(f'<line x1="{x - w / 2}" y1="{y2 + i * 5}" x2="{x + w / 2}" y2="{y2 + i * 5}" stroke="{C["gnd"]}" stroke-width="2.5"/>')
    text(x + 14, y2 + 8, "0V", 11, C["muted"], 700)


def blade(x, y, amp, label, spare=False):
    col = FUSE_COL["spare" if spare else amp]
    add(f'<rect x="{x}" y="{y - 13}" width="44" height="26" rx="5" fill="{col}" stroke="#334155" stroke-width="1.2"/>')
    text(x + 22, y + 4.5, amp if not spare else "–", 11.5, "#111" if not spare else "#94a3b8", 700, "middle")
    text(x + 54, y + 4.5, label, 12.5, C["muted"] if spare else C["ink"], 600)


def inline_fuse(x, y, ref, amp):
    add(f'<rect x="{x - 26}" y="{y - 14}" width="52" height="28" rx="6" fill="{FUSE_COL[amp]}" stroke="#334155" stroke-width="1.2"/>')
    text(x, y + 4.5, amp, 12, "#111", 700, "middle")
    text(x, y - 22, ref, 12, C["ink"], 700, "middle")


def servo_row(x, y, items, color, pitch=58, w=50):
    """items: list of labels; returns list of (cx, top, bottom)."""
    res = []
    for i, s in enumerate(items):
        bx = x + i * pitch
        add(f'<rect x="{bx}" y="{y}" width="{w}" height="40" rx="8" fill="#ecfdf5" stroke="{color}" stroke-width="1.5"/>')
        text(bx + w / 2, y + 25, s, 12, C["ink"], 700, "middle")
        res.append((bx + w / 2, y, y + 40))
    return res


def section(x, y, w, label, color):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{color}" opacity="0.85"/>')
    text(x, y - 10, label, 12.5, color, 800)


# ------------------------------------------------------------------ canvas
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs><filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
    '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.08"/></filter></defs>')
add(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')

# header
add(f'<rect x="0" y="0" width="{W}" height="96" fill="#0f172a"/>')
text(48, 50, "KIRO  ·  SO-101 Mobile Dual-Arm Robot", 28, "#fff", 800)
text(48, 78, "Electrical wiring diagram  —  one 12 V SMPS, one shared 5 V buck, returns to source", 15, "#cbd5e1")
text(W - 48, 50, "Rev F", 22, "#fff", 800, "end")
text(W - 48, 78, "KIRO_FINAL.kicad_sch + 2× Dorhea 4-way · no bus bar  ·  2026-10-26", 13, "#94a3b8", 400, "end")

# section headings
section(48, 140, 470, "AC MAINS 220 V", C["ac"])
section(560, 140, 1010, "12 V DISTRIBUTION", C["v12"])
section(1610, 140, 380, "5 V DISTRIBUTION", C["v5"])
section(2030, 140, 322, "USB / DATA", C["usb"])

# ------------------------------------------------------------------ AC side
box(48, 520, 140, 170, "Wall outlet", ["220 V AC", "50/60 Hz"], C["ac"])
box(250, 470, 200, 300, "AC inlet", ["IEC C14 + switch + fuse"], C["ac"], ref="J1")
# internal parts of the inlet module
add('<rect x="270" y="540" width="160" height="94" rx="8" fill="#fafafa" stroke="#e2e8f0"/>')
text(282, 560, "F0  5 A T · 250 V AC", 12, C["ink"], 700)
add('<rect x="282" y="568" width="60" height="16" rx="8" fill="#fde68a" stroke="#92400e"/>')
text(350, 581, "slow-blow", 11, C["muted"])
text(282, 608, "SW1  DPST (L + N)", 12, C["ink"], 700)
add('<line x1="284" y1="622" x2="306" y2="622" stroke="#334155" stroke-width="2"/>'
    '<line x1="306" y1="622" x2="326" y2="611" stroke="#334155" stroke-width="2"/>'
    '<line x1="328" y1="622" x2="350" y2="622" stroke="#334155" stroke-width="2"/>')
for y, lab in ((680, "L"), (710, "N"), (740, "PE")):
    term(450, y, lab, "right")
# power cord
wire([(188, 605), (250, 605)], "#475569", 10)
tag(219, 640, "cord", "#475569")

# ------------------------------------------------------------------ SMPS
box(560, 470, 230, 340, "SMPS 12 V", ["HS-350-12 · fan-cooled", "12 V · ~29 A · 350 W", "set to 12.0–12.3 V"], C["psu"], ref="PSU1")
for y, lab in ((680, "L"), (710, "N"), (740, "FG")):
    term(560, y, lab, "left")
term(790, 580, "+V", "right", C["v12"])
term(790, 760, "−V", "right", C["gnd"])
wire([(455, 680), (555, 680)], C["L"], 4)
wire([(455, 710), (555, 710)], C["N"], 4)
pe_wire([(455, 740), (555, 740)])
tag(505, 650, "0.75 mm² · 18 AWG", C["L"])

# ------------------------------------------------------------------ fuse box 12 V + ground bus
FBX, FBY, FBW, FBH = 900, 330, 260, 330
box(FBX, FBY, FBW, FBH, "Fuse box 12 V", ["Dorhea 4-way blade · no − bus"], C["fuse"], ref="FB1")
term(FBX, 580, "+ IN", "left", C["v12"])
F_Y = {"F1": 420, "F2": 475, "F3": 530}
blade(FBX + 20, F_Y["F1"], "5 A", "F1  Jetson")
blade(FBX + 20, F_Y["F2"], "15 A", "F2  Wheels")
blade(FBX + 20, F_Y["F3"], "15 A", "F3  Buck 5 V in")
blade(FBX + 20, 625, "spare", "slot 4  spare", spare=True)
for y in F_Y.values():
    term(FBX + FBW, y, "", color=C["v12"])

# no bus bar: 12 V returns land directly on the SMPS COM (-V) terminals
box(FBX, 700, FBW, 150, "12 V returns", ["no bus bar · 1 wire per COM screw", "U2 Jetson − · A1 base 0V · U1 IN−"], C["gnd"], ref="COM")
add(f'<rect x="{FBX + 16}" y="{800}" width="{FBW - 32}" height="34" rx="8" fill="#111827"/>')
text(FBX + FBW / 2, 822, "PSU1 COM ×2 (−V)", 12.5, "#fff", 700, "middle")
term(FBX, 760, "", color=C["gnd"])

# SMPS -> fuse box, SMPS COM -> 12 V returns
wire([(795, 580), (895, 580)], C["v12"], 7)
tag(845, 552, "12 AWG", C["v12"])
text(845, 610, "+12V_MAIN", 11.5, C["v12"], 700, "middle")
wire([(795, 760), (895, 760)], C["gnd"], 7)
tag(845, 732, "14–18 AWG", C["gnd"])

# ------------------------------------------------------------------ 12 V loads
FX = FBX + FBW + 5
# Jetson
box(1290, 300, 270, 170, "Jetson Orin Nano Super", ["Dev kit · DC jack 9–20 V", "5.5 × 2.5 mm barrel, centre +"], C["jet"], ref="U2")
term(1290, 420, "+", "left", C["v12"])
wire([(FX, F_Y["F1"]), (1285, 420)], C["v12"], 4)
tag(1222, 382, "18 AWG", C["v12"])
gnd(1320, 470)
JET_USB = {"cam": 350, "wrist": 395, "hub": 440}
for k, y in JET_USB.items():
    term(1560, y, "", color=C["usb"])

# wheel branch
box(1290, 560, 210, 92, "CH343 base adapter", ["servo bus board · W_A / W_B"], C["servo"], ref="A1")
term(1290, 622, "", "left", C["v12"])
LANE_W = 1240
wire([(FX, F_Y["F2"]), (LANE_W, F_Y["F2"]), (LANE_W, 622), (1285, 622)], C["v12"], 5)
tag(1205, 500, "14 AWG", C["v12"])
text(1290, 548, "+12V_WHEELS", 11, C["v12"], 700)
gnd(1470, 652, 14)
wheels = servo_row(1290, 720, ["FR 7", "RR 9", "FL 8", "RL 10"], C["servo"], pitch=66, w=56)
wire([(LANE_W, 622), (LANE_W, 700), (wheels[-1][0], 700)], C["v12"], 4)
dot(LANE_W, 622, C["v12"])
for cx, top, _ in wheels:
    wire([(cx, 700), (cx, top)], C["v12"], 3)
    dot(cx, 700, C["v12"])
text(1290, 790, "Wheel servos ST3215-C018 · 22 AWG power taps", 11.5, C["muted"])
text(1290, 806, "TTL:  W_A = FR 7 → RR 9    W_B = FL 8 → RL 10", 11.5, C["ttl"], 600)

# buck converter
box(1290, 870, 230, 120, "Buck 12 V → 5 V", ["20 A class · set 5.0–5.1 V", "needs airflow / heatsink"], C["v5"], ref="U1")
term(1290, 965, "IN+", "left", C["v12"])
term(1520, 965, "OUT+", "right", C["v5"])
LANE_B = 1215
wire([(FX, F_Y["F3"]), (LANE_B, F_Y["F3"]), (LANE_B, 965), (1285, 965)], C["v12"], 5)
tag(LANE_B, 860, "14 AWG", C["v12"])
gnd(1400, 990, 14)
text(1290, 1022, "U1 OUT− ← A2, A3 returns (5 V)", 11.5, C["gnd"], 700)

# ------------------------------------------------------------------ 5 V side
RAIL = 1585
wire([(1525, 965), (RAIL, 965), (RAIL, 680), (1610, 680)], C["v5"], 6)
tag(1560, 995, "14 AWG", C["v5"])
text(1576, 940, "+5V_MAIN", 12, C["v5"], 800, "end")

box(1615, 380, 170, 330, "Fuse box 5 V", ["Dorhea 4-way", "fed from U1 OUT+"], C["v5"], ref="FB2")
term(1615, 680, "+ IN", "left", C["v5"])
blade(1630, 495, "2 A", "F4  Leaders")
blade(1630, 545, "15 A", "F5  Followers")
blade(1630, 595, "spare", "slot 3  spare", spare=True)
blade(1630, 640, "spare", "slot 4  spare", spare=True)
term(1785, 495, "", color=C["v5"])
term(1785, 545, "", color=C["v5"])

# leaders
box(1815, 410, 185, 82, "Leader adapter", ["CH343 · torque off"], C["servo"], ref="A2")
term(1815, 470, "", "left", C["v5"])
wire([(1790, 495), (1800, 495), (1800, 470), (1810, 470)], C["v5"], 4)
tag(1915, 396, "20 AWG", C["v5"])
gnd(1975, 492, 10)
leaders = servo_row(1820, 565, ["1", "2", "3", "4", "5", "6"], C["servo"], pitch=34, w=29)
wire([(1905, 492), (1905, 548)], C["v5"], 3, outline=False)
wire([(leaders[0][0], 548), (leaders[-1][0], 548)], C["v5"], 3)
for cx, top, _ in leaders:
    wire([(cx, 548), (cx, top)], C["v5"], 2.5)
text(1815, 625, "6 × leader STS3215 (5 V)", 11.5, C["muted"])
text(1815, 641, "L_A = ID 1–3    L_B = ID 4–6", 11.5, C["ttl"], 600)

# followers
box(1815, 740, 185, 82, "Follower adapter", ["CH343 · 5 V TEST"], C["servo"], ref="A3")
term(1815, 780, "", "left", C["v5"])
wire([(1790, 545), (1806, 545), (1806, 780), (1810, 780)], C["v5"], 5)
tag(1915, 726, "14 AWG", C["v5"])
gnd(1975, 822, 10)
followers = servo_row(1820, 880, ["1", "2", "3", "4", "5", "6"], C["servo"], pitch=34, w=29)
wire([(1905, 822), (1905, 863)], C["v5"], 4, outline=False)
wire([(followers[0][0], 863), (followers[-1][0], 863)], C["v5"], 3.5)
for cx, top, _ in followers:
    wire([(cx, 863), (cx, top)], C["v5"], 3)
text(1815, 940, "6 × follower STS3215 (5 V test)", 11.5, C["muted"])
text(1815, 956, "F_A = ID 1–3    F_B = ID 4–6", 11.5, C["ttl"], 600)
text(1615, 735, "Feed FB2 from the 5 V", 11.5, "#b45309", 700)
text(1615, 751, "buck only — never 12 V.", 11.5, "#b45309", 700)

# ------------------------------------------------------------------ USB / data
UX = 2060
box(UX, 290, 290, 70, "Gemini 335 RGB-D", None, C["usb"], ref="J2")
box(UX, 380, 290, 70, "Wrist camera", None, C["usb"], ref="J3")
box(UX, 520, 290, 270, "VL815 powered USB hub", None, C["usb"], ref="H1")
ports = [("BASE", "→ A1 base adapter"), ("LEADER", "→ A2 leader adapter"),
         ("FOLLOWER", "→ A3 follower adapter"), ("LIDAR", "→ J4 RPLIDAR C1"), ("GAMEPAD", "→ J5 gamepad")]
for i, (p, dest) in enumerate(ports):
    yy = 585 + i * 30
    add(f'<rect x="{UX + 16}" y="{yy - 13}" width="86" height="22" rx="6" fill="#f5f3ff" stroke="#c4b5fd"/>')
    text(UX + 59, yy + 3, p, 11, C["usb"], 700, "middle")
    text(UX + 112, yy + 3, dest, 12, C["ink"])
text(UX + 16, 755, "DC supply: OPEN — verify label,", 11.5, "#b45309", 700)
text(UX + 16, 771, "polarity and current before wiring", 11.5, "#b45309", 700)
box(UX, 820, 290, 70, "RPLIDAR C1", None, C["usb"], ref="J4")
box(UX, 910, 290, 70, "Gamepad", None, C["usb"], ref="J5")

wire([(1565, JET_USB["cam"]), (1600, JET_USB["cam"]), (1600, 260), (2046, 260), (2046, 325), (UX - 4, 325)], C["usb"], 3, "8 6")
wire([(1565, JET_USB["wrist"]), (1610, JET_USB["wrist"]), (1610, 270), (2038, 270), (2038, 415), (UX - 4, 415)], C["usb"], 3, "8 6")
wire([(1565, JET_USB["hub"]), (1620, JET_USB["hub"]), (1620, 280), (2030, 280), (2030, 555), (UX - 4, 555)], C["usb"], 3, "8 6")
text(1810, 252, "USB_CAM · USB_WRIST · USB_HUB", 11.5, C["usb"], 700, "middle")
wire([(UX + 30, 790), (UX + 30, 820)], C["usb"], 3, "8 6")
wire([(UX + 260, 790), (UX + 260, 800), (2370, 800), (2370, 945), (UX + 290, 945)], C["usb"], 3, "8 6")

# ------------------------------------------------------------------ legend + notes
LY = 1040
add(f'<rect x="48" y="{LY}" width="{W - 96}" height="250" rx="14" fill="#fff" stroke="{C["line"]}"/>')
text(72, LY + 34, "LEGEND", 13, C["ink"], 800)
legend = [("L", C["L"], None), ("N", C["N"], None), ("PE / FG", "pe", None), ("+12 V", C["v12"], None),
          ("+5 V", C["v5"], None), ("0 V return", C["gnd"], None), ("USB", C["usb"], "8 6")]
for i, (lab, col, dash) in enumerate(legend):
    lx, ly = 72 + (i % 4) * 150, LY + 64 + (i // 4) * 34
    if col == "pe":
        pe_wire([(lx, ly), (lx + 46, ly)])
    else:
        wire([(lx, ly), (lx + 46, ly)], col, 5, dash)
    text(lx + 56, ly + 4, lab, 12.5, C["ink"], 600)
text(72, LY + 150, "Fuses", 12.5, C["ink"], 700)
for i, (amp, col) in enumerate((("2 A", "#9ca3af"), ("5 A", "#d6b77a"), ("15 A", "#3b82f6"))):
    add(f'<rect x="{130 + i * 70}" y="{LY + 137}" width="52" height="22" rx="5" fill="{col}" stroke="#334155"/>')
    text(156 + i * 70, LY + 153, amp, 11.5, "#111", 700, "middle")
gnd(400, LY + 128, 10)
text(430, LY + 154, "= return wire to its source (note 1)", 12, C["muted"])

NX = 720
text(NX, LY + 34, "NOTES", 13, C["ink"], 800)
notes = [
    "1.  No bus bar: 12 V returns (U2, A1, U1 IN−) go to PSU1 COM; 5 V returns (A2, A3) go to U1 OUT−. Never daisy-chain grounds.",
    "2.  Mains: insulate all AC spade terminals with heat-shrink, PE to SMPS FG, keep AC wiring away from servo and USB harnesses.",
    "3.  Bring-up: set SMPS to 12.0–12.3 V and the buck to 5.0–5.1 V with no load; then fit F1 + F3, then F2, then F4 / F5 in FB2 one at a time.",
    "4.  Followers run on 5 V as a TEST (schematic note). Servo limit is 8.0 V — never feed the 12 V rail into an arm adapter.",
    "5.  Hub DC input is intentionally left open in the schematic: confirm 5 V or 12 V input before connecting it.",
    "6.  SMPS: HS-350-12 (12 V, ~29 A) covers the 20–27 A peak. Mount flat, fan up, keep ≥ 20 mm free above the fan. USB hub lives on the middle floor.",
    "7.  Wire sizes from power_calculation.md · servo leads 22 AWG Molex 5264 (GND / VCC / SIG) · 12 V branches XT60, 5 V outputs XT30.",
]
for i, n in enumerate(notes):
    text(NX, LY + 62 + i * 26, n, 12.5, C["ink"])

add("</svg>")

here = os.path.dirname(os.path.abspath(__file__))
svg_path = os.path.join(here, "kiro_wiring_diagram.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote", svg_path)


def render_png(svg, png, scale=1.5):
    """Render the SVG to PNG with a headless Chromium browser (Chrome or Edge)."""
    candidates = [shutil.which("chrome"), shutil.which("msedge"),
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    exe = next((c for c in candidates if c and os.path.exists(c)), None)
    if not exe:
        print("no Chrome/Edge found - open the SVG in a browser instead")
        return
    html = os.path.join(here, "_render.html")
    with open(html, "w", encoding="utf-8") as f:
        f.write(f'<html><body style="margin:0"><img src="{os.path.basename(svg)}" '
                f'style="width:{W}px;height:{H}px;display:block"></body></html>')
    subprocess.run([exe, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={os.path.join(here, '_chrome_profile')}",
                    f"--force-device-scale-factor={scale}", f"--window-size={W},{H}",
                    f"--screenshot={png}", "file:///" + html.replace("\\", "/")],
                   capture_output=True)
    os.remove(html)
    shutil.rmtree(os.path.join(here, "_chrome_profile"), ignore_errors=True)
    print("wrote", png)


if __name__ == "__main__":
    render_png(svg_path, os.path.join(here, "kiro_wiring_diagram.png"))
