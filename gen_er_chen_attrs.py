# -*- coding: utf-8 -*-
"""Generate Chen ER diagram with attributes as ovals, PK underlined."""

ENTITIES = {
    "e1": {
        "name": "user_account", "x": 450, "y": 50,
        "attrs": [
            ("id", True), ("username", False), ("password", False),
            ("nickname", False), ("created_at", False), ("updated_at", False)
        ],
        "attr_base_x": 700, "attr_base_y": -60, "attr_dy": 48
    },
    "e2": {
        "name": "forum_section", "x": 50, "y": 50,
        "attrs": [
            ("id", True), ("name", False), ("description", False),
            ("sort_order", False), ("enabled", False)
        ],
        "attr_base_x": -170, "attr_base_y": -50, "attr_dy": 48
    },
    "e3": {
        "name": "forum_post", "x": 330, "y": 340,
        "attrs": [
            ("id", True), ("title", False), ("content", False),
            ("author_id", False), ("author_name", False),
            ("section_id", False), ("section_name", False),
            ("like_count", False), ("created_at", False), ("updated_at", False)
        ],
        "attr_base_x": 30, "attr_base_y": 400, "attr_dy": 42
    },
    "e4": {
        "name": "post_comment", "x": 330, "y": 820,
        "attrs": [
            ("id", True), ("post_id", False), ("user_id", False),
            ("username", False), ("content", False),
            ("parent_comment_id", False), ("created_at", False), ("updated_at", False)
        ],
        "attr_base_x": 30, "attr_base_y": 880, "attr_dy": 42
    },
    "e5": {
        "name": "notification_message", "x": 800, "y": 340,
        "attrs": [
            ("id", True), ("type", False), ("user_id", False),
            ("title", False), ("content", False),
            ("is_read", False), ("created_at", False)
        ],
        "attr_base_x": 1050, "attr_base_y": 260, "attr_dy": 44
    },
}

RELS = [
    ("r1", "\u53d1\u5e03", 340, 180, "#fff2cc", "#d6b656", "e1", "e3", "1", "N", False),
    ("r2", "\u5f52\u5c5e", 140, 200, "#fff2cc", "#d6b656", "e2", "e3", "1", "N", False),
    ("r6", "\u70b9\u8d5e", 530, 180, "#f8cecc", "#b85450", "e1", "e3", "M", "N", True),
    ("r7", "\u63a5\u6536", 740, 160, "#fff2cc", "#d6b656", "e1", "e5", "1", "N", False),
    ("r3", "\u64b0\u5199", 640, 600, "#fff2cc", "#d6b656", "e1", "e4", "1", "N", False),
    ("r4", "\u8bc4\u8bba", 380, 600, "#fff2cc", "#d6b656", "e3", "e4", "1", "N", False),
    ("r5", "\u56de\u590d", 150, 920, "#fff2cc", "#d6b656", "e4", "e4", "1", "N", False),
]

lines = []
lines.append('<mxfile>')
lines.append('  <diagram name="ER-Chen" id="er-chen-full">')
lines.append('    <mxGraphModel dx="1400" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1300" math="0" shadow="0">')
lines.append('      <root>')
lines.append('        <mxCell id="0"/>')
lines.append('        <mxCell id="1" parent="0"/>')

cell_id = 100

