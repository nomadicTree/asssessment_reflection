# templates.py
from pathlib import Path
import os
import yaml
from models import QuestionType, QuestionTypeOption

TEMPLATES_DIR = Path("data/templates")


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_template_file(template_id: str, templates_dir: str) -> str:
    """Recursively search for <template_id>.yaml in templates_dir"""
    for root, _, files in os.walk(templates_dir):
        if f"{template_id}.yaml" in files:
            return os.path.join(root, f"{template_id}.yaml")
    raise FileNotFoundError(f"Template {template_id} not found.")


def merge_configs(base: dict, override: dict) -> dict:
    """Merge statements and question_types"""
    merged = base.copy()

    # Merge top-level statements
    merged["statements"] = list(
        dict.fromkeys(
            base.get("statements", []) + override.get("statements", [])
        )
    )

    # Merge question_types
    merged_qt = base.get("question_types", {}).copy()
    for qt_name, qt_data in override.get("question_types", {}).items():
        if qt_name in merged_qt:
            merged_qt[qt_name]["statements"] = list(
                dict.fromkeys(
                    merged_qt[qt_name].get("statements", [])
                    + qt_data.get("statements", [])
                )
            )
            # merge options if any
            merged_qt[qt_name]["options"] = {
                **merged_qt[qt_name].get("options", {}),
                **qt_data.get("options", {}),
            }
        else:
            merged_qt[qt_name] = qt_data
    merged["question_types"] = merged_qt

    return merged


def load_template(template_id: str, templates_dir: str) -> dict:
    """Load template and handle inheritance recursively"""
    path = find_template_file(template_id, templates_dir)
    config = load_yaml(path)

    merged = config.copy()
    for parent_id in config.get("inherits", []) or []:
        parent_config = load_template(parent_id, templates_dir)
        merged = merge_configs(parent_config, merged)

    return merged


def apply_template_to_course(course, templates_dir=TEMPLATES_DIR):
    """Load the template for this course and populate its question_types, including common statements and options."""
    template_data = load_template(course.template, templates_dir)

    # top-level statements from template (including merged inherited templates)
    top_level_statements = template_data.get("statements", [])

    question_types = []
    for qt_name, qt_data in template_data.get("question_types", {}).items():
        # Merge top-level statements into each QuestionType
        qt_statements = list(
            dict.fromkeys(top_level_statements + qt_data.get("statements", []))
        )

        # Create QuestionTypeOption objects
        options = []
        for opt_name, opt_data in qt_data.get("options", {}).items():
            option_statements = opt_data.get("statements", [])
            options.append(
                QuestionTypeOption(name=opt_name, statements=option_statements)
            )

        # Create the QuestionType object
        question_types.append(
            QuestionType(
                name=qt_name, statements=qt_statements, options=options
            )
        )

    course.question_types = question_types
