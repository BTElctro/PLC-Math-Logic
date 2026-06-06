import ast
import json
import os
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from PIL import ImageGrab

# استيراد مكتبات توليد الـ PDF الاحترافية
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 0. نظام اللغات والترجمة الدولي (i18n System)
# ==========================================
languages = {
    "English 🇬🇧": {
        "app_title": "PLC Math & Logic Studio Pro",
        "templates": "Engineering Templates:",
        "choose_template": "--- Choose Template ---",
        "btn_save": "💾 Save",
        "btn_delete": "🗑️ Delete",
        "btn_guide": "📚 Block Guide",
        "btn_shot": "📷 Screenshot",
        "btn_pdf": "📄 Save PDF",
        "equation": "Equation / Logic:",
        "btn_draw": "▶ Draw Blocks (Enter)",
        "btn_preview": "</> Preview & Copy ST",
        "guide_title": "Block Explanations",
        "warn_eq": "Please enter an equation.",
        "shot_success": "Screenshot saved successfully as:\n",
        "pdf_success": "PDF Report generated successfully as:\n",
        "blocks_info": {
            "ADD": "Addition (+)", "SUB": "Subtraction (-)", "MUL": "Multiplication (*)",
            "DIV": "Division (/)", "EXPT": "Exponent / Power (**)", "GT": "Greater Than (>)",
            "LT": "Less Than (<)", "GE": "Greater or Equal (>=)", "LE": "Less or Equal (<=)",
            "EQ": "Equal (==)", "AND": "Logical AND", "OR": "Logical OR", "SQRT": "Square Root"
        }
    },
    "العربية 🇸🇦": {
        "app_title": "استوديو هندسة الـ PLC",
        "templates": ":القوالب الهندسية",
        "choose_template": "--- اختر قالباً جاهزاً ---",
        "btn_save": "💾 حفظ",
        "btn_delete": "🗑️ حذف",
        "btn_guide": "📚 دليل البلوكات",
        "btn_shot": "📷 لقطة شاشة",
        "btn_pdf": "📄 حفظ كـ PDF",
        "equation": ":المعادلة / المنطق",
        "btn_draw": "▶ رسم البلوكات (Enter)",
        "btn_preview": "</> معاينة ونسخ الكود",
        "guide_title": "شرح البلوكات ومعانيها",
        "warn_eq": "الرجاء إدخال معادلة أولاً.",
        "shot_success": "تم حفظ لقطة الشاشة بنجاح باسم:\n",
        "pdf_success": "تم إنشاء تقرير PDF بنجاح باسم:\n",
        "blocks_info": {
            "ADD": "الجمع (+)", "SUB": "الطرح (-)", "MUL": "الضرب (*)",
            "DIV": "القسمة (/)", "EXPT": "الأسس / القوة (**)", "GT": "أكبر من (>)",
            "LT": "أصغر من (<)", "GE": "أكبر من أو يساوي (>=)", "LE": "أصغر من أو يساوي (<=)",
            "EQ": "يساوي (==)", "AND": "بوابة (وَ) المنطقية", "OR": "بوابة (أو) المنطقية", "SQRT": "الجذر التربيعي"
        }
    },
    "Français 🇫🇷": {
        "app_title": "Studio Logique PLC",
        "templates": "Modèles d'ingénierie:",
        "choose_template": "--- Choisir un modèle ---",
        "btn_save": "💾 Enregistrer",
        "btn_delete": "🗑️ Supprimer",
        "btn_guide": "📚 Guide des Blocs",
        "btn_shot": "📷 Capture",
        "btn_pdf": "📄 Sauver PDF",
        "equation": "Équation / Logique:",
        "btn_draw": "▶ Dessiner (Enter)",
        "btn_preview": "</> Aperçu & Copier",
        "guide_title": "Explication des Blocs",
        "warn_eq": "Veuillez entrer une équation.",
        "shot_success": "Capture d'écran enregistrée avec succès sous:\n",
        "pdf_success": "Rapport PDF généré avec succès sous:\n",
        "blocks_info": {
            "ADD": "Addition (+)", "SUB": "Soustraction (-)", "MUL": "Multiplication (*)",
            "DIV": "Division (/)", "EXPT": "Exposant (**)", "GT": "Plus grand que (>)",
            "LT": "Plus petit que (<)", "GE": "Plus grand ou égal (>=)", "LE": "Plus petit ou égal (<=)",
            "EQ": "Égal (==)", "AND": "ET Logique", "OR": "OU Logique", "SQRT": "Racine carrée"
        }
    }
}
current_lang = "English 🇬🇧"

