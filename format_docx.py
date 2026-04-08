import re
from copy import deepcopy
from docx import Document
from docx.shared import Pt, Cm, Emu, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INPUT = "docs/论文修改.docx"
OUTPUT = "docs/论文修改.docx"

FONT_SONG = "宋体"
FONT_HEI = "黑体"
FONT_TNR = "Times New Roman"

PT_ERHAO = Pt(22)
PT_XIAOER = Pt(18)
PT_XIAOSAN = Pt(15)
PT_SIHAO = Pt(14)
PT_XIAOSI = Pt(12)
PT_WUHAO = Pt(10.5)
FIXED_25 = Pt(25)

CHAPTER_TITLES = {
    "第一章 绪论", "第二章 相关技术及方法", "第三章 系统需求分析",
    "第四章 系统详细设计与实现", "第五章 系统测试", "第六章 总结与展望",
}

SECTION_RE = re.compile(r"^([1-6])\.([0-9]+)\s+\S")
SUBSECTION_RE = re.compile(r"^([1-6])\.([0-9]+)\.([0-9]+)\s+\S")


def is_section_heading(text):
    if not SECTION_RE.match(text):
        return False
    words = text.split(None, 1)
    if len(words) < 2:
        return False
    rest = words[1]
    if rest[0].isdigit():
        return False
    if "节" in rest[:4] and any(kw in rest for kw in ("梳理", "描述", "列出", "按功能", "指出")):
        return False
    return True


def is_subsection_heading(text):
    return bool(SUBSECTION_RE.match(text))


def set_run_font(run, cn_font, en_font, size, bold=False):
    run.font.size = size
    run.font.bold = bold
    run.font.name = en_font
    rPr = run._element.find(qn("w:rPr"))
    if rPr is None:
        rPr = run._element.makeelement(qn("w:rPr"), {})
        run._element.insert(0, rPr)
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), en_font)
    rFonts.set(qn("w:hAnsi"), en_font)
    rFonts.set(qn("w:eastAsia"), cn_font)


def set_pf(para, align, line_spacing=1.5, indent_cm=None,
           space_before=None, space_after=None, fixed_line=None):
    pf = para.paragraph_format
    pf.alignment = align
    if fixed_line:
        pf.line_spacing = fixed_line
        pf.line_spacing_rule = 4  # EXACTLY
    else:
        pf.line_spacing = line_spacing
    pf.first_line_indent = Cm(indent_cm) if indent_cm else None
    pf.space_before = space_before if space_before else Pt(0)
    pf.space_after = space_after if space_after else Pt(0)


def fmt_runs(para, cn, en, size, bold=False):
    for run in para.runs:
        set_run_font(run, cn, en, size, bold)


def ensure_runs(para, cn, en, size, bold=False):
    if not para.runs:
        para.add_run(para.text)
    fmt_runs(para, cn, en, size, bold)


def is_figure_line(text):
    return bool(re.match(r"^图\s*[0-9]+-[0-9]+", text))


def is_table_caption(text):
    return bool(re.match(r"^表\s*[0-9]+-[0-9]+", text))


def is_ref_entry(text):
    return bool(re.match(r"^\[[0-9]+\]", text))


# ── Build TOC XML (field-based, updates on open in Word) ──
def make_toc_paragraph():
    p = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "left")
    pPr.append(jc)
    p.append(pPr)

    r1 = OxmlElement("w:r")
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    r1.append(fldChar1)
    p.append(r1)

    r2 = OxmlElement("w:r")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    r2.append(instrText)
    p.append(r2)

    r3 = OxmlElement("w:r")
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    r3.append(fldChar2)
    p.append(r3)

    r4 = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = '【请在 Word 中右键此处，选择"更新域"以生成目录】'
    r4.append(t)
    p.append(r4)

    r5 = OxmlElement("w:r")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    r5.append(fldChar3)
    p.append(r5)

    return p


def add_page_break_para(body, before_element):
    p = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    p.append(pPr)
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    p.append(r)
    body.insert(list(body).index(before_element), p)
    return p


