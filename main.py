from io import BytesIO
import streamlit as st
from PIL import Image
from models import (
    Reflection,
    Topic,
    Course,
    Subject,
    AssessmentReflection,
)
from utils import load_yaml
from templates import apply_template_to_course
from pdf import create_summary_pdf

SUBJECTS_FILE = "./data/subjects.yaml"


def render_marks_status_bar(marks_percentage):
    col1, col2 = st.columns([93, 7])
    with col1:
        st.progress(marks_percentage / 100)
    with col2:
        st.markdown(f"{marks_percentage}%")


def input_marks(index):
    col1, col2 = st.columns([1, 1])
    with col1:
        available_marks = st.number_input(
            "**Marks available:**",
            min_value=0,
            step=1,
            key=f"available_marks_{index}",
        )
    with col2:
        achieved_marks = st.number_input(
            "**Marks achieved:**",
            min_value=0,
            step=1,
            max_value=available_marks,
            key=f"achieved_marks_{index}",
        )
    return available_marks, achieved_marks


def input_question_number(index):
    question_number = st.text_input(
        "**Question number:**",
        key=f"question_number_{index}",
        placeholder="E.g., 5.b.ii",
    )
    return question_number


def input_question_image(index):
    uploaded_file = st.file_uploader(
        "**Upload an image of the question**",
        type=["png", "jpg", "jpeg"],
        key=f"uploaded_file{index}",
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width="content")
        return uploaded_file


def input_question_type(index, available_question_types):
    selected_question_type = st.selectbox(
        "**Type of question:**",
        available_question_types,
        format_func=lambda q: q.name,
        key=f"question_type_{index}",
    )
    return selected_question_type


def select_topics(index, topics):
    selected_topics = st.multiselect(
        "**Which topic(s) does this question assess?**",
        topics,
        format_func=lambda c: c.label(),
        key=f"topics_{index}",
    )
    return selected_topics


def select_statements(index, statements):
    st.markdown("**Select applicable statements:**")
    selected_statements = []
    for i, statement in enumerate(statements):
        checked = st.checkbox(statement, key=f"statement_{index}_{i}")
        if checked:
            selected_statements.append(statement)
    return selected_statements


def select_option_statements(index, available_options):
    selected_option_statements = {}

    if available_options:
        # Step 1: let student choose which options are relevant
        selected_options = st.multiselect(
            "**Select applicable options:**",
            available_options,
            key=f"options_{index}",
            placeholder="Choose options",
            format_func=lambda q: q.name,
        )

        # Step 2: show statements only for selected options
        for option in selected_options:
            st.write(f"**{option.name}:**")
            selected_statements = []
            for j, stmt in enumerate(option.statements):
                checked = st.checkbox(
                    stmt, key=f"option_statement_{index}_{option}_{j}"
                )
                if checked:
                    selected_statements.append(stmt)
            selected_option_statements[option.name] = selected_statements
    return selected_option_statements


def input_written_reflection(index):
    written_reflection = st.text_area(
        "**What could you do differently to improve your response to a question like this?**",
        height=150,
        key=f"future_reflection_{index}",
    ).strip()
    return written_reflection


def render_reflection(index, available_topics, available_question_types):
    r = Reflection()
    st.subheader(f"Reflection {index + 1}:")
    r.question_number = input_question_number(index)
    r.available_marks, r.achieved_marks = input_marks(index)
    render_marks_status_bar(r.marks_percentage())
    r.question_image = input_question_image(index)
    r.question_type = input_question_type(index, available_question_types)
    available_statements = r.question_type.statements
    r.topics = select_topics(index, available_topics)
    r.selected_statements = select_statements(index, available_statements)
    available_options = r.question_type.options
    r.selected_options = select_option_statements(index, available_options)
    r.written_reflection = input_written_reflection(index)

    # Save everything in session_state
    st.session_state.reflections[index] = r

    if index + 1 < len(st.session_state.reflections):
        st.divider()


def apply_styles():
    st.markdown(
        """
        <style>
            /* Base font size for most text elements */
            body, p, span, div, li {
                font-size: 16px !important;
            }

            /* Ensure checkboxes match text size */
            label[data-baseweb="checkbox"] > div:first-child {
                font-size: 16px !important;
            }

            @media print {
            button, st.button, footer, header, .stFileUploader {display: none !important;}
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def load_subjects(file_path):
    data = load_yaml(file_path)

    subjects = []
    for subject_name, subject_data in data["subjects"].items():
        courses = []
        for course_name, course_data in subject_data["courses"].items():
            topics = [
                Topic(code=code, **fields)
                for code, fields in course_data["topics"].items()
            ]
            courses.append(
                Course(
                    name=course_name,
                    template=course_data["template"],
                    topics=topics,
                )
            )
        subjects.append(Subject(name=subject_name, courses=courses))
    return subjects


def main():
    ar = AssessmentReflection()
    apply_styles()
    st.title("Assessment Reflection")
    st.set_page_config(
        page_title="Assessment Reflection",
    )

    subjects = load_subjects(SUBJECTS_FILE)
    ar.student_name = st.text_input("**Your name:**").strip()
    ar.assessment_name = st.text_input("**Assessment name:**").strip()
    ar.subject = st.selectbox(
        "**Subject:**", subjects, format_func=lambda s: s.name
    )
    ar.course = st.selectbox(
        "**Course:**", ar.subject.courses, format_func=lambda c: c.name
    )

    if not ar.course.question_types:
        apply_template_to_course(ar.course)

    st.divider()

    # Initialise reflections if not already in session_state
    if "reflections" not in st.session_state:
        st.session_state.reflections = []

    # If no reflections yet, encourage user to start
    if not st.session_state.reflections:
        st.info("Click **'Add new question'** below to start your reflection.")

    else:
        # Render all current reflections
        for i in range(len(st.session_state.reflections)):
            render_reflection(i, ar.course.topics, ar.course.question_types)
    if st.button("➕ Add new question", use_container_width=True):
        st.session_state.reflections.append(Reflection())
        st.rerun()

    st.divider()
    # Only show download if at least one reflection exists

    if st.session_state.reflections:
        st.header("General reflections")
        ar.general_reflections = {
            "What topics do you need to revise?": "",
            "What mistakes will you try to avoid next time?": "",
            "What strategies or methods could you use next time?": "",
            "What could you change about how you plan or pace your work?": "",
        }

        for i, question in enumerate(ar.general_reflections):
            ar.general_reflections[question] = st.text_area(
                f"**{question}**", height=150, key=f"general_reflection_{i}"
            ).strip()

        if "show_pdf_download" not in st.session_state:
            st.session_state.show_pdf_download = False
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Generate PDF", use_container_width=True):
                st.session_state.show_pdf_download = True

                for r in st.session_state.reflections:
                    ar.reflections.append(r)
        if st.session_state.show_pdf_download:
            pdf_buffer = BytesIO()
            create_summary_pdf(ar, pdf_buffer)
            pdf_buffer.seek(0)
            # Provide a download button with the actual bytes
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name="assessment_reflection.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
