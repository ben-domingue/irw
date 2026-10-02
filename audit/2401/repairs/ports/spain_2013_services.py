"""Python port of data/spain_2013_services.do (#2401).

No Stata on the audit machine. Rather than re-coding the tables, this reads the .do
itself and interprets the few statements it uses before each reshape (keep; gen byte
X = V != 0; drop; replace V = ./k if COND; foreach var of varlist ... { ... }), with
Stata's missing-value comparisons, then reshapes each block's `question_cols` long.

    python3 spain_2013_services.py DO_FILE RAW_DA2986 OUT_DIR

Checked three ways: (1) run on the pre-#2401 script with the uncommitted
`foreach var of varlist p*` edit, it reproduces byte for byte the 8 CSVs Ben built
with Stata from that edit on 2026-09-28; (2) run on origin/main's script, every item
of 5 of the tables matches live (the other 5 differ only on items whose code 0 live
already had as missing); (3) run on this PR's script, an aggregate per-item
fingerprint of (id, resp, cov_sex, cov_age) matches live on every item except the
ones the PR changes.

Source: CIS Estudio 2986 (MD2986.zip: DA2986 data, ES2986 SPSS syntax/codebook),
https://www.cis.es/
"""
import re, sys, os
import pandas as pd, numpy as np

def stata_cond(d, cond):
    # conditions used: `v == k`, inlist(v, a, b), missing(v) & asked & p != 1 ...
    mask = pd.Series(True, index=d.index)
    for term in [t.strip() for t in cond.split('&')]:
        m = re.fullmatch(r'inlist\((\w+), ([\d, ]+)\)', term)
        if m: mask &= d[m[1]].isin([int(x) for x in m[2].split(',')]); continue
        m = re.fullmatch(r'missing\((\w+)\)', term)
        if m: mask &= d[m[1]].isna(); continue
        m = re.fullmatch(r'(\w+) (==|!=) (\d+)', term)
        if m:
            e = d[m[1]] == int(m[3])        # NaN == k is False, NaN != k is True, as in Stata
            mask &= e if m[2] == '==' else ~e; continue
        m = re.fullmatch(r'(\w+)', term)
        if m: mask &= d[m[1]].fillna(1).astype(bool); continue   # Stata: nonzero (incl .) is true
        raise ValueError(term)
    return mask

def execute(d, lines):
    i = 0
    while i < len(lines):
        l = lines[i].strip(); i += 1
        if not l or l.startswith('*'): continue
        m = re.fullmatch(r'foreach var of varlist (.*) \{', l)
        if m:
            body = []
            while lines[i].strip() != '}': body.append(lines[i]); i += 1
            i += 1
            vs = [c for c in d.columns if c.startswith('p')] if m[1].strip() == 'p*' else m[1].split()
            for v in vs:
                d = execute(d, [b.replace('`var\'', v) for b in body])
            continue
        m = re.fullmatch(r'replace (\w+) = (\.|\d+) if (.*)', l)
        if m:
            d.loc[stata_cond(d, m[3]), m[1]] = np.nan if m[2] == '.' else float(m[2]); continue
        m = re.fullmatch(r'gen byte (\w+) = (\w+) != 0', l)
        if m: d[m[1]] = (d[m[2]] != 0).astype(float); continue
        m = re.fullmatch(r'drop (.*)', l)
        if m: d = d.drop(columns=m[1].split()); continue
        raise ValueError(l)
    return d

def run(do_path, raw_path, outdir):
    src = open(do_path, encoding='latin1').read().replace('\r', '')
    inf = re.search(r'infix(.*?)using', src, re.S).group(1).replace('///', ' ')
    spec = re.findall(r'([A-Za-z0-9]+)\s+(\d+)(?:-(\d+))?', inf)
    lines = [l for l in open(raw_path, 'rb').read().decode('latin1').replace('\r', '').split('\n') if l.strip()]
    cols = {}
    for name, a, b in spec:
        a = int(a); b = int(b) if b else a
        cols[name.lower()] = [float(s) if s.isdigit() else np.nan for s in (l[a-1:b].strip() for l in lines)]
    m = pd.DataFrame(cols)
    m.insert(0, 'id', np.arange(1, len(m)+1))
    m = m.rename(columns={'p30': 'cov_sex', 'p31': 'cov_age'})
    m.loc[m.cov_age == 99, 'cov_age'] = np.nan
    covs = ['cov_sex', 'cov_age']
    body = src.split('Process the data', 1)[1]
    out = {}
    for blk in re.split(r'\n\*\*# Bookmark', body)[1:]:
        exp = re.search(r'export delimited using "(.*?)"', blk)
        if not exp: continue
        bl = blk.split('\n')
        k = next(j for j, l in enumerate(bl) if l.startswith('keep id cov_*'))
        q = next(j for j, l in enumerate(bl) if l.startswith('local question_cols'))
        keep = bl[k].split()[3:]
        qcols = bl[q].split()[2:]
        d = execute(m[['id'] + covs + keep].copy(), bl[k+1:q])
        long = d.melt(id_vars=['id'] + covs, value_vars=qcols, var_name='item', value_name='resp')
        long = long[['id', 'item', 'resp'] + covs].sort_values(['id', 'item']).reset_index(drop=True)
        os.makedirs(outdir, exist_ok=True)
        long.to_csv(os.path.join(outdir, exp[1]), index=False, float_format='%.0f')
        out[exp[1]] = long
    return out

if __name__ == '__main__':
    for k, v in run(*sys.argv[1:4]).items(): print(k, len(v))
