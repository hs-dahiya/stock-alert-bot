import requests, json, os
from datetime import datetime, timezone, timedelta

GIST_ID = os.environ['GIST_ID']
GH_PAT  = os.environ['GH_PAT']
IST     = timezone(timedelta(hours=5, minutes=30))

HEADERS = {
    'Authorization': f'token {GH_PAT}',
    'Accept':        'application/vnd.github.v3+json'
}

def load_full_state() -> dict:
    r = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=HEADERS)
    r.raise_for_status()
    raw = r.json()['files']['seen_filings.json']['content']
    return json.loads(raw)

def save_full_state(state: dict):
    content = json.dumps(state, indent=2)
    r = requests.patch(
        f'https://api.github.com/gists/{GIST_ID}',
        headers=HEADERS,
        json={'files': {'seen_filings.json': {'content': content}}}
    )
    r.raise_for_status()

def load_seen() -> set:
    return set(load_full_state().get('seen', []))

def log_alert(state: dict, filing: dict, materiality: dict) -> dict:
    today = datetime.now(IST).strftime('%Y-%m-%d')
    state.setdefault('alert_log', {}).setdefault(today, [])
    state['alert_log'][today].append({
        'symbol':      filing.get('symbol', ''),
        'category':    filing.get('category', ''),
        'priority':    filing.get('priority_score', 0),
        'materiality': materiality.get('tier'),
        'mat_label':   materiality.get('label', ''),
        'exchange':    filing.get('exchange', ''),
        'time_utc':    datetime.now(timezone.utc).strftime('%H:%M'),
    })
    return state

def prune_old_logs(state: dict, keep_days: int = 7) -> dict:
    from datetime import date
    cutoff = (date.today()).isoformat()
    log = state.get('alert_log', {})
    keep = sorted(log.keys())[-keep_days:] if log else []
    state['alert_log'] = {k: v for k, v in log.items() if k in keep}
    return state
