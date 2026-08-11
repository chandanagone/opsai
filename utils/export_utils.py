"""Export helpers: CSV download bytes and printable HTML report generation."""

from datetime import datetime
import pandas as pd


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    if df is None or df.empty:
        df = pd.DataFrame({"Message": ["No data available"]})
    return df.to_csv(index=False).encode("utf-8")


def build_html_report(title: str, subtitle: str, sections: list) -> str:
    """
    sections: list of dicts like:
        {"heading": "KPIs", "type": "kpi", "data": {"Total Assets": 24, ...}}
        {"heading": "Work Orders", "type": "table", "data": dataframe}
        {"heading": "Notes", "type": "text", "data": "some text"}
    Returns a full standalone printable HTML document (string).
    """
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; margin: 40px; }}
    h1 {{ color: #0b192e; margin-bottom: 0; }}
    .subtitle {{ color: #64748b; margin-top: 4px; }}
    .meta {{ color: #94a3b8; font-size: 12px; margin-bottom: 30px; }}
    h2 {{ color: #0b192e; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 36px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; font-size: 13px; }}
    th {{ background-color: #f5f7fb; color: #0b192e; }}
    .kpi-grid {{ display: flex; flex-wrap: wrap; gap: 16px; margin-top: 10px; }}
    .kpi-card {{ border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 20px; min-width: 160px; }}
    .kpi-value {{ font-size: 22px; font-weight: 700; color: #0b192e; }}
    .kpi-label {{ font-size: 12px; color: #64748b; }}
    @media print {{
        body {{ margin: 15px; }}
        h2 {{ page-break-after: avoid; }}
        table {{ page-break-inside: auto; }}
    }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="subtitle">{subtitle}</div>
<div class="meta">Generated on {generated_at}</div>
"""]

    for section in sections:
        heading = section.get("heading", "")
        s_type = section.get("type", "text")
        data = section.get("data")
        parts.append(f"<h2>{heading}</h2>")
        if s_type == "kpi" and isinstance(data, dict):
            parts.append("<div class='kpi-grid'>")
            for k, v in data.items():
                parts.append(
                    f"<div class='kpi-card'><div class='kpi-value'>{v}</div>"
                    f"<div class='kpi-label'>{k}</div></div>"
                )
            parts.append("</div>")
        elif s_type == "table" and isinstance(data, pd.DataFrame):
            if data.empty:
                parts.append("<p>No records available.</p>")
            else:
                parts.append(data.to_html(index=False, border=0))
        else:
            parts.append(f"<p>{data}</p>")

    parts.append("</body></html>")
    return "\n".join(parts)
