#!/usr/bin/env python3
"""Builds the GitHub profile README cards (light + dark SVGs) for emir-0011d.

Edit the CONTENT block, then run:  python3 build.py
Contribution data is read from contrib.json (refresh with the gh command in README-howto).
"""
import base64, datetime as dt, html, json, math, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "profile" if (ROOT / "profile").is_dir() else ROOT
ASSETS = OUT / "assets"

# ---------------- CONTENT ----------------
NAME = "Emircan Çelik"
ROLE = "Product Designer"
PLACE = "Belgrade"
LEAD = "Product designer at Nicey Studio."
REST = "Building design systems that code can trust, plus a few side projects on the way."
FACTS = [("Building", "ToolsCrafter"), ("Focus", "Design systems"), ("Tools", "Figma, Framer")]
LINKS = [
    ("Website", "https://emircancelik.com"),
    ("LinkedIn", "https://linkedin.com/in/emircan1"),
    ("X", "https://x.com/CelkEmircan"),
    ("Dribbble", "https://dribbble.com/celkemircan"),
]
# -----------------------------------------

THEMES = {
    "light": dict(fg="#0a0a0a", mu="#6b6b6b", fa="#e3e3e3"),
    "dark": dict(fg="#ededed", mu="#8b8b8b", fa="#2b2b2b"),
}