# ── Load document ──
doc = Document(INPUT)
body = doc.element.body

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()

    # F1: Chinese title
    if i == 0 and "基于微服务架构" in text:
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(22), space_after=Pt(44))
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_ERHAO, bold=True)
        continue

    # F3: "摘 要"
    if text == "摘 要":
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(22))
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_XIAOER, bold=True)
        continue

    # F7: English title
    if text.startswith("Design and Implementation"):
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(22), space_after=Pt(44))
        ensure_runs(para, FONT_TNR, FONT_TNR, PT_ERHAO, bold=True)
        continue

    # F8: "ABSTRACT"
    if text == "ABSTRACT":
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(22))
        ensure_runs(para, FONT_TNR, FONT_TNR, PT_XIAOER, bold=True)
        continue

    # F5/F6: keywords CN
    if text.startswith("关键词") or text.startswith("**关键词"):
        set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=0.85)
        for run in para.runs:
            if "关键词" in run.text:
                set_run_font(run, FONT_HEI, FONT_TNR, PT_XIAOSI, bold=True)
            else:
                set_run_font(run, FONT_SONG, FONT_TNR, PT_XIAOSI)
        continue

    # F10: Key Words EN
    if text.startswith("Key Words") or text.startswith("**Key Words"):
        set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=1.69)
        fmt_runs(para, FONT_TNR, FONT_TNR, PT_XIAOSI)
        continue

    # F13: Chapter titles
    if text in CHAPTER_TITLES:
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER)
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_XIAOER, bold=True)
        continue

    # F20: "参 考 文 献"
    if text == "参 考 文 献":
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER)
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_XIAOER, bold=True)
        continue

    # F22: "致 谢"
    if text == "致谢" or text == "致 谢":
        para.clear()
        run = para.add_run("致 谢")
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER)
        set_run_font(run, FONT_HEI, FONT_TNR, PT_XIAOER, bold=True)
        continue

    # F14: Section headings (二级标题)
    if is_section_heading(text):
        set_pf(para, WD_ALIGN_PARAGRAPH.LEFT)
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_XIAOSAN, bold=True)
        continue

    # F15: Subsection headings (三级标题) - check if any exist
    if is_subsection_heading(text):
        set_pf(para, WD_ALIGN_PARAGRAPH.LEFT)
        ensure_runs(para, FONT_HEI, FONT_TNR, PT_SIHAO, bold=True)
        continue

    # F21: Reference entries
    if is_ref_entry(text):
        set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY)
        fmt_runs(para, FONT_SONG, FONT_TNR, PT_WUHAO)
        continue

    # F17: Figure captions
    if is_figure_line(text):
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER)
        ensure_runs(para, FONT_SONG, FONT_TNR, PT_WUHAO, bold=False)
        continue

    # F18: Table captions (above table)
    if is_table_caption(text):
        set_pf(para, WD_ALIGN_PARAGRAPH.CENTER)
        ensure_runs(para, FONT_SONG, FONT_TNR, PT_WUHAO, bold=False)
        continue

    # Empty paragraphs
    if text == "":
        continue

    # F4: Chinese abstract (paragraph index 2)
    if i == 2:
        set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=0.85)
        fmt_runs(para, FONT_SONG, FONT_TNR, PT_XIAOSI)
        continue

    # F9: English abstract (paragraph index 6)
    if i == 6:
        set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=1.69)
        fmt_runs(para, FONT_TNR, FONT_TNR, PT_XIAOSI)
        continue

    # F16: Normal body text
    set_pf(para, WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=0.85)
    fmt_runs(para, FONT_SONG, FONT_TNR, PT_XIAOSI)

# F19: Table content formatting
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                set_pf(para, WD_ALIGN_PARAGRAPH.CENTER, indent_cm=None)
                fmt_runs(para, FONT_SONG, FONT_TNR, PT_WUHAO)

# ── Insert TOC page after Key Words (English) ──
# Find the Key Words paragraph, then insert: page break + "目 录" heading + TOC field + page break
kw_idx = None
for i, para in enumerate(doc.paragraphs):
    if para.text.strip().startswith("Key Words"):
        kw_idx = i
        break

if kw_idx is not None:
    kw_element = doc.paragraphs[kw_idx]._element
    next_element = kw_element.getnext()

    # Page break before TOC
    pb1 = OxmlElement("w:p")
    pb1_r = OxmlElement("w:r")
    pb1_br = OxmlElement("w:br")
    pb1_br.set(qn("w:type"), "page")
    pb1_r.append(pb1_br)
    pb1.append(pb1_r)
    kw_element.addnext(pb1)

    # "目 录" heading
    toc_title = OxmlElement("w:p")
    toc_pPr = OxmlElement("w:pPr")
    toc_jc = OxmlElement("w:jc")
    toc_jc.set(qn("w:val"), "center")
    toc_pPr.append(toc_jc)
    toc_spacing = OxmlElement("w:spacing")
    toc_spacing.set(qn("w:after"), str(int(Pt(22))))
    toc_pPr.append(toc_spacing)
    toc_title.append(toc_pPr)
    toc_r = OxmlElement("w:r")
    toc_rPr = OxmlElement("w:rPr")
    toc_b = OxmlElement("w:b")
    toc_rPr.append(toc_b)
    toc_sz = OxmlElement("w:sz")
    toc_sz.set(qn("w:val"), "36")  # 18pt = 36 half-pt = 小二号
    toc_rPr.append(toc_sz)
    toc_szCs = OxmlElement("w:szCs")
    toc_szCs.set(qn("w:val"), "36")
    toc_rPr.append(toc_szCs)
    toc_rFonts = OxmlElement("w:rFonts")
    toc_rFonts.set(qn("w:eastAsia"), FONT_HEI)
    toc_rFonts.set(qn("w:ascii"), FONT_TNR)
    toc_rFonts.set(qn("w:hAnsi"), FONT_TNR)
    toc_rPr.append(toc_rFonts)
    toc_r.append(toc_rPr)
    toc_t = OxmlElement("w:t")
    toc_t.text = "目 录"
    toc_r.append(toc_t)
    toc_title.append(toc_r)
    pb1.addnext(toc_title)

    # TOC field
    toc_field = make_toc_paragraph()
    toc_title.addnext(toc_field)

    # Page break after TOC (before chapter 1)
    pb2 = OxmlElement("w:p")
    pb2_r = OxmlElement("w:r")
    pb2_br = OxmlElement("w:br")
    pb2_br.set(qn("w:type"), "page")
    pb2_r.append(pb2_br)
    pb2.append(pb2_r)
    toc_field.addnext(pb2)

doc.save(OUTPUT)
print(f"Saved to {OUTPUT}")
print(f"Total paragraphs: {len(doc.paragraphs)}")
