# PLC Math & Logic Studio - Android Edition
# Same core engine, KivyMD UI for Android

import ast, json, os, math, datetime, re, tempfile
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.graphics.instructions import PushMatrix, PopMatrix, Translate
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard

try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None
    try:
        from PIL import Image
    except ImportError:
        Image = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
except ImportError:
    SimpleDocTemplate = None

# ─── i18n System ───────────────────────────────
languages = {
    "English": {
        "app_title": "PLC Logic Studio",
        "templates": "Templates:",
        "choose_template": "Choose Template",
        "btn_save": "Save",
        "btn_delete": "Delete",
        "btn_guide": "Guide",
        "btn_shot": "Screenshot",
        "btn_pdf": "PDF",
        "equation": "Equation / Logic:",
        "btn_draw": "Draw Blocks",
        "btn_preview": "Preview ST",
        "guide_title": "Block Guide",
        "warn_eq": "Enter equation first.",
        "shot_success": "Saved: {path}",
        "pdf_success": "PDF saved: {path}",
        "st_copied": "ST code copied.",
        "tpl_saved": "Template '{name}' saved.",
        "tpl_overwrite": "Overwrite '{name}'?",
        "tpl_core_warn": "Cannot delete built-in templates.",
        "tpl_delete_confirm": "Delete '{name}'?",
        "tpl_deleted": "Template deleted.",
        "err_invalid_eq": "Use: OUTPUT = EXPRESSION",
        "err_multi_eq": "Only one '=' allowed.",
        "err_empty_lhs": "Output name empty.",
        "err_empty_rhs": "Expression empty.",
        "err_syntax": "Syntax error.",
        "err_file": "Error: {err}",
        "lets_make": "Let's make something!",
        "blocks_info": {
            "ADD": "Addition (+)", "SUB": "Subtraction (-)", "MUL": "Multiplication (*)",
            "DIV": "Division (/)", "EXPT": "Exponent (**)", "GT": "Greater Than (>)",
            "LT": "Less Than (<)", "GE": "Greater or Equal (>=)", "LE": "Less or Equal (<=)",
            "EQ": "Equal (==)", "NE": "Not Equal (!=)", "AND": "Logical AND",
            "OR": "Logical OR", "NOT": "Logical NOT", "SQRT": "Square Root",
            "ABS": "Absolute Value", "SIN": "Sine", "COS": "Cosine",
            "TAN": "Tangent", "EXP": "Exponential", "LOG": "Natural Log"
        }
    },
    "العربية": {
        "app_title": "استوديو PLC",
        "templates": ":القوالب",
        "choose_template": "اختر قالباً",
        "btn_save": "حفظ",
        "btn_delete": "حذف",
        "btn_guide": "دليل",
        "btn_shot": "لقطة",
        "btn_pdf": "PDF",
        "equation": ":المعادلة",
        "btn_draw": "ارسم البلوكات",
        "btn_preview": "معاينة ST",
        "guide_title": "دليل البلوكات",
        "warn_eq": "أدخل معادلة أولاً.",
        "shot_success": "حُفظ: {path}",
        "pdf_success": "PDF حُفظ: {path}",
        "st_copied": "تم نسخ كود ST.",
        "tpl_saved": "'{name}' حُفظ القالب",
        "tpl_overwrite": "؟ '{name}' هل استبدال",
        "tpl_core_warn": "لا يمكن حذف القوالب الأساسية.",
        "tpl_delete_confirm": "؟ '{name}' حذف",
        "tpl_deleted": "حُذف القالب.",
        "err_invalid_eq": "استخدم: OUTPUT = EXPRESSION",
        "err_multi_eq": "علامة = واحدة فقط مسموحة.",
        "err_empty_lhs": "اسم المخرج فارغ.",
        "err_empty_rhs": "التعبير فارغ.",
        "err_syntax": "خطأ في الصياغة.",
        "err_file": "خطأ: {err}",
        "lets_make": "لنبدع!",
        "blocks_info": {
            "ADD": "الجمع (+)", "SUB": "الطرح (-)", "MUL": "الضرب (*)",
            "DIV": "القسمة (/)", "EXPT": "الأس (**)", "GT": "أكبر من (>)",
            "LT": "أصغر من (<)", "GE": "أكبر أو يساوي (>=)", "LE": "أصغر أو يساوي (<=)",
            "EQ": "يساوي (==)", "NE": "لا يساوي (!=)", "AND": "بوابة وَ",
            "OR": "بوابة أو", "NOT": "نفي", "SQRT": "جذر تربيعي",
            "ABS": "قيمة مطلقة", "SIN": "جا", "COS": "جتا",
            "TAN": "ظا", "EXP": "أسي", "LOG": "لوغاريتم"
        }
    },
    "Francais": {
        "app_title": "Studio PLC",
        "templates": "Modeles:",
        "choose_template": "Choisir modele",
        "btn_save": "Sauver",
        "btn_delete": "Suppr.",
        "btn_guide": "Guide",
        "btn_shot": "Capture",
        "btn_pdf": "PDF",
        "equation": "Equation:",
        "btn_draw": "Dessiner",
        "btn_preview": "Apercu ST",
        "guide_title": "Guide des Blocs",
        "warn_eq": "Entrez une equation.",
        "shot_success": "Sauve: {path}",
        "pdf_success": "PDF sauve: {path}",
        "st_copied": "Code ST copie.",
        "tpl_saved": "Modele '{name}' sauve.",
        "tpl_overwrite": "Ecraser '{name}'?",
        "tpl_core_warn": "Modeles de base proteges.",
        "tpl_delete_confirm": "Supprimer '{name}'?",
        "tpl_deleted": "Modele supprime.",
        "err_invalid_eq": "Utilisez: SORTIE = EXPRESSION",
        "err_multi_eq": "Un seul '=' autorise.",
        "err_empty_lhs": "Nom de sortie vide.",
        "err_empty_rhs": "Expression vide.",
        "err_syntax": "Erreur de syntaxe.",
        "err_file": "Erreur: {err}",
        "lets_make": "Creons quelque chose!",
        "blocks_info": {
            "ADD": "Addition (+)", "SUB": "Soustraction (-)", "MUL": "Multiplication (*)",
            "DIV": "Division (/)", "EXPT": "Exposant (**)", "GT": "Plus grand que (>)",
            "LT": "Plus petit que (<)", "GE": "Plus grand ou egal (>=)", "LE": "Plus petit ou egal (<=)",
            "EQ": "Egal (==)", "NE": "Different (!=)", "AND": "ET Logique",
            "OR": "OU Logique", "NOT": "NON", "SQRT": "Racine carree",
            "ABS": "Valeur absolue", "SIN": "Sinus", "COS": "Cosinus",
            "TAN": "Tangente", "EXP": "Exponentielle", "LOG": "Log naturel"
        }
    }
}
current_lang = "English"

