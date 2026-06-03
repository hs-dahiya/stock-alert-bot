import csv, time
from nse_poller        import poll_nse
from bse_poller        import poll_bse
from deduplicator      import fuzzy_deduplicate
from priority_engine   import should_alert, score_filing
from results_analyzer  import analyze_results
from promoter_alert    import is_promoter_filing, format_promoter_alert
from gemini_gate       import needs_gemini
from materiality_engine import load_master, score_materiality, fmt_materiality
from telegram_sender   import send_alert, send_raw
from heartbeat         import smart_ping
from gist_state        import load_full_state, save_full_state, log_alert, prune_old_logs

def load_watchlist(path='watchlist.csv'):
    nse, bse = set(), set()
    with open(path) as f:
        for row in csv.DictReader(f):
            if row.get('NSE_SYMBOL', '').strip():
                nse.add(row['NSE_SYMBOL'].strip().upper())
            if row.get('BSE_CODE', '').strip():
                bse.add(row['BSE_CODE'].strip())
    return nse, bse

def main():
    errors      = []
    alerts_sent = 0

    nse_symbols, bse_codes = load_watchlist()
    master = load_master()
    print(f'[MAIN] Watchlist: {len(nse_symbols)} NSE | {len(bse_codes)} BSE | Master: {len(master)} companies')

    state = load_full_state()
    seen  = set(state.get('seen', []))

    nse_filings = poll_nse(nse_symbols)
    bse_filings = poll_bse(bse_codes)
    print(f'[MAIN] Fetched NSE:{len(nse_filings)} BSE:{len(bse_filings)}')

    new_filings = fuzzy_deduplicate(nse_filings, bse_filings, seen)
    print(f'[MAIN] New after dedup: {len(new_filings)}')

    new_ids = set()

    for filing in new_filings:
        filing['priority_score'] = score_filing(filing)

        if not should_alert(filing, min_score=1):
            new_ids.add(filing['id'])
            continue

        try:
            mat      = score_materiality(filing, master)
            mat_line = fmt_materiality(mat)

            if is_promoter_filing(filing):
                msg = format_promoter_alert(filing)
                if mat_line: msg += f'\n{mat_line}'
                send_raw(msg)

            elif needs_gemini(filing):
                analysis = analyze_results(filing)
                if mat_line: analysis += f'\n{mat_line}'
                send_alert(filing, analysis)

            else:
                send_alert(filing, mat_line)

            state = log_alert(state, filing, mat)
            alerts_sent += 1
            time.sleep(1)

        except Exception as e:
            print(f'[MAIN] Error on {filing["id"]}: {e}')
            errors.append(str(e)[:60])

        new_ids.add(filing['id'])

    state['seen'] = list(seen | new_ids)
    state = prune_old_logs(state, keep_days=7)
    state = smart_ping(len(nse_filings), len(bse_filings), alerts_sent, errors, state)
    save_full_state(state)
    print(f'[MAIN] Done. Alerts sent: {alerts_sent}')

if __name__ == '__main__':
    main()
