from pathlib import Path

from langchain_core.tools import tool


@tool
def generate_pdf_report(
    report_text: str,
    output_path: str,
) -> str:
    """
    Generate a PDF report from text.
    """
    try:
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate
    except ImportError as e:
        print(f"[report] Failed to load reportlab: {e}")
        raise RuntimeError("Local PDF report generation is not supported. Please configure required libraries.") from e

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