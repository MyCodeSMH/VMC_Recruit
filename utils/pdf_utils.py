import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "fonts/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", "fonts/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", "fonts/DejaVuSans-BoldOblique.ttf"))

from reportlab.pdfbase.pdfmetrics import registerFontFamily
import pdb

registerFontFamily(
    "DejaVu",
    normal="DejaVu",
    bold="DejaVu-Bold",
    italic="DejaVu-Italic",
    boldItalic="DejaVu-BoldItalic"
)

# -----------------------------
# SECTION DETECTION LOGIC
# -----------------------------
SECTION_MAP = {
    "missing skills/requirements": "missing",
    "strengths present in the resume": "strengths",
    "suggestions for optimization": "suggestions"
}

title_style = ParagraphStyle(
    "title",
    fontName="DejaVu",
    fontSize=16,
    spaceAfter=12
)

heading_style = ParagraphStyle(
    "heading",
    fontName="DejaVu",
    fontSize=13,
    spaceBefore=10,
    spaceAfter=6
)

body_style = ParagraphStyle(
    "body",
    fontName="DejaVu",
    fontSize=10,
    leading=14
)

def clean_text(text: str) -> str:
    # Remove markdown headings (#, ##, ### ...)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove bold/italic markdown (**text**, *text*)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Remove stray markdown bullets if needed (optional)
    text = text.replace("•", "■")

    # Normalize weird spacing
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

# -----------------------------
# ICONS (boxed style simulation)
# -----------------------------
def tick_box(text):
    return f"<font color='green'><b>✔</b></font> {text}" if len(text.strip())>0 else ''

def cross_box(text):
    return f"<font color='red'><b>✘</b></font> {text}" if len(text.strip())>0 else ''

def neutral(text):
    return f"<font color='blue'><b>■</b></font> {text}" if len(text.strip())>0 else ''

def strip_numbering(line: str) -> str:
    return re.sub(r"^\d+[\.\)]\s+", "", line).strip()


def normalize(line):
    return line.strip().lower().replace("—", "-")

def parse_sections(text):
    sections = {
        "strengths": [],
        "missing": [],
        "suggestions": []
    }

    flag=False
    # for key in SECTION_MAP:
    #     seen[key]=False

    current = None

    for raw_line in text.split("\n"):
        line = normalize(raw_line)

        # detect section header
        matched_section = None
        for key in SECTION_MAP:
            if key in line:
                flag=True
                matched_section = SECTION_MAP[key]
                current = matched_section
                break

        # collect bullets
        # if (line.startswith("❌") or line.startswith("✅") or line.startswith('☒') or re.match(r"^\d+[\.\)]\s+",line)) and current:
        #     item = raw_line.replace("❌", "").replace("✅", "").replace('☒',"").strip()
        #     if re.match(r"^\d+[\.\)]\s+",line):
        #         item=strip_numbering(item)
        #     sections[current].append(item)
        if flag and len(line.strip())>0:
            item=(' ').join(line.split(' ')[1:]).strip()
            sections[current].append(item)

    return sections



# -----------------------------
# FORMATTERS
# -----------------------------
def format_section(section, items):
    if section == "missing":
        return "<br/>".join([cross_box(i) for i in items])

    if section == "strengths":
        return "<br/>".join([tick_box(i) for i in items])


    return "<br/>".join([neutral(i) for i in items])


def save_string_to_pdf(text,output_filename,candidate_file_name,position):

    # pdb.set_trace()
    text=clean_text(text)
    sections = parse_sections(text)
    doc = SimpleDocTemplate(output_filename)

    # -----------------------------
    # BUILD PDF
    # -----------------------------
    content = []
    
    content.append(Paragraph("Resume vs Job Description Analysis", title_style))
    if len(position)==0:
        content.append(Paragraph(f"for Resume:{candidate_file_name}<br/><br/>", body_style))
    else:
        content.append(Paragraph(f"for Resume:{candidate_file_name} and position: {position}<br/><br/>", body_style))

    mapping_titles = {
        "missing": "Missing Skills / Requirements",
        "strengths": "Strengths",
        "suggestions": "Suggestions for Optimization"
    }

    for key in ["strengths", "missing", "suggestions"]:
        content.append(Paragraph(mapping_titles[key]+"<br/>", heading_style))
        content.append(Paragraph(format_section(key, sections[key][1:]), body_style))
        content.append(Spacer(1, 10))

    doc.build(content)


    # def save_string_to_pdf(text, filename="output.pdf"):
        # doc = SimpleDocTemplate(filename, pagesize=letter)
        # styles = getSampleStyleSheet()
        # style = styles["Normal"]
        # style.fontName = "DejaVu"
        # styles["Heading1"].fontName = "DejaVu-Bold"

        # Convert newlines to HTML breaks so Paragraph renders them
        # formatted_text = text.replace("\n", "<br/>")

        
        # paragraph = Paragraph(formatted_text, style)
        # doc.build([paragraph])