# ==========================================
# 1. نظام إدارة القوالب (JSON)
# ==========================================
DB_FILE = "plc_templates.json"
default_templates = {
    "1. Tank Volume (Cylinder)": "VOLUME = 3.1415 * (RADIUS ** 2) * HEIGHT",
    "2. Spherical Tank Volume": "VOLUME = (4 / 3) * 3.1415 * (RADIUS ** 3)",
    "3. Analog Input Scaling": "SCALEDVAL = ((RAW - MINRAW) / (MAXRAW - MINRAW)) * (MAXSCALE - MINSCALE) + MINSCALE",
    "4. Pump Interlock Safety": "PUMP_RUN = (LEVEL > 20) and (PRESSURE < 5)",
    "5. Liquid Flow Rate (Pipe)": "FLOW_RATE = 3.1415 * ((DIAMETER / 2) ** 2) * VELOCITY",
    "6. Hydraulic Pump Horsepower": "HP = (FLOW_GPM * PRESSURE_PSI) / 1714",
    "7. Celsius to Fahrenheit": "TEMP_F = (TEMP_C * 1.8) + 32"
}

def load_templates():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as file: return json.load(file)
        except Exception: return default_templates.copy()
    else:
        with open(DB_FILE, "w", encoding="utf-8") as file: json.dump(default_templates, file, indent=4)
        return default_templates.copy()

def save_templates_to_file(templates_dict):
    with open(DB_FILE, "w", encoding="utf-8") as file: json.dump(templates_dict, file, indent=4)

templates_db = load_templates()

# ==========================================
# 2. محرك التحليل الهندسي والرسم
# ==========================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BlockGenerator:
    def __init__(self):
        self.blocks = []; self.temp_count = 0
        self.op_map = {
            ast.Add: 'ADD', ast.Sub: 'SUB', ast.Mult: 'MUL', ast.Div: 'DIV', ast.Pow: 'EXPT', 
            ast.Gt: 'GT', ast.Lt: 'LT', ast.GtE: 'GE', ast.LtE: 'LE', ast.Eq: 'EQ', 
            ast.NotEq: 'NE', ast.And: 'AND', ast.Or: 'OR'
        }
    def parse_expression(self, node):
        if isinstance(node, ast.Name): return node.id.upper()
        elif isinstance(node, ast.Constant): return str(node.value)
        elif isinstance(node, ast.BinOp):
            left, right = self.parse_expression(node.left), self.parse_expression(node.right)
            op_name = self.op_map.get(type(node.op), 'UNKNOWN')
            self.temp_count += 1; out_var = f"WIRE_{self.temp_count}"
            self.blocks.append({'op': op_name, 'in1': left, 'in2': right, 'out': out_var})
            return out_var
        elif isinstance(node, ast.Compare):
            left, right = self.parse_expression(node.left), self.parse_expression(node.comparators[0])
            op_name = self.op_map.get(type(node.ops[0]), 'UNKNOWN')
            self.temp_count += 1; out_var = f"WIRE_{self.temp_count}"
            self.blocks.append({'op': op_name, 'in1': left, 'in2': right, 'out': out_var})
            return out_var
        elif isinstance(node, ast.BoolOp):
            left, right = self.parse_expression(node.values[0]), self.parse_expression(node.values[1])
            op_name = self.op_map.get(type(node.op), 'UNKNOWN')
            self.temp_count += 1; out_var = f"WIRE_{self.temp_count}"
            self.blocks.append({'op': op_name, 'in1': left, 'in2': right, 'out': out_var})
            return out_var
        elif isinstance(node, ast.Call):
            func_name = node.func.id.upper()
            arg = self.parse_expression(node.args[0])
            self.temp_count += 1; out_var = f"WIRE_{self.temp_count}"
            self.blocks.append({'op': func_name, 'in1': arg, 'in2': '---', 'out': out_var})
            return out_var
        return "ERR"