def font_face(subsets=("latin", "latin-ext")):
    out = []
    for f, rng in (("latin", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"),
                   ("latin-ext", "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF")):
        if f not in subsets:
            continue
        b64 = base64.b64encode((ROOT / "fonts" / f"{f}.woff2").read_bytes()).decode()
        out.append(f"@font-face {{ font-family: I; src: url(data:font/woff2;base64,{b64}) format('woff2'); font-weight: 400 600; unicode-range: {rng}; }}")
    return "\n".join(out)

FONT = font_face()
FONT_LATIN = font_face(("latin",))

BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
.w { width: 100%; height: 100%; container-type: inline-size; font-family: I, -apple-system, BlinkMacSystemFont, sans-serif;
     font-size: 14px; line-height: 20px; letter-spacing: -.006em; color: var(--fg); -webkit-font-smoothing: antialiased;
     font-feature-settings: 'kern', 'tnum', 'cv11', 'ss01'; }
.m { color: var(--mu); }
.f { opacity: 0; animation: f .9s cubic-bezier(.2,.6,.2,1) forwards; animation-delay: var(--d, 0s); }
@keyframes f { from { opacity: 0; transform: translateY(3px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { .f, .b { animation: none !important; opacity: 1; transform: none; } }
"""

def theme_vars(t):
    c = THEMES[t]
    return f".w {{ --fg: {c['fg']}; --mu: {c['mu']}; --fa: {c['fa']}; }}"

def wrap(height, css, body, label="", font=None):
    aria = f' role="img" aria-label="{html.escape(label)}"' if label else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}" fill="none"{aria}>\n'
            f'<foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" class="w">'
            f'<style><![CDATA[{font or FONT}\n{BASE_CSS}\n{css}]]></style>{body}</div></foreignObject></svg>\n')

LOGIN = "emir-0011d"
QUERY = 'query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'

def fetch_calendar():
    """Live data from GitHub when GITHUB_TOKEN is set (used by the daily Action), else contrib.json."""
    import os, urllib.request
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        data = json.loads((ROOT / "contrib.json").read_text())["data"]
        return (data.get("viewer") or data.get("user"))["contributionsCollection"]["contributionCalendar"]
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"l": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def contributions():
    cal = fetch_calendar()
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days = days[-365:]
    # current streak (today may still be empty)
    streak = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            streak += 1
        elif i == 0:
            continue
        else:
            break
    return cal["totalContributions"], days, streak

def plot(days):
    mx = max(d["contributionCount"] for d in days) or 1
    lines = []
    for i, d in enumerate(days):
        c = d["contributionCount"]
        x = i + 0.5
        delay = 0.9 + i * 0.003
        if c:
            y = 72 - (10 + 58 * math.sqrt(c / mx))
            lines.append(f'<line class="b on" x1="{x}" x2="{x}" y1="72" y2="{y:.2f}" style="animation-delay:{delay:.3f}s"/>')
        else:
            lines.append(f'<line class="b off" x1="{x}" x2="{x}" y1="72" y2="70" style="animation-delay:{delay:.3f}s"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" class="plot" viewBox="0 0 {len(days)} 72" preserveAspectRatio="none">'
           + "".join(lines) + "</svg>")
    # month labels
    months, seen = [], set()
    for i, d in enumerate(days):
        date = dt.date.fromisoformat(d["date"])
        key = (date.year, date.month)
        if date.day <= 7 and key not in seen and i < len(days) - 14:
            seen.add(key)
            months.append(f'<span class="m" style="left:{i / len(days) * 100:.2f}%">{date.strftime("%b")}</span>')
    return svg, "".join(months)

def main_card(t, total, days, streak):
    plot_svg, months = plot(days)
    css = theme_vars(t) + """
.c { height: 100%; display: flex; flex-direction: column; padding-bottom: 20px; }
.g { display: grid; grid-template-columns: repeat(12, minmax(0,1fr)); }
.top b { grid-column: 1/7; font-weight: 500; } .top .r { grid-column: 7/10; } .top .z { grid-column: 10/13; text-align: right; }
.sent p { grid-column: 7/13; font-size: 26px; line-height: 1.23; letter-spacing: -.022em; padding-top: 56px; text-wrap: pretty; }
.fx { grid-column: 7/13; margin-top: 28px; display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px; }
.fc { display: flex; flex-direction: column; min-width: 0; } .fc .v { overflow-wrap: anywhere; }
.gr { margin-top: auto; padding-top: 24px; }
.meta { display: flex; justify-content: space-between; margin-bottom: 14px; }
svg.plot { display: block; width: 100%; height: 72px; overflow: visible; }
.b { stroke-width: 1px; vector-effect: non-scaling-stroke; transform-box: fill-box; transform-origin: bottom;
     transform: scaleY(0); animation: grow .8s cubic-bezier(.2,.7,.2,1) forwards; }
.on { stroke: var(--fg); } .off { stroke: var(--fa); }
@keyframes grow { to { transform: none; } }
.tl { position: relative; height: 20px; margin-top: 8px; } .tl span { position: absolute; top: 0; }
@container (max-width: 699px) { .sent p, .fx { grid-column: 5/13; } .sent p { font-size: 23px; } }
@container (max-width: 559px) { .sent p, .fx { grid-column: 1/13; } .sent p { font-size: 21px; padding-top: 40px; } .fx { margin-top: 22px; gap: 12px; }
  .top .r { grid-column: 7/13; text-align: right; } .top .z { display: none; } .tl span:nth-child(even) { display: none; } .nx { display: none; } }
"""
    facts = "".join(f'<div class="fc"><span class="m">{html.escape(k)}</span><span class="v">{html.escape(v)}</span></div>' for k, v in FACTS)
    today = dt.date.today().strftime("%b %-d")
    body = f"""<div class="c">
<div class="g top"><b class="f">{html.escape(NAME)}</b><span class="r m f" style="--d:.08s">{html.escape(ROLE)}</span><span class="z m f" style="--d:.16s">{html.escape(PLACE)}</span></div>
<div class="g sent"><p class="f" style="--d:.3s">{html.escape(LEAD)} <span class="m">{html.escape(REST)}</span></p><div class="fx f" style="--d:.42s">{facts}</div></div>
<div class="gr f" style="--d:.5s"><div class="meta"><span>{total:,} <span class="m">contributions<span class="nx"> in the last year</span></span></span><span class="m">Updated {today}</span></div>{plot_svg}<div class="tl">{months}</div></div>
</div>"""
    label = f"{NAME}. {LEAD} {REST} " + " ".join(f"{k}: {v}." for k, v in FACTS) + f" {total:,} contributions in the last year."
    return wrap(524, css, body, label)

def link_card(t, text):
    css = theme_vars(t) + """
a, span.l { display: flex; align-items: center; gap: 6px; color: var(--fg); text-decoration: none; height: 32px;
           border-top: 1px solid var(--fa); padding-top: 2px; margin-right: 12px; }
.ar { color: var(--mu); }
"""
    body = f'<span class="l f"><span>{html.escape(text)}</span><span class="ar">↗</span></span>'
    return wrap(32, css, body, font=FONT_LATIN)

def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    total, days, streak = contributions()
    for t in THEMES:
        (ASSETS / f"main-{t}.svg").write_text(main_card(t, total, days, streak))
        for i, (text, _) in enumerate(LINKS):
            (ASSETS / f"link-{i}-{t}.svg").write_text(link_card(t, text))
    alt = f"{NAME}. {LEAD} {REST}"
    w = f"{100 // len(LINKS)}%"
    links = "".join(
        f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/link-{i}-dark.svg">'
        f'<img src="assets/link-{i}-light.svg" alt="{html.escape(text)}" width="{w}" height="32"></picture></a>'
        for i, (text, url) in enumerate(LINKS))
    readme = (
        f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/main-dark.svg">'
        f'<img src="assets/main-light.svg" alt="{html.escape(alt)}" width="100%" height="524" align="left"></picture>\n'
        f'<img src="data:null;," width="100%" height="0" align="left" alt="">\n'
        f'<p>{links}</p>\n')
    (OUT / "README.md").write_text(readme)
    print("total", total, "streak", streak, "->", OUT)

if __name__ == "__main__":
    main()
