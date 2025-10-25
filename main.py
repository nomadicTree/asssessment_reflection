import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
from reflection import Reflection
from topic import Topic

SUBJECTS_FILE = "subjects.yaml"
TEMPLATES_DIR = Path("templates")

def load_yaml(file_path: Path):
    """Load a YAML file and return a dictionary. Returns {} if empty or invalid."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if data is None:
            return {}
        return data

def load_all_templates(templates_dir):
    """
    Recursively load all YAML templates in the directory and subdirectories.
    Returns a dict keyed by template id.
    """
    templates_dir = Path(templates_dir)
    templates = {}

    for file_path in templates_dir.rglob("*.yaml"):
        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            template_id = config.get("id")
            if not template_id:
                raise ValueError(f"Template {file_path} has no 'id' field.")
            templates[template_id] = config
    
    return templates

def merge_configs(base, override):
    """Merge override config into base config, deduplicating statements."""
    merged = base.copy()

    # Merge top-level statements
    base_statements = base.get("statements", [])
    override_statements = override.get("statements", [])
    merged["statements"] = list(dict.fromkeys(base_statements + override_statements))

    # Merge question_types
    base_qt = base.get("question_types", {})
    override_qt = override.get("question_types", {})
    merged_qt = base_qt.copy()
    
    for qt_name, qt_data in override_qt.items():
        if qt_name in merged_qt:
            merged_qt[qt_name]["statements"] = list(
                dict.fromkeys(
                    merged_qt[qt_name].get("statements", []) + qt_data.get("statements", [])
                )
            )
            # Merge options if they exist
            base_options = merged_qt[qt_name].get("options", {})
            override_options = qt_data.get("options", {})
            for opt_name, opt_data in override_options.items():
                if opt_name in base_options:
                    base_options[opt_name]["statements"] = list(
                        dict.fromkeys(
                            base_options[opt_name].get("statements", []) + opt_data.get("statements", [])
                        )
                    )
                else:
                    base_options[opt_name] = opt_data
            if base_options:
                merged_qt[qt_name]["options"] = base_options
        else:
            merged_qt[qt_name] = qt_data
    
    merged["question_types"] = merged_qt
    return merged

def load_template(template_id, all_templates, visited=None):
    """
    Recursively load a template by id, merging all inherited templates.
    `all_templates` should be the dict returned by load_all_templates().
    """
    if visited is None:
        visited = set()
    
    if template_id in visited:
        raise ValueError(f"Circular inheritance detected: {template_id}")
    visited.add(template_id)

    template = all_templates.get(template_id)
    if not template:
        raise FileNotFoundError(f"Template '{template_id}' not found in loaded templates.")

    inherits = template.get("inherits")
    if not inherits:
        return template

    # Ensure inherits is a list
    if isinstance(inherits, str):
        inherits = [inherits]

    merged = {}
    for parent_id in inherits:
        parent_template = load_template(parent_id, all_templates, visited)
        merged = merge_configs(merged, parent_template)

    # Merge current template last so it overrides parents
    merged = merge_configs(merged, template)
    return merged
    """
    Load a template YAML file and all its inherited templates recursively,
    merging statements and question_types.
    """
    if loaded is None:
        loaded = {}

    template_file = templates_dir / f"{template_name}.yaml"
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    config = load_yaml(template_file)

    # Fallback for empty file
    if config is None:
        config = {}

    template_id = config.get("id", template_name)
    if template_id in loaded:
        # Avoid circular inheritance
        return loaded[template_id]

    # Start with empty base
    merged_config = {"statements": [], "question_types": {}}

    # Handle inheritance
    inherits = config.get("inherits") or []
    if isinstance(inherits, str):
        inherits = [inherits]

    for parent_name in inherits:
        parent_config = load_template(parent_name, templates_dir, loaded)
        merged_config = merge_configs(merged_config, parent_config)

    # Merge this template's own data
    merged_config = merge_configs(merged_config, config)

    # Cache the loaded template
    loaded[template_id] = merged_config
    return merged_config

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
            key=f"available_marks_{index}"
        )
    with col2:
        achieved_marks = st.number_input(
            "**Marks achieved:**",
            min_value=0,
            step=1,
            max_value=available_marks,
            key=f"achieved_marks_{index}"
        )
    return available_marks, achieved_marks

def input_question_number(index):
    question_number = st.text_input(
        "**Question number:**",
        key=f"question_number_{index}",
        placeholder="E.g., 5.b.ii"
    )
    return question_number

def input_question_image(index, question_number):
    uploaded_file = st.file_uploader("**Upload an image of the question**", type=["png", "jpg", "jpeg"], key=f"uploaded_file{index}")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Question {question_number}", width="content")
        return image

def input_question_type(index, question_type_names):
    selected_question_type_name = st.radio(
        "**Type of question:**",
        question_type_names,
        key=f"question_type_{index}",
    )
    return selected_question_type_name

def select_topics(index, topics):
    selected_topics = st.multiselect(
        "**Which topic(s) does this question assess?**",
        topics,
        format_func=lambda c: c.label(),
        key=f"topics_{index}"
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
            placeholder="Choose options"
        )
        
        # Step 2: show statements only for selected options
        for option in selected_options:
            st.write(f"**{option}:**")
            option_statements = available_options[option].get("statements", [])
            selected_statements_for_option = []
            for j, stmt in enumerate(option_statements):
                checked = st.checkbox(stmt, key=f"option_statement_{index}_{option}_{j}")
                if checked:
                    selected_statements_for_option.append(stmt)
            selected_option_statements[option] = selected_statements_for_option
    return selected_option_statements

def input_written_reflection(index):
    written_reflection = st.text_area(
        "**What could you do differently to improve your response to a question like this?**",
        height=150,
        key=f"future_reflection_{index}"
    ).strip()
    return written_reflection

def render_reflection(index, course_reflection_data, available_topics):
    r = Reflection()
    st.subheader(f"Reflection {index + 1}:")
    core_statements = course_reflection_data.get("statements", [])
    question_types = course_reflection_data.get("question_types", {})
    question_type_names = list(question_types.keys())

    r.question_number = input_question_number(index)
    r.available_marks, r.achieved_marks = input_marks(index)
    render_marks_status_bar(r.marks_percentage())
    r.question_image = input_question_image(index, r.question_number)
    selected_question_type_name = input_question_type(index, question_type_names)
    selected_question_type = question_types[selected_question_type_name]
    available_statements = core_statements + selected_question_type.get("statements", [])
    r.topics = select_topics(index, available_topics)
    r.selected_statements = select_statements(index, available_statements)
    available_options = selected_question_type.get("options", {})
    r.selected_option_statements = select_option_statements(index, available_options)
    r.written_reflection = input_written_reflection(index)
    
    # Save everything in session_state
    st.session_state.reflections[index] = r

    if index + 1 < len(st.session_state.reflections):
        st.divider()

def generate_summary_text(student_name, assessment_name, reflections, general_reflections):
    summary_text = ""
    if student_name:
        summary_text += f"Name: {student_name}\n"
    if assessment_name:
        summary_text += f"Assessment: {assessment_name}\n"
    for r in reflections:
        summary_text += f"Question {r.question_number}\n"
        summary_text += f"  Marks: {r.achieved_marks}/{r.available_marks}\n"
        summary_text += f"  Question type: {r.question_type}\n"
        summary_text += "  Topics:\n"
        if r.topics:
            for topic in r.topics:
                summary_text += f"    - {topic.label()}\n"
        else:
            summary_text += "    - None selected\n"
        summary_text += "  Statements:\n"
        if r.selected_statements:
            for statement in r.selected_statements:
                summary_text += f"    - {statement}\n"
        else:
            summary_text += "    - None selected\n"
        if hasattr(r, 'selected_option_statements') and r.selected_option_statements:
            summary_text += "  Option statements:\n"
            for option, statements in r.selected_option_statements.items():
                summary_text += f"    {option}:\n"
                if statements:
                    for statement in statements:
                        summary_text += f"      - {statement}\n"
                else:
                    summary_text += "      - None selected\n"

        summary_text += f"  Written reflection:\n"
        if r.written_reflection:
            summary_text += f"    {r.written_reflection}\n"
        else:
            summary_text += "    None written\n"

        summary_text += "\n"

        for question in general_reflections:
            summary_text += f"{question}\n  {general_reflections[question]}\n"

    return summary_text.strip()

def apply_styles():
    st.markdown("""
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
    """, unsafe_allow_html=True)

def generate_file_name(student_name, assessment_name, extension):
    file_name = ""
    if student_name:
        file_name += student_name
        if assessment_name:
            file_name += f" - {assessment_name}"
    elif assessment_name:
        file_name += f"{assessment_name}"
    file_name += f" reflection summary.{extension}"
    return file_name.strip()

def main():
    apply_styles()
    st.title("Assessment Reflection")
    st.set_page_config(
        page_title="Assessment Reflection",
    )
    all_templates = load_all_templates(TEMPLATES_DIR)

    subject_courses = load_yaml(SUBJECTS_FILE)

    student_name = st.text_input("**Your name:**").strip()
    assessment_name = st.text_input("**Assessment name:**").strip()

    available_subjects = subject_courses["subjects"]
    selected_subject = st.radio("**Subject:**", list(available_subjects.keys()))

    available_courses = available_subjects[selected_subject]["courses"]
    selected_course = st.radio("**Course:**", list(available_courses.keys()))

    course_info = available_courses[selected_course]
    template_id = course_info.get("template")
    course_reflection_data = load_template(template_id, all_templates)

    available_topics_dict = available_courses[selected_course]["topics"]
    available_topics = [Topic(code=code, **fields) for code, fields in available_topics_dict.items()]

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
            render_reflection(i, course_reflection_data, available_topics)
    if st.button("➕ Add new question", width="content"):
        st.session_state.reflections.append(Reflection())
        st.rerun()

    st.divider()
    # Only show download if at least one reflection exists
    
    if st.session_state.reflections:
        st.header("General reflections")
        general_reflections = {
            "What topics do you need to revise?": "",
            "What mistakes will you try to avoid next time?": "",
            "What strategies or methods could you use next time?": "",
            "What could you change about how you plan or pace your work?": ""
        }
        for i, question in enumerate(general_reflections):
            general_reflections[question] = st.text_area(f"**{question}**", height=150, key=f"general_reflection_{i}").strip()
            summary_text = generate_summary_text(student_name,
                assessment_name,
                st.session_state.reflections,
                general_reflections
            ) 

        st.download_button(
            label="📄 Download summary (TXT)",
            data=summary_text,
            file_name=generate_file_name(student_name, assessment_name, "txt"),
            mime="text/plain",
            width="content"
        )

if __name__ == "__main__":
    main()