# ─── Template System ────────────────────────────
DB_FILE = "plc_templates.json"
default_templates = {
    "Tank Volume": "VOLUME = PI * (RADIUS ** 2) * HEIGHT",
    "Analog Scaling": "SCALED = ((RAW - MINRAW) / (MAXRAW - MINRAW)) * (MAXSCALE - MINSCALE) + MINSCALE",
    "Pump Interlock": "PUMP_RUN = (LEVEL > 20) and (PRESSURE < 5) and (TEMP < 80)",
    "Flow Rate": "FLOW = PI * ((DIA / 2) ** 2) * VELOCITY",
    "Hydraulic HP": "HP = (FLOW_GPM * PRESSURE_PSI) / 1714",
    "C to Fahrenheit": "TEMP_F = (TEMP_C * 1.8) + 32",
    "Newton 2nd Law": "FORCE = MASS * ACCEL",
    "PID Error": "ERROR = SETPOINT - PV"
}

def load_templates():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except Exception:
            pass
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_templates, f, indent=4)
    except Exception:
        pass
    return default_templates.copy()

def save_templates(tdict):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(tdict, f, indent=4)
        return True
    except Exception:
        return False

templates_db = load_templates()

# ─── AST Engine ─────────────────────────────────
CONSTANTS = {"PI": math.pi, "E": math.e, "TAU": math.tau}
ALLOWED_FUNCS = {"SQRT": math.sqrt, "ABS": abs, "SIN": math.sin, "COS": math.cos,
    "TAN": math.tan, "EXP": math.exp, "LOG": math.log, "LN": math.log,
    "ROUND": round, "MIN": min, "MAX": max}

