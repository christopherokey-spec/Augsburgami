#!/usr/bin/env python3
"""Generate static Augsburgami HTML from games.csv and the supplied visual template.
Requires: pip install beautifulsoup4
Run: python build_augsburgami.py
"""
import csv, re
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / 'augsburgami_template.html'
DATA = ROOT / 'games.csv'
OUTPUT = ROOT / 'index.html'

def key(a,b): return (max(a,b),min(a,b))
def score_id(k): return f'{k[0]}-{k[1]}'
def date_key(g):
    m,d,y = map(int,g['date'].split('/'))
    return y,m,d

def build():
    games=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')))
    if not games: raise ValueError('No games in games.csv')
    groups=defaultdict(list)
    for line,g in enumerate(games,2):
        try:
            a,b=int(g['augsburg_score']),int(g['opponent_score'])
            if a<0 or b<0: raise ValueError('negative score')
            date_key(g)
            if not g['matchup'].strip(): raise ValueError('missing matchup')
        except Exception as e: raise ValueError(f'CSV line {line}: {e}') from e
        groups[key(a,b)].append(g)
    soup=BeautifulSoup(TEMPLATE.read_text(encoding='utf-8'),'html.parser')
    main=soup.select_one('main')
    grid=soup.select_one('#gridView')
    matrix=soup.select_one('table.matrix')
    if not (main and grid and matrix): raise ValueError('Template is missing Augsburgami matrix')
    # Remove old score controls and results; keep grid control, styling and all site chrome.
    for el in main.select('input[id^="score-radio-"], section.detail'): el.decompose()
    # Rebuild only the clickable cells; leave row/column headers and other classes intact.
    col_headers=[int(th.get_text(strip=True)) for th in matrix.select('thead th.colnum')]
    rows=matrix.select('tbody tr')
    if not rows: raise ValueError('Matrix rows missing')
    supported={(max(row, col),min(row,col)) for row in range(len(rows)) for col in col_headers if col>=row}
    missing=set(groups)-supported
    if missing: raise ValueError(f'Scores outside matrix bounds: {sorted(missing)}; expand template matrix first')
    for tr in rows:
        row=int(tr.select_one('th.rownum').get_text(strip=True))
        cells=tr.find_all('td',recursive=False)
        if len(cells)!=len(col_headers): raise ValueError('Matrix column count mismatch')
        for col,cell in zip(col_headers,cells):
            if col<row: continue  # existing lower triangle remains intentionally blank
            k=key(row,col)
            cell.clear()
            if k in groups:
                cell['class']=['hit']
                lab=soup.new_tag('label',attrs={'for':'score-radio-'+score_id(k),'aria-label':'Augsburgami '+score_id(k)})
                cell.append(lab)
            else: cell['class']=['empty']
    # Put the controls before the grid, and the panels after it, exactly as in the original.
    for k in sorted(groups):
        control=soup.new_tag('input',attrs={'class':'view-radio','id':'score-radio-'+score_id(k),'name':'view','type':'radio'})
        grid.insert_before(control)
    last=grid
    for k in sorted(groups):
        sid=score_id(k)
        panel=soup.new_tag('section',attrs={'class':'detail','id':'panel-'+sid})
        h=soup.new_tag('h2');h.string=f'{k[0]}–{k[1]}';panel.append(h)
        for a in ([k[0],k[1]] if k[0]!=k[1] else [k[0]]):
            items=sorted((g for g in groups[k] if int(g['augsburg_score'])==a),key=date_key)
            if not items:continue
            o=soup.new_tag('div',attrs={'class':'orientation'});o.string=f'Augsburg {a}–{k[1] if a==k[0] else k[0]}';panel.append(o)
            for g in items:
                div=soup.new_tag('div',attrs={'class':'game'});div.string=f"{g['date']} {g['matchup']}";panel.append(div)
        back=soup.new_tag('label',attrs={'class':'back','for':'view-grid'});back.string='Back to Augsburgami';panel.append(back)
        last.insert_after(panel);last=panel
    # Only replace generated score-radio CSS rules, retaining all visual CSS verbatim.
    css=soup.style.string or soup.style.get_text()
    css=re.sub(r'(?m)^#score-radio-\d+-\d+:checked ~ #(gridView|panel-\d+-\d+)\s*\{[^}]*\}\s*','',css)
    css+='\n/* GENERATED SCORE NAVIGATION — do not edit manually */\n'
    for k in sorted(groups):
        sid=score_id(k)
        css+=f'#score-radio-{sid}:checked ~ #gridView{{display:none}}\n'
        css+=f'#score-radio-{sid}:checked ~ #panel-{sid}{{display:block}}\n'
    soup.style.string=css
    # Update a pre-existing game count only when the original has an explicit count.
    for node in soup.find_all(string=re.compile(r'\b822\b')):
        if node.parent.name not in ('style','script'):
            node.replace_with(re.sub(r'\b822\b',str(len(games)),str(node)))
    OUTPUT.write_text(str(soup),encoding='utf-8')
    check=BeautifulSoup(OUTPUT.read_text(encoding='utf-8'),'html.parser')
    assert len(check.select('section.detail'))==len(groups)
    assert len(check.select('section.detail .game'))==len(games)
    assert len(check.select('td.hit'))==len(groups)
    assert len(check.select('input[id^="score-radio-"]'))==len(groups)
    print(f'Built {OUTPUT.name}: {len(games)} games, {len(groups)} unique score squares')

if __name__=='__main__':build()
