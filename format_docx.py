import re
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

INPUT = "docs/论文修改.docx"
OUTPUT = "docs/论文修改.docx"

FONT_CN_SONG = "宋体"
FONT_CN_HEI = "黑体"
FONT_EN = "Times New Roman"

PT_XIAOER = Pt(18)
PT_XIAOSAN = Pt(15)
PT_XIAOSI = Pt(12)
PT_WUHAO = Pt(10.5)
PT_ERHAO = Pt(22)

LINE_SPACING_1_5 = 1.5

CHAPTER_TITLES = {"第一章 绪论", "第二章 相关技术及方法", "第三章 系统需求分析",
                  "第四章 系统详细设计与实现", "第五章 系统测试", "第六章 总结与展望"}

SECTION_HEADING_RE = re.compile(r"^[1-6]\.[0-9]+\s+\S")

BODY_START_WITH_SECTION_RE = re.compile(
    r"^[0-9]+\.[0-9]+\s+节|^[0-9]+\.[0-9]+\s+节")


def is_section_heading(text):
    if not SECTION_HEADING_RE.match(text):
        return False
    words = text.split(None, 1)
    if len(words) < 2:
        return False
    label = words[0]
    rest = words[1]
    if rest[0].isdigit():
        return False
    if "节" in rest[:3] and ("梳理" in rest or "描述" in rest or "列出" in rest
                            or "按功能" in rest or "指出" in rest):
        return False
    return True


def set_run_font(run, font_name_cn, font_name_en, size, bold=False):
    run.font.size = size
    run.font.bold = bold
    run.font.name = font_name_en
    r = run._element
    rPr = r.find(qn("w:rPr"))
    if rPr is None:
        rPr = r.makeelement(qn("w:rPr"), {})
        r.insert(0, rPr)
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name_en)
    rFonts.set(qn("w:hAnsi"), font_name_en)
    rFonts.set(qn("w:eastAsia"), font_name_cn)


def set_paragraph_format(para, alignment, line_spacing, first_line_indent=None,
                         space_before=None, space_after=None):
    pf = para.paragraph_format
    pf.alignment = alignment
    pf.line_spacing = line_spacing
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent
    else:
        pf.first_line_indent = None
    if space_before is not None:
        pf.space_before = space_before
    else:
        pf.space_before = Pt(0)
    if space_after is not None:
        pf.space_after = space_after
    else:
        pf.space_after = Pt(0)


def format_all_runs(para, font_cn, font_en, size, bold=False):
    for run in para.runs:
        set_run_font(run, font_cn, font_en, size, bold)


def ensure_single_run(para, font_cn, font_en, size, bold=False):
    if not para.runs:
        run = para.add_run(para.text)
    for run in para.runs:
        set_run_font(run, font_cn, font_en, size, bold)


def is_table_row(text):
    return text.strip().startswith("|")


def is_figure_placeholder(text):
    t = text.strip()
    return re.match(r"^图\s*[0-9]+-[0-9]+", t) is not None


def is_table_caption(text):
    t = text.strip()
    return re.match(r"^表\s*[0-9]+-[0-9]+", t) is not None


def is_reference_entry(text):
    t = text.strip()
    return re.match(r"^\[[0-9]+\]", t) is not None


doc = Document(INPUT)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()

    if i == 0 and "基于微服务架构" in text:
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5,
                             space_before=Pt(22), space_after=Pt(44))
        ensure_single_run(para, FONT_CN_HEI, FONT_EN, PT_ERHAO, bold=True)
        continue

    if text == "摘 要":
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5,
                             space_after=Pt(22))
        ensure_single_run(para, FONT_CN_HEI, FONT_EN, PT_XIAOER, bold=True)
        continue

    if text.startswith("Design and Implementation"):
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5,
                             space_before=Pt(22), space_after=Pt(44))
        ensure_single_run(para, FONT_EN, FONT_EN, PT_ERHAO, bold=True)
        continue

    if text == "ABSTRACT":
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5,
                             space_after=Pt(22))
        ensure_single_run(para, FONT_EN, FONT_EN, PT_XIAOER, bold=True)
        continue

    if text.startswith("关键词：") or text.startswith("**关键词："):
        real_text = text.replace("**", "").strip()
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.JUSTIFY, LINE_SPACING_1_5,
                             first_line_indent=Cm(0.85))
        for run in para.runs:
            run_text = run.text
            if "关键词" in run_text:
                set_run_font(run, FONT_CN_HEI, FONT_EN, PT_XIAOSI, bold=True)
                run.bold = True
            else:
                set_run_font(run, FONT_CN_SONG, FONT_EN, PT_XIAOSI, bold=False)
        continue

    if text.startswith("Key Words:") or text.startswith("**Key Words:"):
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.JUSTIFY, LINE_SPACING_1_5,
                             first_line_indent=Emu(Pt(12).emu * 4))
        for run in para.runs:
            set_run_font(run, FONT_EN, FONT_EN, PT_XIAOSI, bold=False)
        continue

    if text in CHAPTER_TITLES:
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5)
        ensure_single_run(para, FONT_CN_HEI, FONT_EN, PT_XIAOER, bold=True)
        continue

    if text == "参 考 文 献":
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5)
        ensure_single_run(para, FONT_CN_HEI, FONT_EN, PT_XIAOER, bold=True)
        continue

    if text == "致谢" or text == "致 谢":
        para.clear()
        run = para.add_run("致 谢")
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5)
        set_run_font(run, FONT_CN_HEI, FONT_EN, PT_XIAOER, bold=True)
        continue

    if is_section_heading(text):
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.LEFT, LINE_SPACING_1_5,
                             first_line_indent=None)
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        ensure_single_run(para, FONT_CN_HEI, FONT_EN, PT_XIAOSAN, bold=True)
        continue

    if is_reference_entry(text):
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.JUSTIFY, LINE_SPACING_1_5,
                             first_line_indent=None)
        format_all_runs(para, FONT_CN_SONG, FONT_EN, PT_WUHAO)
        continue

    if text == "(empty)" or text == "":
        continue

    if is_figure_placeholder(text) or is_table_caption(text):
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER, LINE_SPACING_1_5)
        format_all_runs(para, FONT_CN_SONG, FONT_EN, PT_WUHAO, bold=True)
        continue

    if i in (2, 6):
        indent = Cm(0.85) if i == 2 else Emu(Pt(12).emu * 4)
        set_paragraph_format(para, WD_ALIGN_PARAGRAPH.JUSTIFY, LINE_SPACING_1_5,
                             first_line_indent=indent)
        font_cn = FONT_CN_SONG if i == 2 else FONT_EN
        format_all_runs(para, font_cn, FONT_EN, PT_XIAOSI)
        continue

    set_paragraph_format(para, WD_ALIGN_PARAGRAPH.JUSTIFY, LINE_SPACING_1_5,
                         first_line_indent=Cm(0.85))
    format_all_runs(para, FONT_CN_SONG, FONT_EN, PT_XIAOSI)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                set_paragraph_format(para, WD_ALIGN_PARAGRAPH.CENTER,
                                     LINE_SPACING_1_5, first_line_indent=None)
                format_all_runs(para, FONT_CN_SONG, FONT_EN, PT_WUHAO)

doc.save(OUTPUT)
print(f"Saved formatted document to {OUTPUT}")
