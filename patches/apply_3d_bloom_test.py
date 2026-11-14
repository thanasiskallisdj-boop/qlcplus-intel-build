#!/usr/bin/env python3
"""Temporary diagnostic patch: bypass the 3D bloom post-processing chain.

This keeps the normal renderer intact and disables only the bloom extraction,
downsample and upsample passes. It is intended to measure whether those nine
full-screen passes are a major contributor to Qt3D frame blocking.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
view = root / "qmlui/qml/fixturesfunctions/3DView/3DView.qml"
gamma_qml = root / "qmlui/qml/fixturesfunctions/3DView/GammaCorrectFilter.qml"
gamma_frag = root / "qmlui/qml/fixturesfunctions/3DView/shaders/gamma_correct.frag"

s = view.read_text()
needle = '    property string contextName: "3D"\n'
assert s.count(needle) == 1, "3DView.qml contextName anchor changed"
s = s.replace(needle, needle + '    // Temporary diagnostic build: disable the bloom post-processing chain.\n    readonly property bool bloomEnabled: false\n', 1)

start = '            component = Qt.createComponent("GrabBrightFilter.qml");\n'
end = '            component = Qt.createComponent("DirectionalLightFilter.qml");\n'
assert s.count(start) == 1 and s.count(end) == 1, "3DView.qml bloom block anchors changed"
s = s.replace(start, '            if (bloomEnabled)\n            {\n' + start, 1)
s = s.replace(end, '            } // bloomEnabled\n\n' + end, 1)

gamma_create = '                "bloomTexture": texChainTextures[0],\n'
assert s.count(gamma_create) == 1, "3DView.qml gamma filter anchor changed"
s = s.replace(gamma_create, gamma_create + '                "bloomEnabled": bloomEnabled,\n', 1)
view.write_text(s)

s = gamma_qml.read_text()
needle = '    property Texture2D bloomTexture: null\n'
assert s.count(needle) == 1, "GammaCorrectFilter.qml bloomTexture anchor changed"
s = s.replace(needle, needle + '    property bool bloomEnabled: true\n', 1)
needle = '        Parameter { name: "bloomTex"; value: bloomTexture }\n'
assert s.count(needle) == 1, "GammaCorrectFilter.qml bloom parameter anchor changed"
s = s.replace(needle, needle + '        Parameter { name: "bloomEnabled"; value: bloomEnabled }\n', 1)
gamma_qml.write_text(s)

s = gamma_frag.read_text()
needle = 'uniform sampler2D bloomTex;\n'
assert s.count(needle) == 1, "gamma_correct.frag bloom sampler anchor changed"
s = s.replace(needle, needle + 'uniform bool bloomEnabled;\n', 1)
needle = '    hdrColor += 0.5 * SAMPLE_TEX2D(bloomTex, fsUv).rgb;\n'
assert s.count(needle) == 1, "gamma_correct.frag bloom sample anchor changed"
s = s.replace(needle, '    if (bloomEnabled)\n        hdrColor += 0.5 * SAMPLE_TEX2D(bloomTex, fsUv).rgb;\n', 1)
gamma_frag.write_text(s)

print("Applied temporary 3D bloom bypass diagnostic patch.")
