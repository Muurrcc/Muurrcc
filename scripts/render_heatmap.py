import json, datetime as dt

data = json.load(open("data/contribs.json"))
days = data["days"]
COL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, X0, Y0 = 12, 3, 20, 34
first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # Sunday-first rows
W = X0 * 2 + 53 * (CELL + GAP)
H = Y0 + 7 * (CELL + GAP) + 50

rects = []
for i, d in enumerate(days):
    n = i + offset
    wk, dow = divmod(n, 7)
    x, y = X0 + wk * (CELL + GAP), Y0 + dow * (CELL + GAP)
    delay = (wk + dow) * 0.02
    rects.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                 f'fill="{COL[d["level"]]}" style="animation-delay:{delay:.2f}s">'
                 f'<title>{d["count"]} on {d["date"]}</title></rect>')

legend_x = W - X0 - 5 * (CELL + 4) - 70
legend = f'<text x="{legend_x}" y="{H-14}" class="t">Less</text>' + "".join(
    f'<rect x="{legend_x+34+i*(CELL+4)}" y="{H-24}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
    for i, c in enumerate(COL)) + f'<text x="{legend_x+34+5*(CELL+4)+4}" y="{H-14}" class="t">More</text>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.t{{font:11px ui-monospace,Menlo,monospace;fill:#8b949e}}
.h{{font:13px ui-monospace,Menlo,monospace;fill:#39d353}}
.c{{opacity:0;transform:translateY(-8px);animation:in .5s ease-out forwards}}
@keyframes in{{to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.c{{animation:none;opacity:1;transform:none}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
<text x="{X0}" y="22" class="h">$ git log --contributions --since="1 year"</text>
{"".join(rects)}
<text x="{X0}" y="{H-14}" class="t">{data["total"]} contributions · best day {data["best"]["count"]} · longest streak {data["longest_streak"]}d · current {data["current_streak"]}d</text>
{legend}
</svg>'''
open("assets/heatmap.svg", "w").write(svg)
