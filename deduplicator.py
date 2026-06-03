def _similarity(a: str, b: str) -> float:
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)

def fuzzy_deduplicate(nse_filings: list, bse_filings: list, seen_ids: set) -> list:
    nse_new = [f for f in nse_filings if f['id'] not in seen_ids]
    bse_new = [f for f in bse_filings if f['id'] not in seen_ids]

    nse_sigs = [(f['isin'], f['category']) for f in nse_new if f.get('isin')]

    unique_bse = []
    for bf in bse_new:
        if not bf.get('isin'):
            unique_bse.append(bf)
            continue
        is_dup = any(
            bf['isin'] == isin and _similarity(bf['category'], nse_cat) > 0.4
            for isin, nse_cat in nse_sigs
        )
        if not is_dup:
            unique_bse.append(bf)

    return nse_new + unique_bse
