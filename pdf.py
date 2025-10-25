from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


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


def create_summary_pdf(ar, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>Assessment Reflection</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(f"<b>Name:</b> {ar.student_name}", styles["Normal"])
    )
    elements.append(
        Paragraph(f"<b>Assessment:</b> {ar.assessment_name}", styles["Normal"])
    )
    elements.append(Spacer(1, 18))

    elements.append(
        Paragraph("<b>Question Reflections</b>", styles["Heading2"])
    )

    for r in ar.reflections:
        elements.append(
            Paragraph(
                f"<b>Question {r.question_number}</b>", styles["Heading3"]
            )
        )
        marks_str = f"<b>Marks: </b> {r.achieved_marks}/{r.available_marks}"
        if r.marks_percentage():
            marks_str += f" ({r.marks_percentage()}%)"
        elements.append(Paragraph(marks_str, styles["Normal"]))

        if r.question_image:
            img_buffer = to_bytesio(r.question_image)

            if img_buffer:
                img = Image(img_buffer)
                img._restrictSize(450, 300)
                img.hAlign = "CENTER"
                elements.append(img)

        elements.append(Spacer(1, 4))
        elements.append(
            Paragraph(f"<b>Question type:</b> {r.question_type.name}")
        )
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("<b>Topics:</b>", styles["Normal"]))
        elements.append(Spacer(1, 4))
        topic_table_data = [["Code", "Topic name"]]
        for topic in r.topics:
            topic_table_data.append([topic.code, topic.name])
        topic_table = Table(topic_table_data, colWidths=[50, 400])
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

        statement_list_items = [
            ListItem(Paragraph(point, styles["Normal"]))
            for point in r.selected_statements
        ]

        statement_list = ListFlowable(
            statement_list_items,
            bulletType="bullet",
            start=None,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20,
        )
        elements.append(statement_list)

        for option in r.selected_options:
            elements.append(Paragraph(option, styles["Normal"]))
            statement_list_items = [
                ListItem(Paragraph(point, styles["Normal"]))
                for point in r.selected_options[option]
            ]

            statement_list = ListFlowable(
                statement_list_items,
                bulletType="bullet",
                start=None,
                spaceBefore=6,
                spaceAfter=6,
                leftIndent=20,
            )
            elements.append(statement_list)

    doc.build(elements)