def process_equation(equation_str):
    try:
        out_var, expr = equation_str.split('=')
        out_var = out_var.strip().upper()
        expr = expr.strip()
        expr_for_ast = expr.replace(" AND ", " and ").replace(" OR ", " or ")
    except ValueError: return None, "Error: Use format (Output = Expression)"
    try:
        parsed_expr = ast.parse(expr_for_ast, mode='eval')
        generator = BlockGenerator()
        generator.parse_expression(parsed_expr.body)
        if generator.blocks: generator.blocks[-1]['out'] = out_var
        return generator.blocks, None
    except SyntaxError: return None, "Error: Invalid Math Syntax"

def draw_grid(canvas, is_dark):
    grid_color = "#2E3440" if is_dark else "#E9ECEF"
    for i in range(0, 4000, 25): canvas.create_line([(i, 0), (i, 2000)], tag='grid_line', fill=grid_color, dash=(2, 2))
    for i in range(0, 2000, 25): canvas.create_line([(0, i), (4000, i)], tag='grid_line', fill=grid_color, dash=(2, 2))

def get_block_colors(op_name, is_dark):
    if is_dark:
        if op_name in ['AND','OR','GT','LT','GE','LE','EQ','NE']: return {"fill": "#198754", "outline": "#146c43", "text": "white"}
        elif op_name in ['ADD','SUB','MUL','DIV','EXPT']: return {"fill": "#0d6efd", "outline": "#0a58ca", "text": "white"}
        else: return {"fill": "#6f42c1", "outline": "#59359a", "text": "white"}
    else:
        if op_name in ['AND','OR','GT','LT','GE','LE','EQ','NE']: return {"fill": "#D4EDDA", "outline": "#155724", "text": "black"}
        elif op_name in ['ADD','SUB','MUL','DIV','EXPT']: return {"fill": "#CCE5FF", "outline": "#004085", "text": "black"}
        else: return {"fill": "#E2D9F3", "outline": "#381861", "text": "black"}

def draw_blocks(event=None):
    equation = entry_equation.get()
    if not equation.strip():
        if event is None: messagebox.showwarning("Warning", languages[current_lang]["warn_eq"])
        return
    blocks, error = process_equation(equation)
    if error:
        messagebox.showerror("Error", error)
        return

    canvas.delete("all")
    is_dark = ctk.get_appearance_mode() == "Dark"
    bg_color, wire_color, text_color, shadow_color = ("#1E1E1E", "#A6ACCD", "#FFFFFF", "#111111") if is_dark else ("#FFFFFF", "#495057", "#212529", "#DEE2E6")
    canvas.config(bg=bg_color)
    draw_grid(canvas, is_dark)
    
    start_x, start_y, block_w, block_h, spacing_x = 150, 180, 130, 75, 420             

    for index, block in enumerate(blocks):
        x, y = start_x + (index * spacing_x), start_y
        colors = get_block_colors(block['op'], is_dark)
        canvas.create_rectangle(x+5, y+5, x + block_w + 5, y + block_h + 5, fill=shadow_color, outline="")
        canvas.create_rectangle(x, y, x + block_w, y + block_h, fill=colors["fill"], outline=colors["outline"], width=2)
        canvas.create_text(x + (block_w/2), y + (block_h/2), text=block['op'], font=("Segoe UI", 14, "bold"), fill=colors["text"])

        def draw_pin(pin_x, pin_y, text, is_out=False, pin_number=1):
            line_len = 140 
            line_start, line_end = (pin_x + block_w, pin_x + block_w + line_len) if is_out else (pin_x - line_len, pin_x)
            canvas.create_line(line_start, pin_y, line_end, pin_y, arrow=tk.LAST, width=2.5, fill=wire_color)
            node_x = pin_x + block_w if is_out else pin_x
            canvas.create_oval(node_x-4, pin_y-4, node_x+4, pin_y+4, fill=bg_color, outline=colors["outline"], width=2)
            
            text_y = pin_y - 12
            if is_out:
                text_x = line_start + (line_len / 2); anchor = "s"; t_color = "#FF4C4C"; font_style = ("Segoe UI", 12, "bold")
            else:
                text_x = line_start + (line_len / 2)
                if pin_number == 1:
                    text_y = pin_y - 10; anchor = "s"
                else:
                    text_y = pin_y + 10; anchor = "n"
                
                if str(text).startswith("WIRE_"):
                    t_color = "#7F8C8D" if is_dark else "#95A5A6"; font_style = ("Segoe UI", 11, "italic")
                else:
                    t_color = text_color; font_style = ("Segoe UI", 12, "normal")

            canvas.create_text(text_x, text_y, text=text, anchor=anchor, font=font_style, fill=t_color)

        draw_pin(x, y + 25, block['in1'], is_out=False, pin_number=1)
        if block['in2'] != '---': draw_pin(x, y + 50, block['in2'], is_out=False, pin_number=2)
        draw_pin(x, y + 37.5, block['out'], is_out=True)
        
    canvas.config(scrollregion=canvas.bbox("all"))

