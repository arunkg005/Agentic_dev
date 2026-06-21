import logging
from xhtml2pdf import pisa

logger = logging.getLogger("NGO-Campaign-Copilot.PDFExporter")

def compile_campaign_plan_pdf(html_content: str, output_path: str) -> bool:
    """Converts the campaign HTML preview to a beautifully formatted PDF."""
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: letter;
        margin: 0.8in;
    }}
    body {{
        font-family: Arial, sans-serif;
        color: #1e293b;
        line-height: 1.5;
        font-size: 10pt;
    }}
    h1 {{
        color: #0f172a;
        font-size: 18pt;
        border-bottom: 2px solid #0d9488;
        padding-bottom: 6px;
        margin-top: 0;
        margin-bottom: 12px;
    }}
    h2 {{
        color: #0d9488;
        font-size: 13pt;
        margin-top: 18px;
        margin-bottom: 8px;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 4px;
        page-break-after: avoid;
    }}
    h3 {{
        color: #1e293b;
        font-size: 10.5pt;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }}
    p, li {{
        font-size: 9.5pt;
        margin-bottom: 6px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
        margin-bottom: 12px;
        font-size: 8.5pt;
    }}
    th, td {{
        border: 1px solid #e2e8f0;
        padding: 6px 8px;
        text-align: left;
    }}
    th {{
        background-color: #f1f5f9;
        font-weight: bold;
        color: #0f172a;
        border-bottom: 2px solid #cbd5e1;
    }}
    ul, ol {{
        margin-top: 4px;
        margin-bottom: 8px;
        padding-left: 20px;
    }}
    hr {{
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 16px 0;
    }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""
    try:
        with open(output_path, "w+b") as f:
            pisa_status = pisa.CreatePDF(styled_html, dest=f)
        if pisa_status.err:
            logger.error("xhtml2pdf error code: %s", pisa_status.err)
            return False
        logger.info("Campaign PDF saved to '%s'.", output_path)
        return True
    except Exception as e:
        logger.error("Error generating PDF: %s", e)
        return False
