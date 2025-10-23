import streamlit as st
import pandas as pd
import json
from pathlib import Path
from question_reflection import Reflection

def render_reflection(index, question_types, available_topics):
    st.subheader(f"Reflection {index + 1}:")
    
    question_number = st.text_input(
        "Question number:",
        key=f"question_number_{index}"
    )
    
    available_marks = st.number_input(
        "Marks available:",
        min_value=0,
        step=1,
        key=f"available_marks_{index}"
    )
    
    achieved_marks = st.number_input(
        "Marks achieved:",
        min_value=0,
        step=1,
        max_value=available_marks,
        key=f"achieved_marks_{index}"
    )
    
    # Select question type
    question_type = st.radio(
        "Type of question:",
        list(question_types.keys()),
        key=f"question_type_{index}"
    )
    
    # Multiselect for topics
    topics = st.multiselect(
        "Which topic(s) does this question assess?",
        available_topics,
        key=f"topics_{index}"
    )
    
    # Dynamically show statements for selected question type
    statements = question_types[question_type].get("statements", [])
    st.write("Select applicable statements:")

    selected_statements = []
    for i, stmt in enumerate(statements):
        checked = st.checkbox(stmt, key=f"statement_{index}_{i}")
        if checked:
            selected_statements.append(stmt)
    
    # Options (e.g., programming constructs)
    options = question_types[question_type].get("options", {})
    selected_option_statements = {}
    
    if options:
        st.write("Select relevant options:")
        # Step 1: let student choose which constructs are relevant
        relevant_options = []
        for option in options.keys():
            if st.checkbox(option, key=f"option_{index}_{option}"):
                relevant_options.append(option)
        
        # Step 2: show statements only for selected constructs
        for option in relevant_options:
            st.write(f"Statements about {option}:")
            option_statements = options[option].get("statements", [])
            selected_statements_for_option = []
            for j, stmt in enumerate(option_statements):
                checked = st.checkbox(stmt, key=f"option_statement_{index}_{option}_{j}")
                if checked:
                    selected_statements_for_option.append(stmt)
            selected_option_statements[option] = selected_statements_for_option
    

    written_reflection = st.text_area(
        "Reflecting on the above, what would you do differently next time to improve your response to a question like this?",
        height=150,
        key=f"future_reflection_{index}"
    )
    
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

def main():
    st.markdown("""
        <style>
            * {
                font-size: 16px !important;   /* sets base font size for everything */
            }
            h1, h2, h3, h4, h5, h6 {
                font-size: revert !important;  /* keeps Streamlit's default heading sizes */
            }
            label[data-baseweb="checkbox"] > div:first-child {
                font-size: 16px !important;    /* ensures checkboxes match the text size */
            }
        </style>
    """, unsafe_allow_html=True)


    st.title("Assessment Reflection")

    subjects_path = Path("./subjects")
    subjects = [d.name.title() for d in subjects_path.iterdir() if d.is_dir()]

    student_name = st.text_input("Enter your name:")
    assessment_name = st.text_input("Enter the assessment name:")
    subject = st.radio("Subject:", subjects)

    courses_path = subjects_path / subject.lower() / "courses"
    courses = [f.name for f in courses_path.iterdir() if f.is_dir()]
    course = st.radio("Course:", courses)
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
        st.info("Click **'Add new reflection'** below to start your reflection.")
    else:
        # Render all current reflections
        for i in range(len(st.session_state.reflections)):
            render_reflection(i, question_types, topic_list)

    # --- Bottom section: Add + Download side by side ---
    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("➕ Add new reflection", use_container_width=True):
            st.session_state.reflections.append(Reflection())
            st.rerun()

    with col2:
        # Only show download if at least one reflection exists
        if st.session_state.reflections:
            summary_text = f"{assessment_name} | {student_name}\n\n"
            for i, r in enumerate(st.session_state.reflections):
                summary_text += f"Question {r.question_number}\n"
                summary_text += f"  Marks available: {r.available_marks}\n"
                summary_text += f"  Marks achieved: {r.achieved_marks}\n"
                summary_text += f"  Question type: {r.question_type}\n"
                summary_text += f"  Topics:\n"
                if r.topics:
                    for topic in r.topics:
                        summary_text += f"    - {topic}\n"
                else:
                    summary_text += "    - None selected\n"
                summary_text += "  Statements:\n"
                if r.selected_statements:
                    for stmt in r.selected_statements:
                        summary_text += f"    - {stmt}\n"
                else:
                    summary_text += "    - None selected\n"
                if hasattr(r, 'selected_option_statements') and r.selected_option_statements:
                    summary_text += f"  Option statements:\n"
                    for option, statements in r.selected_option_statements.items():
                        summary_text += f"    {option}:\n"
                        if statements:
                            for stmt in statements:
                                summary_text += f"      - {stmt}\n"
                        else:
                            summary_text += "      - None selected\n"

                summary_text += f"  Written reflection:\n"
                summary_text += f"    {r.written_reflection}"

            st.download_button(
                label="📄 Download summary (TXT)",
                data=summary_text,
                file_name="reflections_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

if __name__ == "__main__":
    main()