# ==========================================
# 3. ميزة حفظ لقطات الشاشة والـ PDF
# ==========================================
def capture_canvas_image():
    equation = entry_equation.get().strip()
    root.update()
    x = root.winfo_rootx() + canvas_frame.winfo_x()
    y = root.winfo_rooty() + canvas_frame.winfo_y()
    w = canvas_frame.winfo_width()
    h = canvas_frame.winfo_height()
    
    clean_name = equation.split('=')[0].strip().upper() if '=' in equation else "FBD_Output"
    filename = f"Capture_{clean_name}.png"
    
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(filename)
    return filename

def take_canvas_screenshot():
    equation = entry_equation.get().strip()
    if not equation:
        messagebox.showwarning("Warning", languages[current_lang]["warn_eq"])
        return
    filename = capture_canvas_image()
    messagebox.showinfo("Screenshot", languages[current_lang]["shot_success"] + filename)

def export_to_pdf_report():
    equation = entry_equation.get().strip()
    if not equation:
        messagebox.showwarning("Warning", languages[current_lang]["warn_eq"])
        return
        
    temp_img_file = capture_canvas_image()
    clean_name = equation.split('=')[0].strip().upper() if '=' in equation else "REPORT"
    pdf_filename = f"Report_{clean_name}.pdf"
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, spaceAfter=15, textColor='#0D6EFD')
    meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, spaceAfter=15, textColor='#555555')
    eq_style = ParagraphStyle('EqStyle', parent=styles['Code'], fontName='Courier-Bold', fontSize=12, spaceAfter=25, textColor='#198754', wordWrap='LTR')
    
    story.append(Paragraph(f"PLC FBD GENERATOR REPORT: {clean_name}", title_style))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated on: {current_time} | System Status: OK", meta_style))
    
    story.append(Paragraph(f"<b>Target Logic Equation:</b> {equation.upper()}", eq_style))
    story.append(Spacer(1, 15))
    
    try:
        story.append(Paragraph("<b>Visual Function Block Diagram (FBD):</b>", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Image(temp_img_file, width=530, height=260))
    except Exception as e:
        story.append(Paragraph(f"Error embedding diagram image: {str(e)}", styles['Normal']))
        
    doc.build(story)
    messagebox.showinfo("PDF Export", languages[current_lang]["pdf_success"] + pdf_filename)

# ==========================================
# 4. لوحة أزرار العمليات الحسابية والمنطقية
# ==========================================
def insert_operator(operator_str):
    current_idx = entry_equation.index(tk.INSERT)
    entry_equation.insert(current_idx, f" {operator_str} ")
    entry_equation.focus()

# ==========================================
# 5. النوافذ المنبثقة وكود المعاينة
# ==========================================
def open_guide_dialog():
    dialog = ctk.CTkToplevel(root); dialog.title(languages[current_lang]["guide_title"]); dialog.geometry("450x550")
    dialog.transient(root); dialog.grab_set()
    ctk.CTkLabel(dialog, text=languages[current_lang]["guide_title"], font=("Segoe UI", 18, "bold"), text_color="#0D6EFD").pack(pady=15)
    scroll_frame = ctk.CTkScrollableFrame(dialog, width=400, height=450); scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
    blocks_info = languages[current_lang]["blocks_info"]
    for block_name, explanation in blocks_info.items():
        row = ctk.CTkFrame(scroll_frame, fg_color="transparent"); row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=f"[{block_name}]", font=("Consolas", 14, "bold"), width=70, anchor="w", text_color="#198754").pack(side="left")
        align = "e" if current_lang == "العربية 🇸🇦" else "w"
        ctk.CTkLabel(row, text=explanation, font=("Segoe UI", 14), anchor=align).pack(side="right" if current_lang == "العربية 🇸🇦" else "left", fill="x", expand=True)

