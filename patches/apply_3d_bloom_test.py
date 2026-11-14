#!/usr/bin/env python3
"""Safe diagnostic patch: keep the complete Qt3D frame graph intact but omit
only the bloom contribution in the final gamma-correction shader.

The bloom render passes remain present. This is deliberately a visual-only
bypass to verify that the main deferred scene renders correctly before trying
a more invasive performance optimization.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
gamma_frag = root / "qmlui/qml/fixturesfunctions/3DView/shaders/gamma_correct.frag"

s = gamma_frag.read_text()
needle = '    hdrColor += 0.5 * SAMPLE_TEX2D(bloomTex, fsUv).rgb;\n'
assert s.count(needle) == 1, "gamma_correct.frag bloom sample anchor changed"
s = s.replace(needle, '    // Diagnostic: omit bloom contribution; preserve all render passes.\n', 1)
gamma_frag.write_text(s)

print("Applied safe bloom-visual bypass; Qt3D frame graph remains unchanged.")
