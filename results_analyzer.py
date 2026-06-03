import requests, json, re, os
from google import genai

try:
    import fitz  # PyMuPDF
    FITZ_OK = True
except ImportError:
    FITZ_OK = False

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

PROMPT = '''You are a financial data extraction engine. Extract numbers from this filing.
Return ONLY a JSON object — no prose, no markdown, no backticks.

{
  "revenue_cr": <number or null>,
  "pat_cr": <number or null>,
  "ebitda_margin_pct": <number or null>,
  "eps": <number or null>,
  "period": "Q4 FY26",
  "revenue_yoy_pct": <number or null>,
  "revenue_qoq_pct": <number or null>,
  "pat_yoy_pct": <number or null>,
  "pat_qoq_pct": <number or null>,
  "materiality": "HIGH" or "MEDIUM" or "LOW",
  "red_flags": [],
  "dividend": <number or null>
}

Materiality = HIGH if PAT growth > 15% YoY or major miss/beat.
Red flags: auditor change, going concern, negative cash flow with positive PAT, pledge > 50%, debt spike > 30% QoQ.
'''

def _delta(val):
    if val is None: return 'N/A'
    return f"+{val:.1f}%" if val >= 0 else f"{val:.1f}%"

def _fmt(val, prefix='₹', suffix=' Cr'):
    return f"{prefix}{val}{suffix}" if val is not None else 'N/A'

def analyze_results(filing: dict) -> str:
    pdf_url = filing.get('pdf_url')
    if not pdf_url or not FITZ_OK:
        return ''
    try:
        r = requests.get(pdf_url, timeout=20)
        r.raise_for_status()
        doc = fitz.open(stream=r.content, filetype='pdf')
        text = ''.join(page.get_text() for page in doc[:6])[:5000]
        if len(text.strip()) < 100:
            return ''
    except Exception as e:
        print(f'[Results] PDF fetch failed: {e}')
        return ''
    try:
        resp = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=PROMPT + '\n\nFILING TEXT:\n' + text
        )
        raw = re.sub(r'```json|```', '', resp.text.strip()).strip()
        d   = json.loads(raw)
    except Exception as e:
        print(f'[Results] Gemini failed: {e}')
        return ''

    lines = [f"📊 *{d.get('period','Results')} Snapshot*"]
    if d.get('revenue_cr'):
        lines.append(f"Revenue:  {_fmt(d['revenue_cr'])}  |  YoY: {_delta(d.get('revenue_yoy_pct'))}  |  QoQ: {_delta(d.get('revenue_qoq_pct'))}")
    if d.get('pat_cr'):
        lines.append(f"PAT:      {_fmt(d['pat_cr'])}  |  YoY: {_delta(d.get('pat_yoy_pct'))}  |  QoQ: {_delta(d.get('pat_qoq_pct'))}")
    if d.get('ebitda_margin_pct'):
        lines.append(f"EBITDA Margin:  {d['ebitda_margin_pct']:.1f}%")
    if d.get('eps'):
        lines.append(f"EPS:  ₹{d['eps']}")
    if d.get('dividend'):
        lines.append(f"Dividend:  ₹{d['dividend']}/share")
    lines.append(f"Materiality:  {d.get('materiality','N/A')}")
    flags = d.get('red_flags', [])
    if flags:
        lines.append('⚠️ Red Flags: ' + ' · '.join(flags))
    return '\n'.join(lines)
