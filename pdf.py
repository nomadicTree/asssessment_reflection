from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    ListFlowable,
    ListItem,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def to_bytesio(image_obj):
    """Return a BytesIO buffer from any uploaded/loaded image object."""
    if image_obj is None:
        return None

    # Streamlit UploadedFile has getbuffer()
    if hasattr(image_obj, "getbuffer"):
        return BytesIO(image_obj.getbuffer())

    # Some file-like objects have .read()
    if hasattr(image_obj, "read"):
        return BytesIO(image_obj.read())

    # Already raw bytes
    if isinstance(image_obj, (bytes, bytearray)):
        return BytesIO(image_obj)

    raise TypeError(f"Don't know how to convert {type(image_obj)} to BytesIO")


def create_summary_pdf(ar, output_buffer):
    """
    Generate a PDF summary of an AssessmentReflection.
    `output_buffer` should be a file-like object (e.g., BytesIO).
    """
    doc = SimpleDocTemplate(output_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("<b>Assessment Reflection</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Student & Assessment info
    if ar.student_name:
        elements.append(
            Paragraph(f"<b>Name:</b> {ar.student_name}", styles["Normal"])
        )
    if ar.assessment_name:
        elements.append(
            Paragraph(
                f"<b>Assessment:</b> {ar.assessment_name}", styles["Normal"]
            )
        )
    elements.append(Spacer(1, 8))

    # Question reflections
    elements.append(
        Paragraph("<b>Question Reflections</b>", styles["Heading2"])
    )
    for r in ar.reflections:
        elements.append(
            Paragraph(
                f"<b>Question {r.question_number}</b>", styles["Heading3"]
            )
        )

        # Question image
        if r.question_image:
            try:
                img_buffer = to_bytesio(r.question_image)
                img = Image(img_buffer)
                img._restrictSize(450, 300)
                img.hAlign = "CENTER"
                elements.append(img)
                elements.append(Spacer(1, 6))
            except Exception as e:
                elements.append(
                    Paragraph(
                        f"<i>Could not load question image: {e}</i>",
                        styles["Normal"],
                    )
                )

        # Marks
        marks_str = f"{r.achieved_marks}/{r.available_marks}"
        if r.available_marks > 0:
            marks_str += f" ({r.marks_percentage()}%)"
        elements.append(
            Paragraph(f"<b>Marks:</b> {marks_str}", styles["Normal"])
        )

        # Question type
        if r.question_type:
            elements.append(
                Paragraph(
                    f"<b>Question type:</b> {r.question_type.name}",
                    styles["Normal"],
                )
            )

        # Topics table
        if r.topics:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("<b>Topics:</b>", styles["Normal"]))
            elements.append(Spacer(1, 4))
            topic_table_data = [["Code", "Topic name"]]
            for topic in r.topics:
                topic_table_data.append([topic.code, topic.name])
            topic_table = Table(topic_table_data, colWidths=[40, 400])
            topic_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            elements.append(topic_table)
            elements.append(Spacer(1, 12))

        # Selected statements
        if r.selected_statements:
            elements.append(
                Paragraph("<b>Selected statements:</b>", styles["Normal"])
            )
            statement_items = [
                ListItem(Paragraph(str(s), styles["Normal"]))
                for s in r.selected_statements
                if s
            ]
            if statement_items:
                elements.append(Spacer(1, 4))
                elements.append(
                    ListFlowable(
                        statement_items, bulletType="bullet", leftIndent=10
                    )
                )

        # Selected options
        for option_name, option_points in r.selected_options.items():
            if option_points:
                elements.append(Spacer(1, 6))
                elements.append(
                    Paragraph(f"<b>{option_name}</b>", styles["Normal"])
                )
                option_items = [
                    ListItem(Paragraph(str(p), styles["Normal"]))
                    for p in option_points
                    if p
                ]
                if option_items:
                    elements.append(
                        ListFlowable(
                            option_items, bulletType="bullet", leftIndent=10
                        )
                    )

        elements.append(Spacer(1, 12))
        if r.written_reflection:
            elements.append(
                Paragraph(
                    "<b>What could you do differently to improve your response to a question like this?</b>",
                    styles["Normal"],
                )
            )
            elements.append(Paragraph(r.written_reflection, styles["Normal"]))

    # General reflections
    if getattr(ar, "general_reflections", None):
        elements.append(
            Paragraph("<b>General Reflections</b>", styles["Heading2"])
        )
        for question, answer in ar.general_reflections.items():
            elements.append(Paragraph(f"<b>{question}</b>", styles["Normal"]))
            elements.append(
                Paragraph(answer or "<i>No response</i>", styles["Normal"])
            )
            elements.append(Spacer(1, 6))

    doc.build(elements)
