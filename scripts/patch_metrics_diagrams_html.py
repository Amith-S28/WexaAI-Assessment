import base64
from pathlib import Path

def get_base64(path):
    p = Path(path)
    if not p.exists():
        p = Path("Local Run") / path
    with open(p, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

html_path = Path('benchmark-metrics-diagrams.html')
content = html_path.read_text(encoding='utf-8')

replacements = {
    'src="assets/jitter_tail_latency_comparison.png"': f'src="{get_base64("assets/jitter_tail_latency_comparison.png")}"',
    'src="assets/concurrency_speedup_factor.png"': f'src="{get_base64("assets/concurrency_speedup_factor.png")}"',
    'src="assets/radar_performance_profile.png"': f'src="{get_base64("assets/radar_performance_profile.png")}"',
    'src="assets/architectural_tradeoff_quadrant.png"': f'src="{get_base64("assets/architectural_tradeoff_quadrant.png")}"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

html_path.write_text(content, encoding='utf-8')
print('Embedded base64 images into benchmark-metrics-diagrams.html successfully!')