class BlockGenerator:
    def __init__(self):
        self.blocks = []
        self.temp_count = 0
        self.op_map = {
            ast.Add: "ADD", ast.Sub: "SUB", ast.Mult: "MUL", ast.Div: "DIV",
            ast.Pow: "EXPT", ast.Mod: "MOD", ast.FloorDiv: "FDIV",
            ast.Gt: "GT", ast.Lt: "LT", ast.GtE: "GE", ast.LtE: "LE",
            ast.Eq: "EQ", ast.NotEq: "NE",
            ast.And: "AND", ast.Or: "OR"
        }
    def new_wire(self):
        self.temp_count += 1
        return f"W_{self.temp_count}"
    def add_block(self, op, in1, in2, out):
        self.blocks.append({"op": op, "in1": in1, "in2": in2, "out": out})
        return out
    def parse_expression(self, node):
        if isinstance(node, ast.Name):
            nm = node.id.upper()
            return str(CONSTANTS[nm]) if nm in CONSTANTS else nm
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return str(node.value)
            raise ValueError(f"Bad const: {type(node.value).__name__}")
        if isinstance(node, ast.UnaryOp):
            op = self.parse_expression(node.operand)
            out = self.new_wire()
            if isinstance(node.op, ast.USub):
                return self.add_block("MUL", op, "-1", out)
            if isinstance(node.op, ast.UAdd):
                return op
        if isinstance(node, ast.BinOp):
            l = self.parse_expression(node.left)
            r = self.parse_expression(node.right)
            op = self.op_map.get(type(node.op))
            if not op: raise ValueError(f"Bad binary: {type(node.op).__name__}")
            return self.add_block(op, l, r, self.new_wire())
        if isinstance(node, ast.BoolOp):
            op = self.op_map.get(type(node.op))
            if not op: raise ValueError(f"Bad bool: {type(node.op).__name__}")
            r = self.parse_expression(node.values[0])
            for v in node.values[1:]:
                r = self.add_block(op, r, self.parse_expression(v), self.new_wire())
            return r
        if isinstance(node, ast.Compare):
            l = self.parse_expression(node.left)
            for op_node, comp in zip(node.ops, node.comparators):
                op = self.op_map.get(type(op_node))
                if not op: raise ValueError(f"Bad cmp: {type(op_node).__name__}")
                r = self.parse_expression(comp)
                l = self.add_block(op, l, r, self.new_wire())
            return l
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Simple func names only")
            fn = node.func.id.upper()
            if len(node.args) < 1: raise ValueError(f"{fn}() needs arg")
            if len(node.args) > 1: raise ValueError(f"{fn} takes 1 arg, got {len(node.args)}")
            if fn not in ALLOWED_FUNCS: raise ValueError(f"Unknown: {fn}")
            return self.add_block(fn, self.parse_expression(node.args[0]), "---", self.new_wire())
        raise ValueError(f"Unsupported: {type(node).__name__}")

def process_equation(equation_str):
    if "=" not in equation_str: return None, "err_invalid_eq"
    if equation_str.count("=") > 1: return None, "err_multi_eq"
    out_var, expr = equation_str.split("=", 1)
    out_var = out_var.strip().upper()
    expr = expr.strip()
    if not out_var: return None, "err_empty_lhs"
    if not expr: return None, "err_empty_rhs"
    expr_norm = expr.replace(" AND ", " and ").replace(" OR ", " or ")
    try:
        tree = ast.parse(expr_norm, mode="eval")
    except SyntaxError: return None, "err_syntax"
    try:
        gen = BlockGenerator()
        result = gen.parse_expression(tree.body)
        if gen.blocks: gen.blocks[-1]["out"] = out_var
        return gen.blocks, None
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"err_syntax ({e})"

# ─── Block Drawing Helpers ──────────────────────
BLOCK_COLORS_DARK = {
    "LOGIC": ("#198754", "#146c43", "white"),
    "MATH": ("#0d6efd", "#0a58ca", "white"),
    "FUNC": ("#6f42c1", "#59359a", "white"),
}
BLOCK_COLORS_LIGHT = {
    "LOGIC": ("#D4EDDA", "#155724", "black"),
    "MATH": ("#CCE5FF", "#004085", "black"),
    "FUNC": ("#E2D9F3", "#381861", "black"),
}
LOGIC_OPS = {"AND","OR","NOT","GT","LT","GE","LE","EQ","NE"}
MATH_OPS = {"ADD","SUB","MUL","DIV","EXPT","MOD","FDIV"}

