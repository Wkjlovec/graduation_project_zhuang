# -*- coding: utf-8 -*-
"""Convert all .mmd files to .drawio files with embedded PNG."""
import os
import subprocess
import base64
import glob

DIAGRAMS_DIR = "docs/diagrams"
TEMPLATE = '''<mxfile>
  <diagram name="{name}" id="{diagram_id}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/png,{b64};" vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="{w}" height="{h}" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

mmd_files = sorted(glob.glob(os.path.join(DIAGRAMS_DIR, "*.mmd")))
skip = {"fig4-4-er-chen.mmd", "fig4-4-er-diagram.mmd"}

converted = 0
for mmd_path in mmd_files:
    basename = os.path.basename(mmd_path)
    name = os.path.splitext(basename)[0]
    drawio_path = os.path.join(DIAGRAMS_DIR, name + ".drawio")
    png_path = os.path.join(DIAGRAMS_DIR, name + ".png")

    if basename in skip:
        print(f"  SKIP {basename} (has dedicated drawio)")
        continue

    if os.path.exists(drawio_path):
        print(f"  EXISTS {drawio_path}")
        continue

    if not os.path.exists(png_path):
        print(f"  Generating PNG for {basename}...")
        result = subprocess.run(
            ["mmdc", "-i", mmd_path, "-o", png_path,
             "-w", "1200", "-H", "900", "--backgroundColor", "white"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  ERROR generating PNG: {result.stderr}")
            continue

    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    from PIL import Image
    try:
        img = Image.open(png_path)
        w, h = img.size
        scale = min(1100 / w, 780 / h, 1.0)
        w = int(w * scale)
        h = int(h * scale)
    except Exception:
        w, h = 800, 600

    xml = TEMPLATE.format(
        name=name,
        diagram_id=f"diag-{name}",
        b64=b64,
        w=w,
        h=h
    )

    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(xml)

    converted += 1
    print(f"  OK {drawio_path} ({w}x{h})")

print(f"\nConverted {converted} files. Chen ER drawio created separately.")