def open_data_type_dialog():
    equation = entry_equation.get()
    if not equation.strip(): 
        messagebox.showwarning("Warning", languages[current_lang]["warn_eq"])
        return
    try:
        output_var, expression = equation.split('=')
        output_var = output_var.strip().upper(); expression = expression.strip().upper()
        inputs = set()
        parsed_expr = ast.parse(expression.replace(" AND ", " and ").replace(" OR ", " or "), mode='eval')
        for node in ast.walk(parsed_expr):
            if isinstance(node, ast.Name) and node.id.upper() not in ['SQRT', 'ABS', 'SIN', 'COS']: inputs.add(node.id.upper())
    except Exception: return messagebox.showerror("Error", "Could not parse equation.")

    dialog = ctk.CTkToplevel(root); dialog.title("Export ST Code Preview"); dialog.geometry("550x600")
    dialog.transient(root); dialog.grab_set()
    
    ctk.CTkLabel(dialog, text="1. Variable Types:", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=10)
    frame_vars = ctk.CTkScrollableFrame(dialog, height=150); frame_vars.pack(fill="x", padx=20)
    var_types = {}

    def update_preview(*args):
        st_code = "FUNCTION_BLOCK Logic_Block\n\nVAR_INPUT\n"
        for var in sorted(inputs): st_code += f"    {var} : {var_types[var].get()};\n"
        st_code += "END_VAR\n\nVAR_OUTPUT\n"
        st_code += f"    {output_var} : {var_types[output_var].get()};\n"
        st_code += "END_VAR\n\n// The Logic\n"
        st_code += f"{output_var} := {expression};\n\nEND_FUNCTION_BLOCK"
        text_preview.configure(state="normal"); text_preview.delete("1.0", tk.END); text_preview.insert(tk.END, st_code)
        text_preview.configure(state="disabled"); dialog.st_code_cache = st_code 

    def add_row(parent, var_name, is_out=False):
        row = ctk.CTkFrame(parent, fg_color="transparent"); row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=f"{var_name} (Out)" if is_out else var_name, width=150, anchor="w", font=("Segoe UI", 14)).pack(side="left")
        default_type = "BOOL" if any(k in var_name.upper() for k in ['PUMP', 'RUN', 'CMD', 'STATUS']) else "REAL"
        combo = ctk.CTkComboBox(row, values=["REAL", "INT", "BOOL", "DINT", "WORD"], width=120, command=update_preview)
        combo.set(default_type); combo.pack(side="left"); var_types[var_name] = combo

    for var in sorted(inputs): add_row(frame_vars, var)
    add_row(frame_vars, output_var, is_out=True)

    ctk.CTkLabel(dialog, text="2. Live Code Preview:", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(20,10))
    text_preview = ctk.CTkTextbox(dialog, height=200, font=("Consolas", 14), fg_color="#1E1E1E", text_color="#A6ACCD")
    text_preview.pack(fill="both", expand=True, padx=20); update_preview()

    def copy_code():
        root.clipboard_clear(); root.clipboard_append(dialog.st_code_cache)
        messagebox.showinfo("Success", "ST Code copied to clipboard!"); dialog.destroy()

    ctk.CTkButton(dialog, text="Copy ST Code", font=("Segoe UI", 14, "bold"), fg_color="#198754", hover_color="#146c43", command=copy_code).pack(pady=20)

