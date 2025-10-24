import streamlit as st
import pandas as pd
import json
from pathlib import Path
from question_reflection import Reflection

def render_reflection(index, question_types, available_topics):
    st.subheader(f"Reflection {index + 1}:")
    
    question_number = st.text_input(
        "**Question number:**",
        key=f"question_number_{index}"
    )

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
    
    # Select question type
    question_type = st.radio(
        "**Type of question:**",
        list(question_types.keys()),
        key=f"question_type_{index}"
    )
    
    # Multiselect for topics
    topics = st.multiselect(
        "**Which topic(s) does this question assess?**",
        available_topics,
        key=f"topics_{index}"
    )
    
    # Dynamically show statements for selected question type
    statements = question_types[question_type].get("statements", [])
    st.markdown("**Select applicable statements:**")

    selected_statements = []
    for i, stmt in enumerate(statements):
        checked = st.checkbox(stmt, key=f"statement_{index}_{i}")
        if checked:
            selected_statements.append(stmt)
    
    # Options (e.g., programming constructs)
    options = question_types[question_type].get("options", {})
    selected_option_statements = {}
    
    if options:
        st.markdown("**Select applicable options:**")
        # Step 1: let student choose which constructs are relevant
        relevant_options = []
        for option in options.keys():
            if st.checkbox(option, key=f"option_{index}_{option}"):
                relevant_options.append(option)
        
        # Step 2: show statements only for selected constructs
        for option in relevant_options:
            st.write(f"**{option}:**")
            option_statements = options[option].get("statements", [])
            selected_statements_for_option = []
            for j, stmt in enumerate(option_statements):
                checked = st.checkbox(stmt, key=f"option_statement_{index}_{option}_{j}")
                if checked:
                    selected_statements_for_option.append(stmt)
            selected_option_statements[option] = selected_statements_for_option
    

    written_reflection = st.text_area(
        "**What could you do differently to improve your response to a question like this?**",
        height=150,
        key=f"future_reflection_{index}"
    ).strip()
    
    # Save everything in session_state
    st.session_state.reflections[index] = Reflection(
        question_number,
        available_marks,
        achieved_marks,
        question_type,
        topics,
        selected_statements,
        selected_option_statements,
        written_reflection
    ) 

    if index + 1 < len(st.session_state.reflections):
        st.divider()

def generate_summary_text(student_name, assessment_name, reflections, knowledge, skills, execution, time):
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
                summary_text += f"    - {topic}\n"
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

        if knowledge:
            summary_text += f"Topics to revise:\n  {knowledge}\n"
        if skills:
            summary_text += f"Strategies/methods for next time:\n  {skills}\n"
        if execution:
            summary_text += f"Mistakes to avoid:\n  {execution}\n"
        if time:
            summary_text += f"Plans and timing:\n  {time}\n"
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
            button, st.button, footer, header {display: none !important;}
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

    subjects_path = Path("./subjects")
    subjects = [d.name.title() for d in subjects_path.iterdir() if d.is_dir()]

    student_name = st.text_input("**Your name:**").strip()
    assessment_name = st.text_input("**Assessment name:**").strip()
    subject = st.radio("**Subject:**", subjects)

    courses_path = subjects_path / subject.lower() / "courses"
    courses = [f.name for f in courses_path.iterdir() if f.is_dir()]
    course = st.radio("**Course:**", courses)
    st.divider()

    # Load topics
    course_path = courses_path / course
    topic_file = course_path / "topics.json"
    with open(topic_file, "r", encoding="utf-8") as f:
        topics = json.load(f)
    topic_list = [f"{t['code']}: {t['name']}" for t in topics]

    # Load question types
    question_types_file = course_path / "question_types.json"
    with open(question_types_file, "r", encoding="utf-8") as f:
        question_types = json.load(f)

    # Initialise reflections if not already in session_state
    if "reflections" not in st.session_state:
        st.session_state.reflections = []

    # If no reflections yet, encourage user to start
    if not st.session_state.reflections:
        st.info("Click **'Add new question'** below to start your reflection.")

    else:
        # Render all current reflections
        for i in range(len(st.session_state.reflections)):
            render_reflection(i, question_types, topic_list)
    if st.button("➕ Add new question", use_container_width=True):
        st.session_state.reflections.append(Reflection())
        st.rerun()

    st.divider()
    # Only show download if at least one reflection exists
    if st.session_state.reflections:
        st.subheader("General reflections")
        knowledge_reflection = st.text_area("**What topics do you need to revise?**", height=150).strip()
        skills_reflection = st.text_area("**What strategies or methods could you use next time?**", height=150).strip()
        execution_reflection = st.text_area("**What mistakes will you try to avoid next time?**", height=150).strip()
        time_reflection = st.text_area("**What would you change about how you plan or pace your work?**", height=150).strip()
        summary_text = generate_summary_text(student_name,
            assessment_name,
            st.session_state.reflections,
            knowledge_reflection,
            skills_reflection,
            execution_reflection,
            time_reflection) 

        st.download_button(
            label="📄 Download summary (TXT)",
            data=summary_text,
            file_name=generate_file_name(student_name, assessment_name, "txt"),
            mime="text/plain",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
