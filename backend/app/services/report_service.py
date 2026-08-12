from fastapi import HTTPException

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
)

from app.tools.report import generate_pdf_report



def create_report(
    request: ReportRequest,
) -> ReportResponse:
    """
    Generate report from provided content.
    """


    try:

        result = generate_pdf_report.invoke(
            {
                "report_text": request.content,

                "output_path":
                f"reports/{request.filename}"
            }
        )


        return ReportResponse(

            filename=request.filename,

            path=result,

            message="Report generated successfully"

        )


    except Exception as e:


        raise HTTPException(

            status_code=400,

            detail=f"Report generation failed: {str(e)}"

        )