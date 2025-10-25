from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from question_reflection import Reflection

def create_reflection_pdf(student_name, assessment_name, reflections, general_reflections, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>Assessment Reflection</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Name:</b> {student_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Assessment:</b> {assessment_name}", styles["Normal"]))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph(f"<b>Question Reflections</b>", styles["Heading2"]))

    for r in reflections:
        marks_str = f"<b>Marks: </b> {r.achieved_marks}/{r.available_marks}"
        if r. available_marks > 0:
            marks_percentage = int((r.achieved_marks / r.available_marks) * 100)
            marks_str += f" ({marks_percentage}%)"
        elements.append(Paragraph(f"<b>Question {r.question_number}</b>", styles["Heading3"]))
        elements.append(Paragraph(marks_str, styles["Normal"]))
        elements.append(Paragraph(f"<b>Question type:</b> {r.question_type}"))
        topics_table_data = [["Topic code", "Topic name"]]
        for t in r.topics:
            topics_table_data.append([[t]])

        topics_table = Table(topics_table_data, colWidths=[80, 400])
        elements.append(topics_table)


    doc.build(elements)

reflection_1 = Reflection(
    "5.b.ii",
    5,
    3,
    "Programming",
    ["1.2.1", "1.2.2"],
    ["Knew the answer", "Killed my boss"],
    {"Iteration": "Attempted iteration"},
    "I must not tell lies"
)

create_reflection_pdf("Jon", "Y12 Autumn 1", [reflection_1], None, "./report.pdf")

