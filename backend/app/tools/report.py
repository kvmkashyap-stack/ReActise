from pathlib import Path

from langchain_core.tools import tool
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


@tool
def generate_pdf_report(
    report_text: str,
    output_path: str,
) -> str:
    """
    Generate a PDF report from text.
    """

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            report_text.replace("\n", "<br/>"),
            styles["BodyText"],
        )
    ]

    document.build(story)

    return output_path