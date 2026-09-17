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
    cols = 38
    rows = 7
    total_cells = cols * rows

    data = contribs[-total_cells:] if len(contribs) >= total_cells else contribs
    while len(data) < total_cells:
        data.insert(0, {"level": 0, "count": 0})

    width = 890
    height = 360
    
    # Grid yerleşimi
    off_x = 24
    off_y = 66
    c_sz = 10.0
    c_gap = 3.2
    grid_w = cols * (c_sz + c_gap)
    grid_h = rows * (c_sz + c_gap)

    # Renk Paleti (Deep dark tensorboard)
    c_bg = "#07090e"
    c_card = "#0f131d"
    c_border = "#1a2233"
    c_border_light = "#253248"
    c_text = "#f1f5f9"
    c_muted = "#64748b"
    c_blue = "#3b82f6"
    c_cyan = "#06b6d4"
    c_green = "#10b981"
    c_rose = "#f43f5e"
    c_amber = "#f59e0b"

    levels = ["#111622", "#1d2e4a", "#2563eb", "#3b82f6", "#60a5fa"]
    total_tokens = sum(d.get("count", 0) for d in data)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append('  <defs>')
    # Gradientler
    svg.append(f'    <linearGradient id="gLoss" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{c_rose}"/><stop offset="100%" stop-color="{c_blue}"/></linearGradient>')
    svg.append(f'    <linearGradient id="gGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{c_amber}"/><stop offset="100%" stop-color="{c_green}"/></linearGradient>')
    svg.append(f'    <linearGradient id="gBeam" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{c_blue}" stop-opacity="0"/><stop offset="50%" stop-color="{c_blue}" stop-opacity="0.25"/><stop offset="100%" stop-color="{c_blue}" stop-opacity="0"/></linearGradient>')
    
    # CSS Styles
    svg.append('    <style>')
    svg.append(f'      .mono {{ font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace; font-size: 11px; fill: {c_muted}; }}')
    svg.append(f'      .mono-title {{ font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace; font-size: 11px; font-weight: 700; fill: {c_text}; }}')
    svg.append(f'      .mono-val {{ font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace; font-size: 15px; font-weight: 700; fill: {c_text}; }}')
    svg.append(f'      .mono-sm {{ font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace; font-size: 9.5px; fill: {c_muted}; }}')
    svg.append(f'      .tag {{ font-family: ui-monospace, SFMono-Regular, monospace; font-size: 9px; font-weight: 700; }}')
    svg.append('      @keyframes pulseDot { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }')
    svg.append('      .live-dot { animation: pulseDot 1.8s infinite ease-in-out; }')
    svg.append(f'      @keyframes sweep {{ 0% {{ transform: translateX(-40px); }} 100% {{ transform: translateX({grid_w + 60:.0f}px); }} }}')
    svg.append('      .scanner {{ animation: sweep 5.5s cubic-bezier(0.4, 0, 0.2, 1) infinite; }}')
    svg.append('    </style>')
    svg.append('  </defs>')

    # Ana Çerçeve
    svg.append(f'  <rect width="{width}" height="{height}" rx="12" fill="{c_bg}" stroke="{c_border}" stroke-width="1.2"/>')

    # Top Bar: Status & Hardware
    svg.append(f'  <rect x="0" y="0" width="{width}" height="42" fill="{c_card}" rx="12" />')
    svg.append(f'  <rect x="0" y="32" width="{width}" height="10" fill="{c_card}" />')
    svg.append(f'  <line x1="0" y1="42" x2="{width}" y2="42" stroke="{c_border}" stroke-width="1"/>')

    svg.append(f'  <circle cx="28" cy="21" r="4.5" fill="{c_green}" class="live-dot"/>')
    svg.append(f'  <text x="40" y="25" class="mono-title">MONITOR::LIVE</text>')
    svg.append(f'  <text x="135" y="25" class="mono">epoch: 84/100 | step: 42,800 | lr: 1.2e-4 (cosine) | opt: adamw</text>')
    svg.append(f'  <text x="{width - 24}" y="25" text-anchor="end" class="mono-title" fill="{c_blue}">TARGET: OPTICAL_LATENT_SPACE</text>')

    # --- SOL: COMMIT ACTIVATION TENSOR PANEL ---
    p_tensor_w = grid_w + 32
    svg.append(f'  <rect x="16" y="52" width="{p_tensor_w:.1f}" height="152" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="30" y="70" class="mono-title">ACTIVATION TENSOR [7, 38]</text>')
    svg.append(f'  <text x="{p_tensor_w}" y="70" text-anchor="end" class="mono-sm">sparsity: 18.4% | active: {total_tokens} commits</text>')

    for idx, cell in enumerate(data):
        col = idx // rows
        row = idx % rows
        cx = off_x + 6 + col * (c_sz + c_gap)
        cy = off_y + 18 + row * (c_sz + c_gap)
        lvl = min(max(cell.get("level", 0), 0), 4)
        svg.append(f'  <rect x="{cx:.1f}" y="{cy:.1f}" width="{c_sz}" height="{c_sz}" rx="2" fill="{levels[lvl]}"/>')

    # Tensor tarama huzmesi
    svg.append(f'  <g class="scanner">')
    svg.append(f'    <rect x="{off_x + 6}" y="{off_y + 18}" width="34" height="{grid_h:.1f}" fill="url(#gBeam)" />')
    svg.append(f'  </g>')

    # Alt tensör durum özeti
    svg.append(f'  <text x="30" y="193" class="mono-sm">input_dim: 266 feat &bull; norm: layernorm &bull; activation: gelu &bull; throughput: 1.84k toks/s</text>')

    # --- SAĞ: 4 METRİK KARTLARI ---
    right_x = p_tensor_w + 28
    right_w = width - right_x - 16
    col_w = (right_w - 12) / 2

    # Metrik 1: Train Loss & Curve
    m1_x, m1_y = right_x, 52
    svg.append(f'  <rect x="{m1_x:.1f}" y="{m1_y}" width="{col_w:.1f}" height="70" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="{m1_x + 12:.1f}" y="{m1_y + 20}" class="mono-sm">TRAIN / VAL LOSS</text>')
    svg.append(f'  <text x="{m1_x + 12:.1f}" y="{m1_y + 40}" class="mono-val" fill="{c_rose}">0.0382</text>')
    svg.append(f'  <text x="{m1_x + 76:.1f}" y="{m1_y + 40}" class="mono-sm" fill="{c_muted}">val: 0.0415</text>')
    # Mini curve 1
    pts1 = []
    for i in range(16):
        px = m1_x + col_w - 74 + (i / 15) * 62
        py = m1_y + 54 - (18 * math.exp(-i / 5.0) + math.sin(i * 0.7) * 2.0)
        pts1.append(f"{px:.1f},{py:.1f}")
    svg.append(f'  <polyline points="{" ".join(pts1)}" fill="none" stroke="url(#gLoss)" stroke-width="1.8" stroke-linecap="round"/>')

    # Metrik 2: Grad Norm
    m2_x, m2_y = right_x + col_w + 12, 52
    svg.append(f'  <rect x="{m2_x:.1f}" y="{m2_y}" width="{col_w:.1f}" height="70" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="{m2_x + 12:.1f}" y="{m2_y + 20}" class="mono-sm">GRAD NORM (||g||)</text>')
    svg.append(f'  <text x="{m2_x + 12:.1f}" y="{m2_y + 40}" class="mono-val" fill="{c_amber}">0.842</text>')
    svg.append(f'  <text x="{m2_x + 72:.1f}" y="{m2_y + 40}" class="mono-sm" fill="{c_green}">&plusmn;0.06</text>')
    pts2 = []
    for i in range(16):
        px = m2_x + col_w - 74 + (i / 15) * 62
        py = m2_y + 46 - (6 * math.sin(i * 0.6) + 4 * math.cos(i * 1.3))
        pts2.append(f"{px:.1f},{py:.1f}")
    svg.append(f'  <polyline points="{" ".join(pts2)}" fill="none" stroke="url(#gGrad)" stroke-width="1.8" stroke-linecap="round"/>')

    # Metrik 3: Perplexity / Error
    m3_x, m3_y = right_x, 134
    svg.append(f'  <rect x="{m3_x:.1f}" y="{m3_y}" width="{col_w:.1f}" height="70" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="{m3_x + 12:.1f}" y="{m3_y + 20}" class="mono-sm">PERPLEXITY (PPL)</text>')
    svg.append(f'  <text x="{m3_x + 12:.1f}" y="{m3_y + 40}" class="mono-val" fill="{c_cyan}">1.041</text>')
    svg.append(f'  <text x="{m3_x + 68:.1f}" y="{m3_y + 40}" class="mono-sm" fill="{c_muted}">optimal</text>')
    pts3 = []
    for i in range(16):
        px = m3_x + col_w - 74 + (i / 15) * 62
        py = m3_y + 54 - (14 * math.exp(-i / 7.0) + math.sin(i) * 1.2)
        pts3.append(f"{px:.1f},{py:.1f}")
    svg.append(f'  <polyline points="{" ".join(pts3)}" fill="none" stroke="{c_cyan}" stroke-width="1.8" stroke-linecap="round"/>')

    # Metrik 4: Bit Error Rate (RS Codec FEC)
    m4_x, m4_y = right_x + col_w + 12, 134
    svg.append(f'  <rect x="{m4_x:.1f}" y="{m4_y}" width="{col_w:.1f}" height="70" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="{m4_x + 12:.1f}" y="{m4_y + 20}" class="mono-sm">BER (POST-FEC)</text>')
    svg.append(f'  <text x="{m4_x + 12:.1f}" y="{m4_y + 40}" class="mono-val" fill="{c_green}">0.00e0</text>')
    svg.append(f'  <text x="{m4_x + 82:.1f}" y="{m4_y + 40}" class="mono-sm" fill="{c_green}">0 err / 48B</text>')
    pts4 = []
    for i in range(16):
        px = m4_x + col_w - 74 + (i / 15) * 62
        py = m4_y + 50 - (2.5 if i < 6 else 0.5)
        pts4.append(f"{px:.1f},{py:.1f}")
    svg.append(f'  <polyline points="{" ".join(pts4)}" fill="none" stroke="{c_green}" stroke-width="1.8" stroke-linecap="round"/>')

    # --- ALT: CONSOLE LOGS & CHECKPOINTS ---
    b_y = 216
    b_w = width - 32
    svg.append(f'  <rect x="16" y="{b_y}" width="{b_w}" height="128" rx="8" fill="{c_card}" stroke="{c_border}" stroke-width="1"/>')
    svg.append(f'  <text x="30" y="{b_y + 22}" class="mono-title">ENGINE STDOUT & CHECKPOINTS</text>')
    svg.append(f'  <text x="{width - 30}" y="{b_y + 22}" text-anchor="end" class="mono-sm" fill="{c_blue}">AUTOSAVE: ON (step_every=500)</text>')
    svg.append(f'  <line x1="16" y1="{b_y + 32}" x2="{width - 16}" y2="{b_y + 32}" stroke="{c_border}" stroke-width="0.8"/>')

    logs = [
        ("[14:22:04]", "INFO", c_blue,  "Initialized 1D-CNN backbone (kernel=3, channels=[32, 64, 128]) - ONNX WebGPU runtime locked"),
        ("[14:22:18]", "STEP", c_amber, "Forward-backward pass: 96 APSK symbols decoded; cross-entropy loss converged below 0.040"),
        ("[14:22:32]", "FEC",  c_green, "Reed-Solomon RS(48,40) Galois 256 syndrome check cleared: 0 corrupted bytes, payload valid"),
        ("[14:22:49]", "SAVE", c_cyan,  "Checkpoint exported: model_v1_converged.onnx (FP32 | 148 KB) -> deployed to tturkayy.github.io")
    ]

    for idx, (timestamp, tag, tag_color, msg) in enumerate(logs):
        ly = b_y + 52 + idx * 19
        svg.append(f'  <text x="30" y="{ly}" class="mono-sm" fill="{c_muted}">{timestamp}</text>')
        svg.append(f'  <rect x="94" y="{ly - 10}" width="38" height="13" rx="3" fill="{tag_color}" fill-opacity="0.12"/>')
        svg.append(f'  <text x="113" y="{ly}" text-anchor="middle" class="tag" fill="{tag_color}">{tag}</text>')
        svg.append(f'  <text x="142" y="{ly}" class="mono" fill="{c_text}">{msg}</text>')

    svg.append('</svg>')

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated neural dashboard at {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_svg()