# ==========================================
# 6. دوال الواجهة والتحكم
# ==========================================
def update_ui_language(*args):
    global current_lang
    current_lang = lang_var.get(); lang_dict = languages[current_lang]
    root.title(lang_dict["app_title"])
    lbl_templates.configure(text=lang_dict["templates"])
    combo_templates.set(lang_dict["choose_template"])
    btn_save.configure(text=lang_dict["btn_save"])
    btn_delete.configure(text=lang_dict["btn_delete"])
    btn_guide.configure(text=lang_dict["btn_guide"])
    btn_shot.configure(text=lang_dict["btn_shot"])
    btn_pdf.configure(text=lang_dict["btn_pdf"])
    lbl_eq.configure(text=lang_dict["equation"])
    btn_draw.configure(text=lang_dict["btn_draw"])
    btn_preview.configure(text=lang_dict["btn_preview"])

def toggle_theme():
    ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
    if entry_equation.get().strip(): draw_blocks(event="theme")
    else: canvas.delete("all"); draw_grid(canvas, ctk.get_appearance_mode() == "Dark")

def on_template_select(choice):
    if choice in templates_db:
        entry_equation.delete(0, tk.END); entry_equation.insert(0, templates_db[choice]); draw_blocks()

def save_custom_template():
    current_eq = entry_equation.get().strip()
    if "=" not in current_eq: return messagebox.showerror("Error", "Please enter a valid equation.")
    template_name = simpledialog.askstring("Save Template", "Enter template name:", parent=root)
    if template_name:
        templates_db[template_name] = current_eq; save_templates_to_file(templates_db)
        combo_templates.configure(values=list(templates_db.keys())); combo_templates.set(template_name)
        messagebox.showinfo("Success", f"Template '{template_name}' saved!")

def delete_custom_template():
    selected = combo_templates.get()
    if selected in default_templates: return messagebox.showwarning("Warning", "Cannot delete core engineering templates.")
    if selected not in templates_db: return
    confirm = messagebox.askyesno("Confirm", f"Delete template '{selected}'?")
    if confirm:
        del templates_db[selected]; save_templates_to_file(templates_db)
        combo_templates.configure(values=list(templates_db.keys()))
        combo_templates.set("--- Choose Template ---")
        entry_equation.delete(0, tk.END); canvas.delete("all")
        draw_grid(canvas, ctk.get_appearance_mode() == "Dark")

# ==========================================
# 7. بناء الواجهة الرسومية الكاملة (CTk GUI)
# ==========================================
root = ctk.CTk()
root.geometry("1150x850")
root.minsize(850, 700) 

frame_top = ctk.CTkFrame(root, corner_radius=10)
frame_top.pack(fill="x", padx=20, pady=20)

row1 = ctk.CTkFrame(frame_top, fg_color="transparent")
row1.pack(fill="x", padx=20, pady=(15, 5))

ctk.CTkButton(row1, text="🌙 / ☀️ Mode", width=100, border_width=2, fg_color="transparent", text_color=("black", "white"), font=("Segoe UI", 12, "bold"), command=toggle_theme).pack(side="right", padx=5)

lang_var = ctk.StringVar(value="English 🇬🇧")
lang_menu = ctk.CTkOptionMenu(row1, variable=lang_var, values=list(languages.keys()), command=update_ui_language, width=130)
lang_menu.pack(side="right", padx=5)

btn_guide = ctk.CTkButton(row1, text="", width=120, fg_color="#6f42c1", hover_color="#59359a", font=("Segoe UI", 12, "bold"), command=open_guide_dialog)
btn_guide.pack(side="right", padx=5)

btn_shot = ctk.CTkButton(row1, text="", width=120, fg_color="#00A896", hover_color="#028074", font=("Segoe UI", 12, "bold"), command=take_canvas_screenshot)
btn_shot.pack(side="right", padx=5)

btn_pdf = ctk.CTkButton(row1, text="", width=120, fg_color="#E63946", hover_color="#D62828", font=("Segoe UI", 12, "bold"), command=export_to_pdf_report)
btn_pdf.pack(side="right", padx=5)

# القوالب الهندسية
row2 = ctk.CTkFrame(frame_top, fg_color="transparent")
row2.pack(fill="x", padx=20, pady=5)