def get_block_colors(op_name, is_dark):
    pal = BLOCK_COLORS_DARK if is_dark else BLOCK_COLORS_LIGHT
    if op_name in LOGIC_OPS: return pal["LOGIC"]
    if op_name in MATH_OPS: return pal["MATH"]
    return pal["FUNC"]

# ─── FBD Canvas Widget ──────────────────────────
class FBDCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blocks = []
        self.is_dark = True
        self.wire_color = "#A6ACCD"
        self.text_color = "#FFFFFF"
        self.bg_color = "#1E1E1E"
        self.block_w = 130
        self.block_h = 75
        self.spacing_x = 420
        self.start_x = 150
        self.start_y = 50

    def draw(self, blocks, is_dark):
        self.blocks = blocks
        self.is_dark = is_dark
        if is_dark:
            self.bg_color = "#1E1E1E"
            self.wire_color = "#A6ACCD"
            self.text_color = "#FFFFFF"
        else:
            self.bg_color = "#FFFFFF"
            self.wire_color = "#495057"
            self.text_color = "#212529"

        total_w = self.start_x + len(blocks) * self.spacing_x + 300
        total_h = self.start_y + self.block_h + 200
        self.size = (max(total_w, dp(360)), max(total_h, dp(200)))
        self.canvas.clear()
        self._draw_grid(total_w, total_h)
        self._draw_blocks()

    def _draw_grid(self, total_w, total_h):
        with self.canvas:
            Color(*get_color_from_hex(self.bg_color))
            Rectangle(pos=(0, 0), size=self.size)
            Color(*get_color_from_hex("#2E3440" if self.is_dark else "#E9ECEF"))
            for x in range(0, int(total_w) + 25, 25):
                Line(points=[x, 0, x, total_h], width=0.5, dash_length=3, dash_offset=3)
            for y in range(0, int(total_h) + 25, 25):
                Line(points=[0, y, total_w, y], width=0.5, dash_length=3, dash_offset=3)

    def _draw_blocks(self):
        if not self.blocks:
            return
        # First pass: positions
        op = {}  # out_name -> position (x, y)
        blocks_xy = []
        for idx, block in enumerate(self.blocks):
            x = self.start_x + idx * self.spacing_x
            y = self.start_y + self.block_h
            blocks_xy.append((x, y))
            out_x = x + self.block_w
            out_y = y + self.block_h / 2
            op[block["out"]] = (out_x, out_y)

        # Draw wires first (on bottom layer)
        self.canvas.add(Color(*get_color_from_hex(self.wire_color)))
        wire_width = dp(2.2)
        for idx, block in enumerate(self.blocks):
            bx, by = blocks_xy[idx]
            inp1_info = block["in1"]
            inp2_info = block["in2"]
            # Input 1
            if inp1_info in op:
                sx, sy = op[inp1_info]
                dx, dy = bx, by + 25
                mid = (sx + dx) // 2
                self.canvas.add(Line(points=[sx, sy, mid, sy, mid, dy, dx, dy], width=wire_width))
                self._arrow(dx, dy, 1, wire_width)
            else:
                self._stub(bx, by + 25, inp1_info, 1, wire_width)
            # Input 2
            if inp2_info != "---":
                if inp2_info in op:
                    sx, sy = op[inp2_info]
                    dx, dy = bx, by + 50
                    mid = (sx + dx) // 2
                    self.canvas.add(Line(points=[sx, sy, mid, sy, mid, dy, dx, dy], width=wire_width))
                    self._arrow(dx, dy, 1, wire_width)
                else:
                    self._stub(bx, by + 50, inp2_info, 2, wire_width)

        # Draw blocks (on top layer)
        for idx, block in enumerate(self.blocks):
            bx, by = blocks_xy[idx]
            fill, outline, txt = get_block_colors(block["op"], self.is_dark)
            out_x = bx + self.block_w
            out_y = by + self.block_h / 2

            # Shadow
            self.canvas.add(Color(*get_color_from_hex("#111111" if self.is_dark else "#DEE2E6")))
            shadow = Rectangle(pos=(bx + 4, by + 4), size=(self.block_w, self.block_h))
            self.canvas.add(shadow)

            # Block body
            self.canvas.add(Color(*get_color_from_hex(fill)))
            self.canvas.add(Rectangle(pos=(bx, by), size=(self.block_w, self.block_h)))
            self.canvas.add(Color(*get_color_from_hex(outline)))
            self.canvas.add(Line(rectangle=(bx, by, self.block_w, self.block_h), width=2))

            # Block label
            self._label(bx + self.block_w / 2, by + self.block_h / 2, block["op"], txt, 14, "bold", "center", "center")

            # Output
            self.canvas.add(Color(*get_color_from_hex(self.bg_color)))
            self.canvas.add(Ellipse(pos=(out_x - 5, out_y - 5), size=(10, 10)))
            self.canvas.add(Color(*get_color_from_hex(outline)))
            self.canvas.add(Line(circle=(out_x, out_y, 5), width=2))
            self._label(out_x + 12, out_y - 14, block["out"], "#FF4C4C", 12, "bold", "left", "bottom")

    def _arrow(self, x, y, direction, width):
        self.canvas.add(Color(*get_color_from_hex(self.wire_color)))
        if direction > 0:
            self.canvas.add(Line(points=[x, y, x - 8, y - 4, x - 8, y + 4], width=width, close=True))
        else:
            self.canvas.add(Line(points=[x, y, x + 8, y - 4, x + 8, y + 4], width=width, close=True))

    def _stub(self, bx, by, text, pin_num, width):
        stub_end = bx - 140
        self.canvas.add(Color(*get_color_from_hex(self.wire_color)))
        self.canvas.add(Line(points=[stub_end, by, bx, by], width=width))
        self._arrow(bx, by, 1, width)
        # Label
        if text.startswith("W_") or text in CONSTANTS or text.replace(".","").replace("-","").isdigit():
            c = "#7F8C8D" if self.is_dark else "#95A5A6"
            f = 11
            s = "italic"
        else:
            c = self.text_color
            f = 12
            s = "normal"
        ly = by - 10 if pin_num == 1 else by + 10
        self._label((stub_end + bx) // 2, ly, text, c, f, s, "center", "top" if pin_num == 1 else "bottom")
        # Input pin
        self.canvas.add(Color(*get_color_from_hex(self.bg_color)))
        self.canvas.add(Ellipse(pos=(bx - 4, by - 4), size=(8, 8)))
        colors = get_block_colors("ADD", self.is_dark)
        self.canvas.add(Color(*get_color_from_hex(colors[1])))
        self.canvas.add(Line(circle=(bx, by, 4), width=2))

    def _label(self, x, y, text, color, size, style, halign, valign):
        from kivy.uix.label import Label
        lbl = Label(text=text, font_size=sp(size), bold=("bold" in style),
                    italic=("italic" in style), color=get_color_from_hex(color),
                    halign=halign, valign=valign, size_hint=(None, None))
        lbl.texture_update()
        lbl.size = lbl.texture_size
        if halign == "center": x -= lbl.width / 2
        elif halign == "right": x -= lbl.width
        if valign == "center": y -= lbl.height / 2
        elif valign == "top": y -= lbl.height
        lbl.pos = (x, y)
        self.canvas.add(lbl)

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

# ─── Main App ───────────────────────────────────
class PLCStudioApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "PLC Logic Studio"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_style = "M3"

    def build(self):
        self.lang = languages[current_lang]
        self.is_dark = True
        self._build_ui()
        return self.root

    def _build_ui(self):
        from kivy.uix.screenmanager import ScreenManager, Screen
        self.root = ScreenManager()

        main_screen = Screen(name="main")

        layout = MDBoxLayout(orientation="vertical", spacing=dp(4), padding=[dp(8), dp(4), dp(8), dp(4)])

        # ── Top Bar ──
        top = MDBoxLayout(adaptive_height=True, spacing=dp(6))

        self.theme_btn = MDIconButton(icon="weather-sunny", on_release=self.toggle_theme)
        top.add_widget(self.theme_btn)

        lang_btn = MDFlatButton(text="EN", on_release=self.open_lang_menu)
        self.lang_btn = lang_btn
        top.add_widget(lang_btn)
        self.lang_menu = None

        for text, cmd in [("Guide", self.open_guide), ("Screenshot", self.take_shot), ("PDF", self.make_pdf)]:
            b = MDFlatButton(text=text, on_release=cmd)
            setattr(self, f"btn_{text.lower()}", b)
            top.add_widget(b)

        layout.add_widget(top)

        # ── Templates ──
        tpl_row = MDBoxLayout(adaptive_height=True, spacing=dp(4))

        self.tpl_label = MDLabel(text=self.lang["templates"], size_hint_x=0.25, halign="left")
        tpl_row.add_widget(self.tpl_label)

        self.tpl_btn = MDFlatButton(text=self.lang["choose_template"], on_release=self.open_tpl_menu)
        tpl_row.add_widget(self.tpl_btn)

        for text, cmd, color in [("Save", self.save_tpl, "#FD7E14"), ("Delete", self.del_tpl, "#DC3545")]:
            b = MDFlatButton(text=text, md_bg_color=get_color_from_hex(color),
                           text_color=(1,1,1,1), on_release=cmd)
            setattr(self, f"tpl_{text.lower()}", b)
            tpl_row.add_widget(b)

        layout.add_widget(tpl_row)

        # ── Equation Input ──
        self.eq_label = MDLabel(text=self.lang["equation"], adaptive_height=True)
        layout.add_widget(self.eq_label)

        self.eq_input = MDTextField(hint_text="OUTPUT = EXPRESSION", multiline=False,
                                    font_size=sp(18), mode="outlined",
                                    on_text_validate=self.draw_blocks)
        layout.add_widget(self.eq_input)

        # ── Keypad ──
        keypad = MDBoxLayout(adaptive_height=True, spacing=dp(3))
        keys = [("+", "#2D3748"), ("-", "#2D3748"), ("*", "#2D3748"), ("/", "#2D3748"),
                ("**", "#2D3748"), ("=", "#4A5568"), ("(", "#4A5568"), (")", "#4A5568"),
                ("and", "#0D6EFD"), ("or", "#0D6EFD"), ("not", "#DC3545")]
        for txt, color in keys:
            kb = MDFlatButton(text=txt, md_bg_color=get_color_from_hex(color),
                             text_color=(1,1,1,1), font_size=sp(14),
                             on_release=lambda x, v=txt: self.insert_op(v))
            keypad.add_widget(kb)
        layout.add_widget(keypad)

        # ── Action Buttons ──
        actions = MDBoxLayout(adaptive_height=True, spacing=dp(10))
        for text, cmd, color in [("Draw Blocks", self.draw_blocks, "#198754"),
                                 ("Preview ST", self.open_st_dialog, "#0D6EFD")]:
            b = MDRaisedButton(text=text, md_bg_color=get_color_from_hex(color),
                              text_color=(1,1,1,1), on_release=cmd)
            setattr(self, f"btn_{text.split()[0].lower()}", b)
            actions.add_widget(b)
        layout.add_widget(actions)

        # ── Canvas ──
        sv = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.canvas_widget = FBDCanvas()
        sv.add_widget(self.canvas_widget)
        layout.add_widget(sv, 1)

        # ── Footer ──
        footer = MDLabel(text=self.lang["lets_make"], adaptive_height=True,
                         halign="center", font_style="Caption",
                         theme_text_color="Hint")
        layout.add_widget(footer)

        main_screen.add_widget(layout)
        self.root.add_widget(main_screen)
        self.root.current = "main"

        # Build language menu
        self._build_lang_menu()
        self._build_tpl_menu()

    # ─── i18n ───
    def _build_lang_menu(self):
        items = [{"text": k, "on_release": lambda v=k: self.set_lang(v)}
                 for k in languages]
        self.lang_menu = MDDropdownMenu(caller=self.lang_btn, items=items,
                                        width_mult=3, position="bottom")

    def open_lang_menu(self, btn):
        self.lang_menu.open()

    def set_lang(self, lang_name):
        global current_lang
        current_lang = lang_name
        self.lang = languages[lang_name]
        self.lang_btn.text = lang_name[:2].upper()
        self.lang_menu.dismiss()
        self.refresh_ui()

    def refresh_ui(self):
        self.tpl_label.text = self.lang["templates"]
        self.tpl_btn.text = self.lang["choose_template"]
        self.eq_label.text = self.lang["equation"]
        for name, attr in [("Guide", "btn_guide"), ("Screenshot", "btn_shot"), ("PDF", "btn_pdf")]:
            getattr(self, attr).text = self.lang[f"btn_{name.lower()}"]
        self.tpl_save.text = self.lang["btn_save"]
        self.tpl_delete.text = self.lang["btn_delete"]
        self.btn_draw.text = self.lang["btn_draw"]
        self.btn_preview.text = self.lang["btn_preview"]

    # ─── Templates ───
    def open_tpl_menu(self, btn):
        items = [{"text": k, "on_release": lambda v=k: self.select_tpl(v)}
                 for k in templates_db]
        self.tpl_menu = MDDropdownMenu(caller=self.tpl_btn, items=items,
                                       width_mult=4, position="bottom")
        self.tpl_menu.open()

    def select_tpl(self, name):
        self.tpl_menu.dismiss()
        self.tpl_btn.text = name
        self.eq_input.text = templates_db[name]
        self.draw_blocks()

    def save_tpl(self, btn):
        if "=" not in self.eq_input.text:
            self.snack(self.lang["err_invalid_eq"])
            return
        dialog = MDDialog(title="Save Template", text="Enter template name:",
                         items=[MDTextField(hint_text="Name")],
                         buttons=[MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                                  MDRaisedButton(text="Save", on_release=lambda x: self._do_save(dialog))])
        dialog.open()

    def _do_save(self, dialog):
        name = dialog.items[0].text.strip()
        dialog.dismiss()
        if not name: return
        if name in templates_db:
            import copy
            c = copy.copy
            conf = MDDialog(title="Confirm", text=self.lang["tpl_overwrite"].format(name=name),
                           buttons=[MDFlatButton(text="No", on_release=lambda x: conf.dismiss()),
                                    MDRaisedButton(text="Yes", on_release=lambda x: (conf.dismiss(),
                                        self._final_save(name)))])
            conf.open()
        else:
            self._final_save(name)

    def _final_save(self, name):
        templates_db[name] = self.eq_input.text
        if save_templates(templates_db):
            self.snack(self.lang["tpl_saved"].format(name=name))

    def del_tpl(self, btn):
        name = self.tpl_btn.text
        if name in default_templates:
            self.snack(self.lang["tpl_core_warn"])
            return
        if name not in templates_db: return
        conf = MDDialog(title="Confirm", text=self.lang["tpl_delete_confirm"].format(name=name),
                       buttons=[MDFlatButton(text="No", on_release=lambda x: conf.dismiss()),
                                MDRaisedButton(text="Yes", on_release=lambda x:
                                    (conf.dismiss(), self._do_del(name)))])
        conf.open()

    def _do_del(self, name):
        del templates_db[name]
        if save_templates(templates_db):
            self.tpl_btn.text = self.lang["choose_template"]
            self.snack(self.lang["tpl_deleted"])

    # ─── Core ───
    def insert_op(self, val):
        self.eq_input.insert_text(f" {val} ")

    def draw_blocks(self, *args):
        eq = self.eq_input.text.strip()
        if not eq:
            self.snack(self.lang["warn_eq"])
            return
        blocks, error = process_equation(eq)
        if error:
            err_text = self.lang.get(error, error)
            self.snack(err_text)
            return
        self.canvas_widget.draw(blocks, self.is_dark)

    def toggle_theme(self, btn):
        self.is_dark = not self.is_dark
        self.theme_cls.theme_style = "Dark" if self.is_dark else "Light"
        self.theme_btn.icon = "weather-night" if self.is_dark else "weather-sunny"
        if self.eq_input.text.strip():
            self.draw_blocks()

    def snack(self, msg):
        MDSnackbar(MDSnackbarSupportingText(text=msg), y=dp(24)).open()

    # ─── Guide Dialog ───
    def open_guide(self, btn):
        lines = []
        for name, desc in self.lang["blocks_info"].items():
            lines.append(f"[b]{name}[/b]: {desc}")
        dialog = MDDialog(title=self.lang["guide_title"],
                         text="\n".join(lines),
                         buttons=[MDFlatButton(text="Close", on_release=lambda x: dialog.dismiss())],
                         size_hint_x=0.9)
        dialog.open()

    # ─── ST Preview ───
    def open_st_dialog(self, btn):
        eq = self.eq_input.text.strip()
        if not eq:
            self.snack(self.lang["warn_eq"])
            return
        try:
            out_var, expression = eq.split("=", 1)
            out_var = out_var.strip().upper()
            expression = expression.strip()
            from ast import walk, Name as AstName
            inputs = set()
            expr_norm = expression.replace(" AND ", " and ").replace(" OR ", " or ")
            parsed = ast.parse(expr_norm, mode="eval")
            for n in walk(parsed):
                if isinstance(n, AstName):
                    nm = n.id.upper()
                    if nm not in ALLOWED_FUNCS and nm not in CONSTANTS:
                        inputs.add(nm)
        except Exception as e:
            self.snack(f"Parse: {e}")
            return

        st_code = f"FUNCTION_BLOCK LogicBlock\n\nVAR_INPUT\n"
        for v in sorted(inputs):
            ty = "REAL" if not any(k in v for k in ["PUMP","RUN","CMD","FLAG"]) else "BOOL"
            st_code += f"    {v} : {ty};\n"
        st_code += f"END_VAR\n\nVAR_OUTPUT\n    {out_var} : REAL;\nEND_VAR\n\n"
        st_code += f"{out_var} := {expression};\n\nEND_FUNCTION_BLOCK"

        dialog = MDDialog(title="ST Code Preview", text=st_code,
                         buttons=[MDFlatButton(text="Copy", on_release=lambda x:
                             (self.copy_st(st_code), dialog.dismiss())),
                                  MDFlatButton(text="Close", on_release=lambda x: dialog.dismiss())],
                         size_hint_x=0.95)
        dialog.open()

    def copy_st(self, text):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(text)
        self.snack(self.lang["st_copied"])

    # ─── Screenshot ───
    def take_shot(self, btn):
        if not self.eq_input.text.strip():
            self.snack(self.lang["warn_eq"])
            return
        self.draw_blocks()
        Clock.schedule_once(lambda dt: self._do_shot(), 0.2)

    def _do_shot(self):
        name = "PLC_Capture.png"
        try:
            self.canvas_widget.export_to_png(name)
            self.snack(self.lang["shot_success"].format(path=name))
        except Exception as e:
            self.snack(f"Error: {e}")

    # ─── PDF ───
    def make_pdf(self, btn):
        if SimpleDocTemplate is None:
            self.snack("reportlab not installed")
            return
        if not self.eq_input.text.strip():
            self.snack(self.lang["warn_eq"])
            return
        self.draw_blocks()
        Clock.schedule_once(lambda dt: self._do_pdf(), 0.3)

    def _do_pdf(self):
        name = "PLC_Report.pdf"
        tmp_img = os.path.join(tempfile.gettempdir(), "fbd_android_tmp.png")
        try:
            self.canvas_widget.export_to_png(tmp_img)
        except Exception as e:
            self.snack(f"Image: {e}")
            return
        try:
            from PIL import Image as PILImage
            with PILImage.open(tmp_img) as im:
                iw, ih = im.size
            ratio = min(530.0 / iw, 700.0 / ih) if iw and ih else 0.3
            dw, dh = iw * ratio, ih * ratio

            doc = SimpleDocTemplate(name, pagesize=letter,
                                    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            title = ParagraphStyle("T", parent=styles["Heading1"], fontName="Helvetica-Bold",
                                   fontSize=18, spaceAfter=12, textColor="#0D6EFD")
            meta = ParagraphStyle("M", parent=styles["Normal"], fontSize=10, spaceAfter=10)
            eqs = ParagraphStyle("E", parent=styles["Code"], fontName="Courier-Bold",
                                 fontSize=11, spaceAfter=15, textColor="#198754")

            clean = self.eq_input.text.split("=")[0].strip().upper()[:30] if "=" in self.eq_input.text else "PLC"
            story = [Paragraph(f"PLC Report: {clean}", title),
                     Paragraph(f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M}", meta),
                     Paragraph(f"<b>Equation:</b> {self.eq_input.text}", eqs),
                     Paragraph("<b>FBD Diagram:</b>", styles["Normal"]),
                     Spacer(1, 8),
                     RLImage(tmp_img, width=dw, height=dh)]
            doc.build(story)
            self.snack(self.lang["pdf_success"].format(path=name))
        except Exception as e:
            self.snack(f"PDF: {e}")
        finally:
            try:
                if os.path.exists(tmp_img): os.remove(tmp_img)
            except Exception:
                pass


# ─── Entry Point ────────────────────────────────
if __name__ == "__main__":
    PLCStudioApp().run()
