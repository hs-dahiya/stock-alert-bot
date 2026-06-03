import csv, re

def load_master(path='company_master.csv') -> dict:
    master = {}
    try:
        with open(path) as f:
            for row in csv.DictReader(f):
                sym = row.get('SYMBOL', '').strip().upper()
                if not sym: continue
                master[sym] = {
                    'revenue': _num(row.get('ANNUAL_REVENUE_CR')),
                    'pat':     _num(row.get('ANNUAL_PAT_CR')),
                    'mktcap':  _num(row.get('MARKET_CAP_CR')),
                    'sector':  row.get('SECTOR', ''),
                    'fy':      row.get('FY', ''),
                }
    except FileNotFoundError:
        pass
    return master

def _num(val):
    try: return float(str(val).replace(',', '').strip())
    except: return None

def _extract_value(text: str):
    patterns = [
        r'(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)\s*(?:cr|crore)',
        r'([\d,]+(?:\.\d+)?)\s*(?:cr|crore)',
    ]
    for pat in patterns:
        m = re.search(pat, text.lower())
        if m:
            try: return float(m.group(1).replace(',', ''))
            except: pass
    return None

def _tier(pct: float) -> str:
    if pct > 15: return 'VERY HIGH'
    if pct > 5:  return 'HIGH'
    if pct > 1:  return 'MEDIUM'
    return 'LOW'

def score_materiality(filing: dict, master: dict) -> dict:
    sym  = filing.get('symbol', '').upper()
    co   = master.get(sym, {})
    cat  = (filing.get('category', '') + ' ' + filing.get('description', '')).lower()
    desc = filing.get('description', '')
    result = {'tier': None, 'pct': None, 'label': None}

    if any(kw in cat for kw in ['order', 'contract', 'loi', 'work order']):
        val = _extract_value(desc)
        rev = co.get('revenue')
        if val and rev:
            pct = (val / rev) * 100
            fy  = co.get('fy', '')
            result = {'tier': _tier(pct), 'pct': round(pct, 1),
                      'label': f'Order ₹{val:.0f} Cr = {pct:.1f}% of {fy} Revenue (₹{rev:.0f} Cr)'}

    elif any(kw in cat for kw in ['buyback', 'qip', 'preferential', 'rights']):
        val    = _extract_value(desc)
        mktcap = co.get('mktcap')
        if val and mktcap:
            pct = (val / mktcap) * 100
            result = {'tier': _tier(pct), 'pct': round(pct, 1),
                      'label': f'Amount ₹{val:.0f} Cr = {pct:.1f}% of Market Cap'}

    elif any(kw in cat for kw in ['pledge', 'encumbrance']):
        m = re.search(r'(\d+(?:\.\d+)?)\s*%', desc)
        if m:
            p = float(m.group(1))
            tier = 'VERY HIGH' if p > 50 else 'HIGH' if p > 25 else 'MEDIUM' if p > 10 else 'LOW'
            result = {'tier': tier, 'pct': p, 'label': f'Promoter pledge at {p}%'}

    return result

def fmt_materiality(m: dict) -> str:
    if not m.get('tier') or m['tier'] == 'LOW':
        return ''
    icon = {'MEDIUM': '📌', 'HIGH': '🔴', 'VERY HIGH': '⚡'}.get(m['tier'], '')
    return f"{icon} Materiality: {m['tier']} — {m['label']}"