for eid, edata in ENTITIES.items():
    name = edata["name"]
    ex, ey = edata["x"], edata["y"]
    lines.append(f'        <mxCell id="{eid}" value="&lt;b&gt;{name}&lt;/b&gt;" '
                 f'style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" '
                 f'vertex="1" parent="1">')
    lines.append(f'          <mxGeometry x="{ex}" y="{ey}" width="180" height="50" as="geometry"/>')
    lines.append(f'        </mxCell>')

    ax = edata["attr_base_x"]
    ay = edata["attr_base_y"]
    dy = edata["attr_dy"]

    for i, (attr_name, is_pk) in enumerate(edata["attrs"]):
        aid = f"a{cell_id}"
        eid_edge = f"ae{cell_id}"
        cell_id += 1

        if is_pk:
            label = f"&lt;u&gt;{attr_name}&lt;/u&gt;"
        else:
            label = attr_name

        ox = ax
        oy = ay + i * dy

        lines.append(f'        <mxCell id="{aid}" value="{label}" '
                     f'style="ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;" '
                     f'vertex="1" parent="1">')
        lines.append(f'          <mxGeometry x="{ox}" y="{oy}" width="110" height="36" as="geometry"/>')
        lines.append(f'        </mxCell>')

        lines.append(f'        <mxCell id="{eid_edge}" style="endArrow=none;strokeColor=#999999;" '
                     f'edge="1" source="{eid}" target="{aid}" parent="1">')
        lines.append(f'          <mxGeometry relative="1" as="geometry"/>')
        lines.append(f'        </mxCell>')

for rid, rname, rx, ry, fill, stroke, src, tgt, card_s, card_t, is_mn in RELS:
    extra = ""
    if is_mn:
        rname_display = f"&lt;b&gt;{rname}&lt;/b&gt;&lt;br&gt;&lt;font style=&amp;quot;font-size:10px&amp;quot;&gt;(M:N)&lt;/font&gt;"
    else:
        rname_display = f"&lt;b&gt;{rname}&lt;/b&gt;"

    lines.append(f'        <mxCell id="{rid}" value="{rname_display}" '
                 f'style="rhombus;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=12;" '
                 f'vertex="1" parent="1">')
    lines.append(f'          <mxGeometry x="{rx}" y="{ry}" width="90" height="70" as="geometry"/>')
    lines.append(f'        </mxCell>')

    fc = "#b85450" if is_mn else "#000000"

    edge_a = f"{rid}_ea"
    edge_b = f"{rid}_eb"

    src_exit = ""
    if rid == "r3":
        src_exit = "exitX=1;exitY=1;"
    if rid == "r5":
        src_exit = "exitX=0;exitY=1;"

    lines.append(f'        <mxCell id="{edge_a}" style="endArrow=none;{src_exit}" '
                 f'edge="1" source="{src}" target="{rid}" parent="1">')
    lines.append(f'          <mxGeometry relative="1" as="geometry"/>')
    lines.append(f'        </mxCell>')
    lines.append(f'        <mxCell id="{edge_a}_lbl" value="{card_s}" '
                 f'style="edgeLabel;html=1;fontSize=12;fontStyle=1;fontColor={fc};" '
                 f'vertex="1" connectable="0" parent="{edge_a}">')
    lines.append(f'          <mxGeometry x="-0.3" relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>')
    lines.append(f'        </mxCell>')

    tgt_entry = ""
    if rid == "r5":
        tgt_entry = "entryX=0;entryY=0.75;"

    lines.append(f'        <mxCell id="{edge_b}" style="endArrow=none;{tgt_entry}" '
                 f'edge="1" source="{rid}" target="{tgt}" parent="1">')
    lines.append(f'          <mxGeometry relative="1" as="geometry"/>')
    lines.append(f'        </mxCell>')
    lines.append(f'        <mxCell id="{edge_b}_lbl" value="{card_t}" '
                 f'style="edgeLabel;html=1;fontSize=12;fontStyle=1;fontColor={fc};" '
                 f'vertex="1" connectable="0" parent="{edge_b}">')
    lines.append(f'          <mxGeometry x="0.3" relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>')
    lines.append(f'        </mxCell>')

lines.append('      </root>')
lines.append('    </mxGraphModel>')
lines.append('  </diagram>')
lines.append('</mxfile>')

output = "\n".join(lines)
with open("docs/diagrams/fig4-4-er-chen.drawio", "w", encoding="utf-8") as f:
    f.write(output)

attr_count = sum(len(e["attrs"]) for e in ENTITIES.values())
print(f"Generated Chen ER with {len(ENTITIES)} entities, {attr_count} attribute ovals, {len(RELS)} relationships")
