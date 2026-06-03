import os
from datetime import datetime, timezone, timedelta
from gist_state import load_full_state
from telegram_sender import send_digest

IST = timezone(timedelta(hours=5, minutes=30))

CATEGORY_EMOJI = {
    'financial results': '📊', 'quarterly results': '📊',
    'order': '📦', 'contract': '📦',
    'dividend': '💰',
    'promoter': '🔍', 'pledge': '🔍', 'insider': '🔍',
    'buyback': '🔁',
    'board meeting': '🏛',
}

def _emoji(cat: str) -> str:
    c = cat.lower()
    for k, e in CATEGORY_EMOJI.items():
        if k in c: return e
    return '🔔'

def send():
    state = load_full_state()
    today = datetime.now(IST).strftime('%Y-%m-%d')
    log   = state.get('alert_log', {}).get(today, [])
    date_str = datetime.now(IST).strftime('%d %b %Y')

    if not log:
        send_digest(f'📋 *Daily Digest — {date_str}*\nNo material filings today.')
        return

    # Very high materiality first
    very_high = [e for e in log if e.get('materiality') == 'VERY HIGH']
    groups    = {}
    for entry in log:
        groups.setdefault(entry.get('category', 'Other'), []).append(entry)

    lines = [f'📋 *Daily Filing Digest — {date_str}*', '─' * 32]

    if very_high:
        lines.append(f'\n⚡ *Very High Materiality ({len(very_high)})*')
        for e in very_high:
            lines.append(f"  · {e['symbol']}  —  {e.get('mat_label','')}")

    for cat, entries in sorted(groups.items()):
        emoji = _emoji(cat)
        lines.append(f'\n{emoji} *{cat} ({len(entries)})*')
        for e in entries:
            mat = f"  |  {e['materiality']}" if e.get('materiality') and e['materiality'] != 'LOW' else ''
            lines.append(f"  · {e['symbol']}{mat}")

    total_syms = len(set(e['symbol'] for e in log))
    lines.append(f'\nTotal alerts: {len(log)}  |  Stocks active: {total_syms}')

    send_digest('\n'.join(lines))

if __name__ == '__main__':
    send()
