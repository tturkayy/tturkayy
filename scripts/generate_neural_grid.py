import json
import math
import os
import urllib.request

USERNAME = "tturkayy"
OUTPUT_PATH = "dist/neural-grid.svg"

def fetch_contributions():
    url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("contributions", [])
    except Exception:
        return [{"level": (i % 5), "count": i % 7} for i in range(52 * 7)]

def generate_svg():
    contribs = fetch_contributions()
    data = contribs[-(52 * 7):] if len(contribs) >= 364 else contribs
    while len(data) < 364:
        data.insert(0, {"level": 0, "count": 0})

    cols = 52
    rows = 7
    cell_size = 11
    gap = 3.5
    offset_x = 30
    offset_y = 65

    width = int(offset_x + cols * (cell_size + gap) + 40)
    height = 240

    c_bg = "#080b11"
    c_border = "#1f293d"
    c_muted = "#5c6b84"
    c_accent = "#3b82f6"
    c_loss = "#f43f5e"

    color_levels = [
        "#111622",
        "#1e3a5f",
        "#2563eb",
        "#3b82f6",
        "#60a5fa"
    ]

    total_commits = sum(d.get("count", 0) for d in data)
    grid_w = cols * (cell_size + gap)
    grid_h = rows * (cell_size + gap)

    loss_y_base = height - 28
    loss_pts = []
    num_pts = 60
    for i in range(num_pts):
        px = offset_x + (i / (num_pts - 1)) * grid_w
        val = 18.0 * math.exp(-i / 16.0) + 2.5 * math.cos(i * 0.45) * math.exp(-i / 30.0)
        py = loss_y_base - val
        loss_pts.append(f"{px:.1f},{py:.1f}")

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <defs>')
    svg.append('    <linearGradient id="gradLoss" x1="0%" y1="0%" x2="100%" y2="0%">')
    svg.append(f'      <stop offset="0%" stop-color="{c_loss}" stop-opacity="0.9"/>')
    svg.append(f'      <stop offset="100%" stop-color="{c_accent}" stop-opacity="0.9"/>')
    svg.append('    </linearGradient>')
    svg.append('    <linearGradient id="scanBeam" x1="0%" y1="0%" x2="100%" y2="0%">')
    svg.append(f'      <stop offset="0%" stop-color="{c_accent}" stop-opacity="0"/>')
    svg.append(f'      <stop offset="50%" stop-color="{c_accent}" stop-opacity="0.3"/>')
    svg.append(f'      <stop offset="100%" stop-color="{c_accent}" stop-opacity="0"/>')
    svg.append('    </linearGradient>')
    svg.append('    <style>')
    svg.append(f'      .mono {{ font-family: monospace, Courier; font-size: 11px; fill: {c_muted}; }}')
    svg.append('      .mono-bold { font-family: monospace, Courier; font-size: 12px; font-weight: bold; fill: #f3f6fc; }')
    svg.append('      .tensor-cell { rx: 2.5px; ry: 2.5px; }')
    svg.append(f'      @keyframes scan {{ 0% {{ transform: translateX(-60px); }} 100% {{ transform: translateX({width + 60}px); }} }}')
    svg.append('      .scanner { animation: scan 6s cubic-bezier(0.4, 0, 0.2, 1) infinite; }')
    svg.append('    </style>')
    svg.append('  </defs>')

    # Background
    svg.append(f'  <rect width="{width}" height="{height}" rx="12" fill="{c_bg}" stroke="{c_border}" stroke-width="1.2"/>')

    # Header texts (Entities escaped cleanly)
    svg.append(f'  <text x="{offset_x}" y="32" class="mono-bold">optimizer::adamw (lr=3e-4) - gradient_step_sweep</text>')
    svg.append(f'  <text x="{offset_x}" y="48" class="mono">tensor_dim: [7, 52] | active_params: {total_commits} tokens | loss: 0.0412 (converged)</text>')

    # Grid Cells
    for idx, cell in enumerate(data):
        col = idx // rows
        row = idx % rows
        x = offset_x + col * (cell_size + gap)
        y = offset_y + row * (cell_size + gap)
        lvl = min(max(cell.get("level", 0), 0), 4)
        fill = color_levels[lvl]
        svg.append(f'  <rect class="tensor-cell" x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" fill="{fill}"/>')

    # Scanner beam
    svg.append('  <g class="scanner">')
    svg.append(f'    <rect x="0" y="{offset_y}" width="40" height="{grid_h:.1f}" fill="url(#scanBeam)"/>')
    svg.append('  </g>')

    # Loss trace line
    svg.append(f'  <text x="{offset_x}" y="{loss_y_base - 22}" class="mono" font-size="9px">loss_convergence_trace - e(t)</text>')
    svg.append(f'  <line x1="{offset_x}" y1="{loss_y_base}" x2="{offset_x + grid_w:.1f}" y2="{loss_y_base}" stroke="{c_border}" stroke-dasharray="2,2" stroke-width="0.8"/>')
    svg.append(f'  <polyline points="{" ".join(loss_pts)}" fill="none" stroke="url(#gradLoss)" stroke-width="1.6" stroke-linecap="round"/>')
    svg.append('</svg>')

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated clean SVG at {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_svg()
