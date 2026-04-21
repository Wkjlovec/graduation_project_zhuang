"""
毕业答辩PPT自动生成脚本
课题：微服务架构的论坛系统实现（PC + 移动端）
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

PRIMARY = RGBColor(0x1A, 0x56, 0xDB)
PRIMARY_LIGHT = RGBColor(0xE8, 0xF0, 0xFE)
ACCENT = RGBColor(0x34, 0xA8, 0x53)
DARK = RGBColor(0x20, 0x2C, 0x3C)
GRAY = RGBColor(0x5F, 0x6B, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF8, 0xF9, 0xFA)
BORDER = RGBColor(0xDE, 0xE2, 0xE6)
ORANGE = RGBColor(0xFB, 0x8C, 0x00)
RED_ACCENT = RGBColor(0xE5, 0x39, 0x35)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape_fill(slide, left, top, width, height, color, corner_radius=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    if corner_radius is not None:
        shape.adjustments[0] = corner_radius
    return shape


def add_textbox(slide, left, top, width, height, text, font_size=18,
                bold=False, color=DARK, alignment=PP_ALIGN.LEFT, font_name="微软雅黑"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_paragraph(text_frame, text, font_size=16, bold=False, color=DARK,
                  alignment=PP_ALIGN.LEFT, space_before=Pt(6), space_after=Pt(2),
                  font_name="微软雅黑", level=0):
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    p.level = level
    return p


def add_title_bar(slide, title_text, subtitle_text=None):
    bar = add_shape_fill(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(1.1), PRIMARY, 0)
    add_textbox(slide, Inches(0.8), Inches(0.15), Inches(10), Inches(0.7),
                title_text, font_size=28, bold=True, color=WHITE)
    if subtitle_text:
        add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.35),
                    subtitle_text, font_size=14, color=RGBColor(0xBB, 0xD5, 0xFD))
    page_indicator = add_textbox(slide, Inches(11.5), Inches(0.3), Inches(1.5), Inches(0.5),
                                 "", font_size=12, color=WHITE, alignment=PP_ALIGN.RIGHT)
    return bar


def add_card(slide, left, top, width, height, title, items, icon_color=PRIMARY):
    card = add_shape_fill(slide, left, top, width, height, WHITE, 0.05)
    card.shadow.inherit = False

    accent_bar = add_shape_fill(slide, left, top, Inches(0.06), height, icon_color, 0)

    add_textbox(slide, left + Inches(0.3), top + Inches(0.15), width - Inches(0.5), Inches(0.4),
                title, font_size=16, bold=True, color=icon_color)

    txBox = slide.shapes.add_textbox(left + Inches(0.3), top + Inches(0.55),
                                     width - Inches(0.5), height - Inches(0.7))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(13)
        p.font.color.rgb = DARK
        p.font.name = "微软雅黑"
        p.space_before = Pt(3)
        p.space_after = Pt(2)
    return card


def make_table(slide, left, top, width, row_height, headers, rows):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width,
                                         Emu(int(row_height * n_rows)))
    table = table_shape.table

    col_widths = [width // n_cols] * n_cols
    for i, w in enumerate(col_widths):
        table.columns[i].width = w

    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.name = "微软雅黑"
            p.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.cell(ri + 1, ci)
            cell.text = str(val)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.color.rgb = DARK
                p.font.name = "微软雅黑"
                p.alignment = PP_ALIGN.CENTER
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 == 0 else LIGHT_BG
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    return table_shape


def slide_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)

    add_shape_fill(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(3.8), PRIMARY, 0)
    add_shape_fill(slide, Inches(0), Inches(3.6), SLIDE_WIDTH, Inches(0.4),
                   RGBColor(0x13, 0x45, 0xB5), 0)

    add_textbox(slide, Inches(1.5), Inches(0.8), Inches(10), Inches(0.5),
                "毕业设计答辩", font_size=18, color=RGBColor(0xBB, 0xD5, 0xFD),
                alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(1), Inches(1.4), Inches(11), Inches(1.2),
                "基于微服务架构的论坛系统\n设计与实现", font_size=36, bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(1.5), Inches(2.7), Inches(10), Inches(0.5),
                "—— PC 端 + 移动端双端协同", font_size=18, color=RGBColor(0xBB, 0xD5, 0xFD),
                alignment=PP_ALIGN.CENTER)

    info_items = [
        "答辩人：XXX　　学号：XXXXXXXXXX",
        "指导教师：XXX 副教授",
        "专业：软件工程　　学院：计算机与信息学院",
    ]
    y = Inches(4.4)
    for item in info_items:
        add_textbox(slide, Inches(3), y, Inches(7), Inches(0.4),
                    item, font_size=16, color=GRAY, alignment=PP_ALIGN.CENTER)
        y += Inches(0.45)

    add_textbox(slide, Inches(3), Inches(6.3), Inches(7), Inches(0.4),
                "二〇二六年五月", font_size=14, color=GRAY, alignment=PP_ALIGN.CENTER)


def slide_outline(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "目 录", "CONTENTS")

    sections = [
        ("01", "研究背景与意义", "行业痛点 · 现有方案不足 · 课题创新点"),
        ("02", "需求分析与目标", "功能需求 · 非功能需求 · 技术路线"),
        ("03", "系统设计与架构", "整体架构 · 核心模块 · 技术选型"),
        ("04", "实现与关键技术", "核心功能 · 难点攻克 · 开发工具链"),
        ("05", "系统测试", "测试策略 · 回归测试 · 性能基准"),
        ("06", "总结与展望", "核心成果 · 不足 · 未来方向"),
    ]

    start_x = Inches(0.8)
    start_y = Inches(1.6)
    card_w = Inches(3.8)
    card_h = Inches(1.6)
    gap_x = Inches(0.25)
    gap_y = Inches(0.3)

    for i, (num, title, desc) in enumerate(sections):
        col = i % 3
        row = i // 3
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        card = add_shape_fill(slide, x, y, card_w, card_h, PRIMARY_LIGHT, 0.05)

        num_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.2), y + Inches(0.25),
                                            Inches(0.6), Inches(0.6))
        num_circle.fill.solid()
        num_circle.fill.fore_color.rgb = PRIMARY
        num_circle.line.fill.background()
        tf = num_circle.text_frame
        tf.paragraphs[0].text = num
        tf.paragraphs[0].font.size = Pt(20)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = WHITE
        tf.paragraphs[0].font.name = "微软雅黑"
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

        add_textbox(slide, x + Inches(1.0), y + Inches(0.3), Inches(2.5), Inches(0.4),
                    title, font_size=18, bold=True, color=PRIMARY)

        add_textbox(slide, x + Inches(0.2), y + Inches(1.0), card_w - Inches(0.4), Inches(0.5),
                    desc, font_size=12, color=GRAY)


def slide_background(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "01 研究背景与意义", "Research Background & Significance")

    add_card(slide, Inches(0.5), Inches(1.4), Inches(5.8), Inches(2.6),
             "📋 行业与社会痛点", [
                 "• 高校交流场景碎片化：教学通知分散在课程平台、班级群等多渠道",
                 "• 信息版本不一致、上下文断裂、历史结论难追溯",
                 "• AI工具普及后内容生产加速，信息密集但有效触达率低",
                 "• 传统论坛系统功能单一，工程可维护性差",
             ], PRIMARY)

    add_card(slide, Inches(6.7), Inches(1.4), Inches(5.8), Inches(2.6),
             "⚠️ 现有方案的不足", [
                 "• 单体架构 → 模块耦合高、扩展性差",
                 "• 仅PC端 → 移动端体验缺失",
                 "• 缺少统一鉴权 → 安全边界模糊",
                 "• 无自动化测试 → 交付质量不可控",
                 "• 缺乏缓存机制 → 高并发下性能瓶颈",
             ], ORANGE)

    add_card(slide, Inches(0.5), Inches(4.3), Inches(12), Inches(2.6),
             "💡 课题创新点与价值", [
                 "① 微服务架构（6个独立服务） → 松耦合、可独立部署与扩展",
                 "② PC + 移动双端协同（Vue 3 + Element Plus / Vant） → 统一API、一致体验",
                 "③ JWT + Redis会话 + 网关统一鉴权 → 完整安全闭环（登录/刷新/登出/锁定）",
                 "④ Redis缓存层 → 帖子列表缓存命中后响应提升 80%+",
                 "⑤ 可复现测试链路（回归脚本 + 缓存基准 + 一键启停） → 工程质量可验证",
             ], ACCENT)


def slide_requirements(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "02 需求分析与目标", "Requirements Analysis & Objectives")

    add_card(slide, Inches(0.5), Inches(1.4), Inches(6), Inches(3.0),
             "🔧 功能性需求", [
                 "用户管理：注册/登录/登出/个人信息/会话管理",
                 "论坛核心：分区浏览/发帖/编辑/删除/详情查看",
                 "互动功能：评论(含二级回复)/点赞(去重)/搜索",
                 "通知系统：系统公告/个人通知/标记已读",
                 "推荐模块：音乐/书籍推荐（首页展示）",
                 "双端支持：PC端 + 移动端 完整功能覆盖",
             ], PRIMARY)

    add_card(slide, Inches(6.8), Inches(1.4), Inches(6), Inches(3.0),
             "📊 非功能性需求", [
                 "性能：帖子列表缓存命中后响应 ≤ 10ms (P95)",
                 "安全：JWT双令牌 + 会话校验 + 登录失败锁定",
                 "可用性：一键启停脚本 + 健康检查验活",
                 "可测试性：自动化回归12项场景 + 缓存基准",
                 "可维护性：服务独立部署、统一接口规范",
                 "兼容性：PC浏览器 + 移动端浏览器",
             ], ACCENT)

    add_card(slide, Inches(0.5), Inches(4.7), Inches(12.3), Inches(2.3),
             "🎯 研究目标与技术路线", [
                 "目标：设计并实现一个面向高校场景的微服务论坛系统，解决信息碎片化和系统可维护性问题",
                 "技术路线：需求调研 → 架构设计（微服务拆分） → 核心服务开发 → 双端前端开发 → 缓存与安全加固 → 自动化测试与验收",
             ], PRIMARY)


def slide_architecture(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "03 系统设计与架构 — 整体架构", "System Architecture Overview")

    layers = [
        ("客户端层", Inches(1.3), PRIMARY_LIGHT, PRIMARY,
         ["PC端 (Vue3 + Element Plus)", "移动端 (Vue3 + Vant)"], Inches(3.5)),
        ("API网关层", Inches(2.55), RGBColor(0xFE, 0xF3, 0xE2), ORANGE,
         ["Spring Cloud Gateway — 统一路由 · JWT验证 · CORS · Redis会话校验"], Inches(8.5)),
        ("业务服务层", Inches(3.8), RGBColor(0xE8, 0xF5, 0xE9), ACCENT,
         ["auth-user", "forum", "notification", "media", "search"], Inches(8.5)),
        ("注册中心", Inches(5.05), RGBColor(0xF3, 0xE5, 0xF5), RGBColor(0x9C, 0x27, 0xB0),
         ["Nacos — 服务注册与发现 · 配置管理"], Inches(8.5)),
        ("数据层", Inches(6.3), RGBColor(0xE3, 0xF2, 0xFD), PRIMARY,
         ["MySQL 8.4（持久化）", "Redis 7.4（缓存 + 会话）"], Inches(8.5)),
    ]

    for name, y, bg_color, border_color, items, width in layers:
        x = Inches(2.2)
        h = Inches(1.05)
        card = add_shape_fill(slide, x, y, width, h, bg_color, 0.03)
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        add_textbox(slide, Inches(0.5), y + Inches(0.2), Inches(1.5), Inches(0.5),
                    name, font_size=13, bold=True, color=border_color, alignment=PP_ALIGN.RIGHT)

        items_text = "　｜　".join(items)
        add_textbox(slide, x + Inches(0.3), y + Inches(0.25), width - Inches(0.6), Inches(0.6),
                    items_text, font_size=13, color=DARK, alignment=PP_ALIGN.CENTER)

    for y_top in [Inches(2.35), Inches(3.55), Inches(4.8), Inches(6.05)]:
        arrow = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(6.3), y_top, Inches(0.35), Inches(0.25))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = GRAY
        arrow.line.fill.background()


def slide_architecture_modules(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "03 系统设计与架构 — 核心模块设计", "Core Module Design")

    modules = [
        ("gateway-service", "API网关", [
            "端口: 8080",
            "JWT令牌验证+Redis会话",
            "全局CORS跨域配置",
            "路由转发(lb://服务名)",
        ], PRIMARY),
        ("auth-user-service", "认证用户", [
            "端口: 8081",
            "注册/登录/刷新/登出",
            "双令牌(Access+Refresh)",
            "登录失败锁定机制",
        ], ACCENT),
        ("forum-service", "论坛核心", [
            "端口: 8082",
            "帖子/评论/点赞CRUD",
            "分区管理",
            "Redis缓存(@Cacheable)",
        ], ORANGE),
        ("notification-service", "通知服务", [
            "端口: 8083",
            "系统公告/个人通知",
            "已读标记",
            "首页通知聚合",
        ], RGBColor(0x9C, 0x27, 0xB0)),
        ("media-service", "媒体推荐", [
            "端口: 8084",
            "音乐/书籍推荐",
            "首页内容聚合",
            "类型筛选(music/book)",
        ], RGBColor(0x00, 0x97, 0xA7)),
        ("search-service", "搜索服务", [
            "端口: 8085",
            "帖子关键词搜索",
            "OpenFeign服务间调用",
            "分区+分页联合查询",
        ], RED_ACCENT),
    ]

    start_x = Inches(0.4)
    start_y = Inches(1.4)
    card_w = Inches(4.0)
    card_h = Inches(2.7)
    gap_x = Inches(0.2)
    gap_y = Inches(0.2)

    for i, (name, title, items, color) in enumerate(modules):
        col = i % 3
        row = i // 3
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        card = add_shape_fill(slide, x, y, card_w, card_h, WHITE, 0.04)
        card.line.color.rgb = BORDER
        card.line.width = Pt(1)

        header_bar = add_shape_fill(slide, x, y, card_w, Inches(0.55), color, 0.04)
        add_textbox(slide, x + Inches(0.15), y + Inches(0.08), card_w - Inches(0.3), Inches(0.4),
                    f"{title} ({name})", font_size=12, bold=True, color=WHITE)

        for j, item in enumerate(items):
            add_textbox(slide, x + Inches(0.2), y + Inches(0.65 + j * 0.45),
                        card_w - Inches(0.4), Inches(0.4),
                        f"▸ {item}", font_size=11, color=DARK)


def slide_database(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "03 系统设计与架构 — 数据库设计", "Database Design")

    tables_data = [
        ("user_account", "用户表", [
            ("id", "BIGINT", "主键, 自增"),
            ("username", "VARCHAR(50)", "唯一, 登录名"),
            ("password", "VARCHAR(255)", "BCrypt加密"),
            ("nickname", "VARCHAR(50)", "昵称"),
            ("created_at", "DATETIME", "创建时间"),
            ("updated_at", "DATETIME", "更新时间"),
        ]),
        ("forum_post", "帖子表", [
            ("id", "BIGINT", "主键, 自增"),
            ("title", "VARCHAR(200)", "帖子标题"),
            ("content", "TEXT", "帖子内容"),
            ("section_id", "BIGINT", "外键→forum_section"),
            ("author_id/name", "BIGINT/VARCHAR", "作者信息"),
            ("like_count", "INT", "点赞计数"),
        ]),
        ("post_comment", "评论表", [
            ("id", "BIGINT", "主键, 自增"),
            ("content", "TEXT", "评论内容"),
            ("post_id", "BIGINT", "外键→forum_post"),
            ("parent_id", "BIGINT", "父评论(二级)"),
            ("author_id/name", "BIGINT/VARCHAR", "评论作者"),
            ("created/updated", "DATETIME", "时间戳"),
        ]),
    ]

    x_positions = [Inches(0.3), Inches(4.5), Inches(8.7)]
    y = Inches(1.4)
    card_w = Inches(4.0)

    for idx, (table_name, display_name, fields) in enumerate(tables_data):
        x = x_positions[idx]

        header = add_shape_fill(slide, x, y, card_w, Inches(0.5), PRIMARY, 0.03)
        add_textbox(slide, x + Inches(0.1), y + Inches(0.05), card_w - Inches(0.2), Inches(0.4),
                    f"📦 {display_name} ({table_name})", font_size=13, bold=True, color=WHITE)

        for fi, (fname, ftype, fdesc) in enumerate(fields):
            fy = y + Inches(0.55 + fi * 0.38)
            row_bg = WHITE if fi % 2 == 0 else LIGHT_BG
            row = add_shape_fill(slide, x, fy, card_w, Inches(0.36), row_bg, 0)
            row.line.fill.background()
            add_textbox(slide, x + Inches(0.1), fy + Inches(0.02), Inches(1.4), Inches(0.3),
                        fname, font_size=10, bold=True, color=PRIMARY)
            add_textbox(slide, x + Inches(1.5), fy + Inches(0.02), Inches(1.1), Inches(0.3),
                        ftype, font_size=9, color=GRAY)
            add_textbox(slide, x + Inches(2.6), fy + Inches(0.02), Inches(1.3), Inches(0.3),
                        fdesc, font_size=9, color=DARK)

    other_y = Inches(4.4)
    add_card(slide, Inches(0.3), other_y, Inches(3.8), Inches(2.5),
             "📦 其他数据表", [
                 "forum_section — 论坛分区",
                 "  · id, name, description, sort_order",
                 "post_like — 点赞记录",
                 "  · id, post_id, user_id (唯一约束)",
                 "notification_message — 通知消息",
                 "  · id, title, content, type, target_user",
                 "  · is_read, created_at",
             ], PRIMARY)

    add_card(slide, Inches(4.5), other_y, Inches(4.0), Inches(2.5),
             "🔗 Redis 数据结构", [
                 "auth:session:{sessionId}",
                 "  → 用户会话信息(JWT签发校验)",
                 "auth:login:fail:{username}:{ip}",
                 "  → 登录失败计数(防暴力破解)",
                 "forum:post:list::*",
                 "  → 帖子列表缓存(TTL=2min)",
                 "forum:post:detail::*",
                 "  → 帖子详情缓存(TTL=5min)",
             ], RED_ACCENT)

    add_card(slide, Inches(8.8), other_y, Inches(4.0), Inches(2.5),
             "🔒 安全机制", [
                 "密码存储: BCrypt 单向散列",
                 "令牌: JWT Access + Refresh 双令牌",
                 "会话: Redis 集中管理, 登出即失效",
                 "网关: 统一 JWT 校验 + 路径白名单",
                 "锁定: 登录失败N次后短时锁定",
                 "权限: 帖子仅作者可编辑/删除",
             ], ACCENT)


def slide_tech_selection(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "03 系统设计与架构 — 关键技术选型", "Technology Selection")

    headers = ["技术领域", "本项目选型", "对比方案", "选型理由"]
    rows = [
        ["后端框架", "Spring Boot 3.2", "Django / Express", "Java生态成熟, Spring Cloud微服务生态完善"],
        ["微服务治理", "Spring Cloud Alibaba", "Dubbo / gRPC", "Nacos集成注册+配置, 与Gateway无缝衔接"],
        ["API网关", "Spring Cloud Gateway", "Nginx / Kong", "原生支持服务发现, 与JWT Filter深度集成"],
        ["前端框架", "Vue 3 + TypeScript", "React / Angular", "组合式API, 生态轻量, 双端复用路由设计"],
        ["PC端UI", "Element Plus", "Ant Design Vue", "组件丰富, 文档完善, 社区活跃"],
        ["移动端UI", "Vant 4", "uni-app / Ionic", "Vue3原生适配, 轻量高性能"],
        ["数据库", "MySQL 8.4", "PostgreSQL / MongoDB", "事务支持完善, 运维成本低, JPA兼容性好"],  # pragma: allowlist secret
        ["缓存", "Redis 7.4", "Memcached / Caffeine", "支持多数据结构, 兼顾会话管理与数据缓存"],
        ["认证", "JWT + Spring Security", "OAuth2 / Session", "无状态令牌+Redis会话=安全与性能兼顾"],
        ["服务注册", "Nacos 2.3", "Eureka / Consul", "支持注册发现+配置管理, 阿里生态维护活跃"],
    ]

    make_table(slide, Inches(0.4), Inches(1.4), Inches(12.5), Emu(int(Inches(0.42))),
               headers, rows)


def slide_implementation_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "04 实现与关键技术 — 认证与网关", "Authentication & Gateway Implementation")

    add_card(slide, Inches(0.4), Inches(1.4), Inches(6.2), Inches(5.5),
             "🔐 JWT 双令牌认证流程", [
                 "1. 用户提交 username + password",
                 "2. auth-service 验证 → 签发 Access Token (短期)",
                 "                     + Refresh Token (长期)",
                 "3. Redis 写入 session: auth:session:{sid}",
                 "4. 客户端携带 Bearer Token 访问受保护接口",
                 "5. Gateway JwtRelayFilter 校验:",
                 "   · JWT签名有效性 + 类型(access)",
                 "   · Redis session存在性",
                 "   · 提取 userId/username → X-User-Id/X-Username",
                 "6. 下游服务通过请求头获取用户身份",
                 "",
                 "Refresh 流程:",
                 "   · Access过期 → 前端401拦截器自动调用 /refresh",
                 "   · 验证Refresh Token → 签发新Access Token",
                 "   · 并发请求通过 pending queue 避免重复刷新",
                 "",
                 "Logout 流程:",
                 "   · 调用 /logout → Redis 删除 session",
                 "   · 网关拦截后续请求(session不存在) → 401",
             ], PRIMARY)

    add_card(slide, Inches(6.9), Inches(1.4), Inches(6.0), Inches(2.5),
             "🌐 网关路由配置", [
                 "/api/auth/**   → auth-user-service (StripPrefix=1)",
                 "/api/users/**  → auth-user-service (StripPrefix=1)",
                 "/api/forum/**  → forum-service (StripPrefix=2)",
                 "/api/notifications/** → notification-service",
                 "/api/media/**  → media-service (StripPrefix=1)",
                 "/api/search/** → search-service (StripPrefix=1)",
             ], ACCENT)

    add_card(slide, Inches(6.9), Inches(4.2), Inches(6.0), Inches(2.7),
             "🛡️ 安全策略伪代码", [
                 "function JwtRelayFilter(request):",
                 "  if path in PUBLIC_PATHS: forward()",
                 "  token = extractBearer(request)",
                 "  claims = jwt.verify(token, SECRET)",
                 "  assert claims.type == 'access'",
                 "  session = redis.get('auth:session:' + claims.sid)",
                 "  assert session != null",
                 "  request.addHeader('X-User-Id', claims.uid)",
                 "  forward(request)",
             ], RED_ACCENT)


def slide_implementation_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "04 实现与关键技术 — 论坛核心与缓存", "Forum Core & Cache Implementation")

    add_card(slide, Inches(0.4), Inches(1.4), Inches(6.2), Inches(3.0),
             "📝 论坛核心功能伪代码", [
                 "// 发帖流程",
                 "function createPost(request, user):",
                 "  validate(request.title, request.content)",
                 "  section = sectionRepo.findById(request.sectionId)",
                 "  post = new ForumPost(title, content, section, user)",
                 "  postRepo.save(post)",
                 "  cacheEvict('forum:post:list')  // 清除列表缓存",
                 "  return post",
                 "",
                 "// 二级评论",
                 "function addComment(postId, request, user):",
                 "  post = postRepo.findById(postId)",
                 "  comment = new PostComment(content, post, user)",
                 "  if request.parentId: comment.parent = parentComment",
                 "  commentRepo.save(comment)",
             ], PRIMARY)

    add_card(slide, Inches(6.9), Inches(1.4), Inches(6.0), Inches(3.0),
             "⚡ Redis 缓存策略", [
                 "缓存机制: Spring Cache + RedisCacheManager",
                 "",
                 "@Cacheable('forum:post:list')",
                 "function listPosts(page, size, sectionId):",
                 "  // 首次请求: 查DB → 写Redis (TTL=2min)",
                 "  // 后续请求: 直接从Redis读取",
                 "  return postRepo.findAll(pageable)",
                 "",
                 "@CacheEvict('forum:post:list', allEntries=true)",
                 "function createPost(...)  // 写操作清除缓存",
                 "",
                 "序列化: GenericJackson2Json (支持泛型反序列化)",
                 "TTL 配置: list=2min, detail=5min, default=10min",
             ], ACCENT)

    add_card(slide, Inches(0.4), Inches(4.7), Inches(6.2), Inches(2.2),
             "💡 难点与解决方案", [
                 "① 并发点赞去重 → 数据库唯一约束(post_id+user_id)",
                 "   + 业务层异常捕获返回友好提示",
                 "② 双端认证一致性 → 前端Axios 401拦截器 + pending queue",
                 "   单次刷新 + 并发请求排队重试",
                 "③ 缓存一致性 → 写操作主动 @CacheEvict + 短TTL兜底",
                 "④ 服务间调用 → OpenFeign声明式客户端(search→forum)",
             ], ORANGE)

    add_card(slide, Inches(6.9), Inches(4.7), Inches(6.0), Inches(2.2),
             "🔧 开发工具链（技术栈）", [
                 "语言: Java 17 / TypeScript 5",
                 "构建: Maven 3.9 / Vite 5",
                 "容器: Docker Compose (MySQL+Redis+Nacos)",
                 "IDE: IntelliJ IDEA / VS Code",
                 "版本控制: Git + GitHub",
                 "测试: Python自动化回归 + 缓存基准脚本",
             ], RGBColor(0x9C, 0x27, 0xB0))


def slide_frontend(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "04 实现与关键技术 — 双端前端实现", "Dual-End Frontend Implementation")

    add_card(slide, Inches(0.4), Inches(1.4), Inches(6.2), Inches(5.5),
             "🖥️ PC端 (Vue3 + Element Plus)", [
                 "路由: 6个页面 (登录/帖子列表/详情/发帖/个人/通知)",
                 "",
                 "帖子列表页:",
                 "  · 分区筛选下拉 + 关键词搜索",
                 "  · 分页控制 (5/10/20条切换)",
                 "  · 侧边栏: 通知摘要 + 音乐/书籍推荐",
                 "",
                 "帖子详情页:",
                 "  · 帖子内容 + 点赞按钮",
                 "  · 评论列表 (支持二级回复)",
                 "",
                 "认证流程:",
                 "  · 顶部导航栏显示用户名/登录按钮",
                 "  · localStorage 持久化 (forum_pc_*)",
                 "  · 401自动刷新 + 登出状态同步",
                 "",
                 "状态管理: Pinia (仅auth store, 其余为组件状态)",
             ], PRIMARY)

    add_card(slide, Inches(6.9), Inches(1.4), Inches(6.0), Inches(5.5),
             "📱 移动端 (Vue3 + Vant 4)", [
                 "路由: 相同6个页面, 适配移动端布局",
                 "",
                 "交互差异:",
                 "  · NavBar导航替代顶部菜单",
                 "  · Cell组件展示帖子列表",
                 "  · 底部区域评论输入",
                 "  · 个人页集成登出 + 通知入口",
                 "",
                 "统一API层:",
                 "  · 相同的 api/ 模块 (auth/forum/notification/media)",
                 "  · 相同的 axios 实例 + 拦截器逻辑",
                 "  · 不同的 localStorage 前缀 (forum_mobile_*)",
                 "    → 双端可同域运行不冲突",
                 "",
                 "共通设计:",
                 "  · 加载态 / 空状态 / 错误重试",
                 "  · 公共浏览无需登录 (列表/详情)",
                 "  · 写操作路由守卫 (无token → /login)",
             ], ACCENT)


def slide_testing(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "05 系统测试", "System Testing")

    add_card(slide, Inches(0.4), Inches(1.4), Inches(5.8), Inches(3.0),
             "🧪 自动化回归测试 (12项场景)", [
                 "✅ 分区读取验证",
                 "✅ 双用户注册登录",
                 "✅ 发帖 → 评论 → 搜索 全链路",
                 "✅ 通知与推荐模块接口",
                 "✅ 我的通知读取与已读标记",
                 "✅ 无Token写操作拦截 (401)",
                 "✅ 无权限操作拦截 (403)",
                 "✅ 并发重复点赞稳定性 (去重)",
                 "✅ 登出后会话立即失效",
                 "✅ Refresh Token 续签流程",
                 "✅ Token 过期拦截",
                 "通过率: 100% (所有场景全部通过)",
             ], ACCENT)

    headers = ["测试指标", "测试结果", "说明"]
    rows = [
        ["帖子列表冷请求", "~22-31 ms", "首次请求(无缓存)"],
        ["帖子列表热请求均值", "~4-5 ms", "后续请求(Redis缓存)"],
        ["热请求 P95", "~5-6 ms", "95%请求在此延迟内"],
        ["缓存提升比例", "81-85%", "相对冷请求提升"],
        ["回归测试通过率", "100%", "12项场景全部通过"],
        ["异常场景通过率", "100%", "6项异常场景全部通过"],
    ]

    make_table(slide, Inches(6.5), Inches(1.4), Inches(6.3), Emu(int(Inches(0.42))),
               headers, rows)

    add_card(slide, Inches(0.4), Inches(4.7), Inches(12.4), Inches(2.2),
             "📋 测试策略总结", [
                 "• 测试方式: Python自动化脚本 (run_system_regression.py) + 缓存基准脚本 (benchmark_forum_cache.py)",
                 "• 覆盖范围: 全链路功能回归 + 异常场景 + 性能基准 + 并发稳定性",
                 "• 可复现性: 一键执行 (generate-test-reports.sh), 报告自动生成为Markdown文档",
                 "• 运维闭环: 启动脚本 → 验活检查 → 回归测试 → 报告产物, 全流程可重复执行",
             ], PRIMARY)


def slide_summary(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_title_bar(slide, "06 总结与展望", "Summary & Future Work")

    add_card(slide, Inches(0.4), Inches(1.4), Inches(6.0), Inches(3.2),
             "🏆 核心研究成果", [
                 "① 完成了基于微服务架构的论坛系统设计与实现",
                 "   · 6个微服务独立部署, 职责清晰, 松耦合",
                 "   · 网关统一接入, Nacos注册发现",
                 "",
                 "② 实现了PC+移动双端协同的前端系统",
                 "   · 统一API设计, 一致的认证与交互体验",
                 "   · Vue3 + Element Plus / Vant 技术栈",
                 "",
                 "③ 建立了可复现的工程验证体系",
                 "   · 自动化回归+缓存基准+一键启停",
                 "   · 测试通过率100%, 缓存提升80%+",
             ], ACCENT)

    add_card(slide, Inches(6.7), Inches(1.4), Inches(6.0), Inches(3.2),
             "⚠️ 局限性", [
                 "• 搜索功能基于内存过滤, 未引入全文搜索引擎",
                 "  (如Elasticsearch), 大数据量下效率受限",
                 "",
                 "• 媒体推荐为静态数据, 未接入推荐算法",
                 "",
                 "• 系统未做高可用集群部署验证",
                 "  (单实例部署, 未验证分布式容灾)",
                 "",
                 "• 前端edit/delete功能API已就绪但UI未完整接入",
                 "",
                 "• 未引入CI/CD自动化流水线",
             ], ORANGE)

    add_card(slide, Inches(0.4), Inches(4.9), Inches(12.3), Inches(2.0),
             "🚀 未来优化方向", [
                 "① 引入 Elasticsearch 实现全文搜索 + 高亮 + 权重排序 → 提升大规模内容检索效率",
                 "② 接入推荐算法（协同过滤/内容匹配）→ 实现个性化内容推荐",
                 "③ 多实例部署 + Kubernetes编排 → 实现高可用与弹性扩缩容",
                 "④ 引入消息队列（RocketMQ/Kafka）→ 异步通知、服务解耦",
                 "⑤ 前端 SSR + PWA → 提升首屏性能和移动端离线体验",
             ], PRIMARY)


def slide_thanks(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)

    add_shape_fill(slide, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT, PRIMARY, 0)

    add_textbox(slide, Inches(2), Inches(2.0), Inches(9), Inches(1.5),
                "感谢各位老师的指导与聆听", font_size=40, bold=True,
                color=WHITE, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(2), Inches(3.8), Inches(9), Inches(1.0),
                "恳请各位老师批评指正", font_size=24,
                color=RGBColor(0xBB, 0xD5, 0xFD), alignment=PP_ALIGN.CENTER)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5), Inches(5.0),
                                  Inches(3.3), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0xBB, 0xD5, 0xFD)
    line.line.fill.background()

    add_textbox(slide, Inches(3), Inches(5.3), Inches(7), Inches(0.5),
                "答辩人：XXX　　指导教师：XXX", font_size=16,
                color=RGBColor(0xBB, 0xD5, 0xFD), alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(3), Inches(5.8), Inches(7), Inches(0.5),
                "二〇二六年五月", font_size=14,
                color=RGBColor(0xBB, 0xD5, 0xFD), alignment=PP_ALIGN.CENTER)


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    slide_cover(prs)
    slide_outline(prs)
    slide_background(prs)
    slide_requirements(prs)
    slide_architecture(prs)
    slide_architecture_modules(prs)
    slide_database(prs)
    slide_tech_selection(prs)
    slide_implementation_1(prs)
    slide_implementation_2(prs)
    slide_frontend(prs)
    slide_testing(prs)
    slide_summary(prs)
    slide_thanks(prs)

    output_path = "/workspace/docs/毕业答辩PPT.pptx"
    prs.save(output_path)
    print(f"PPT已生成: {output_path}")
    print(f"共 {len(prs.slides)} 页幻灯片")


if __name__ == "__main__":
    main()