lbl_templates = ctk.CTkLabel(row2, text="", font=("Segoe UI", 14, "bold"))
lbl_templates.pack(side="left", padx=(0, 10))
combo_templates = ctk.CTkComboBox(row2, values=list(templates_db.keys()), width=380, font=("Segoe UI", 14), command=on_template_select)
combo_templates.pack(side="left", padx=5)
btn_save = ctk.CTkButton(row2, text="", width=80, fg_color="#FD7E14", hover_color="#E0690C", font=("Segoe UI", 12, "bold"), command=save_custom_template)
btn_save.pack(side="left", padx=5)
btn_delete = ctk.CTkButton(row2, text="", width=80, fg_color="#DC3545", hover_color="#BB2D3B", font=("Segoe UI", 12, "bold"), command=delete_custom_template)
btn_delete.pack(side="left", padx=5)

# خانة إدخال المعادلة
row3 = ctk.CTkFrame(frame_top, fg_color="transparent")
row3.pack(fill="x", padx=20, pady=5)

lbl_eq = ctk.CTkLabel(row3, text="", font=("Segoe UI", 16, "bold"))
lbl_eq.pack(anchor="center", pady=(0, 2))
entry_equation = ctk.CTkEntry(row3, font=("Consolas", 20), justify="center", height=50, border_width=2)
entry_equation.pack(fill="x", expand=True, padx=20)
root.bind('<Return>', draw_blocks)

# لوحة المفاتيح الهندسية
row_keypad = ctk.CTkFrame(frame_top, fg_color="transparent")
row_keypad.pack(pady=(2, 8))

operators = [
    ("+", "+"), ("-", "-"), ("*", "*"), ("/", "/"), ("**", "**"),
    ("=", "="), ("(", "("), (")", ")"), ("and", "and"), ("or", "or")
]

for op_label, op_val in operators:
    color = "#4A5568" if op_label in ["(", ")", "="] else ("#0D6EFD" if op_label in ["and", "or"] else "#2D3748")
    btn_op = ctk.CTkButton(
        row_keypad, text=op_label, width=55, height=32, 
        fg_color=color, font=("Consolas", 14, "bold"),
        command=lambda v=op_val: insert_operator(v)
    )
    btn_op.pack(side="left", padx=3)

# أزرار التنفيذ
row4 = ctk.CTkFrame(frame_top, fg_color="transparent")
row4.pack(pady=(0, 10))

btn_draw = ctk.CTkButton(row4, text="", height=40, font=("Segoe UI", 14, "bold"), fg_color="#198754", hover_color="#146c43", command=draw_blocks)
btn_draw.pack(side="left", padx=10)
btn_preview = ctk.CTkButton(row4, text="", height=40, font=("Segoe UI", 14, "bold"), fg_color="#0D6EFD", hover_color="#0B5ED7", command=open_data_type_dialog)
btn_preview.pack(side="left", padx=10)

# مساحة العرض الرسومية المخططة
canvas_frame = ctk.CTkFrame(root, corner_radius=15)
canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 5))

h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

canvas = tk.Canvas(canvas_frame, highlightthickness=0, yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
canvas.pack(side=tk.LEFT, fill="both", expand=True)
v_scroll.config(command=canvas.yview); h_scroll.config(command=canvas.xview)

# ==========================================
# 8. شريط الدعاء السفلي الاحترافي ذو الخلفية الضبابية/المعتمة
# ==========================================
frame_dua = ctk.CTkFrame(root, height=45, corner_radius=0, fg_color=("#1A1F2C", "#111622"))
frame_dua.pack(fill="x", side="bottom", pady=(5, 0))

lbl_dua = ctk.CTkLabel(
    frame_dua, 
    text="❤️ارجوا من كل شخص استعمل البرنامج ان يدعو لي ولكل من ساهم في تطويره بالرحمة والمغفرة  ", 
    font=("Segoe UI", 14, "bold"), 
    text_color="#E2E8F0",
    justify="center"
)
lbl_dua.pack(expand=True, fill="both", pady=5)

update_ui_language()
draw_grid(canvas, True)

root.mainloop()