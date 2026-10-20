#!/usr/bin/env python3
# Camada adicional de detalhe (fabricante+segmento+cliente) por cidade, pro clique no mapa.
# Fonte: ../emplacamentos_detalhe_2026.csv (export Kayque, snapshot 30/09/2026).
# Mesmas exclusoes do cenario oficial do mapa (Bachiega, Bendo Alimentos, Canavieiro, Usina Acucareira)
# e mesmo universo de fabricante/segmento/cidade do emplac.json — mas os totais aqui NAO sao
# garantidos bater 1:1 com emplac.json (snapshots de datas diferentes). Usar so como detalhe complementar.
import csv, json, unicodedata, re
from collections import defaultdict

def norm(s):
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.upper().replace('.', ' ')
    return re.sub(r'\s+', ' ', s).strip()

def excluido(cliente, segmento):
    c = cliente.upper()
    if 'BACHIEGA' in c: return True
    if 'BENDO ALIMENTOS' in c: return True
    if segmento.strip().upper() == 'CANAVIEIRO': return True
    if 'USINA ACUCAREIRA' in c or 'USINA AÇUCAREIRA' in c: return True
    return False

emplac = json.load(open('emplac.json'))
fabs, fams = emplac['fabs'], emplac['fams']
fab_idx = {norm(f): i for i, f in enumerate(fabs)}
fam_idx = {norm(f): i for i, f in enumerate(fams)}
reg = json.load(open('data.json'))
reg_keys = set(reg.keys())

agg = defaultdict(int)  # (cityKey, fabIdx, famIdx, cliente) -> qtd
with open('../emplacamentos_detalhe_2026.csv', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f, delimiter=';'):
        cli = row['Cliente'].strip()
        seg = row['Familia_Produto'].strip()
        fab = row['Fabricante'].strip()
        cidade = row['Municipio'].strip()
        qtd = int(row['Emplacamentos'])
        if excluido(cli, seg):
            continue
        fi = fab_idx.get(norm(fab))
        mi = fam_idx.get(norm(seg))
        ck = norm(cidade)
        if fi is None or mi is None or ck not in reg_keys:
            continue
        agg[(ck, fi, mi, cli)] += qtd

out = defaultdict(list)
for (ck, fi, mi, cli), qtd in agg.items():
    marca = 0 if fabs[fi] == 'GUERRA' else 1
    out[ck].append([fi, mi, marca, cli, qtd])
for ck in out:
    out[ck].sort(key=lambda x: -x[4])

meta = {
    'fonte': 'emplacamentos_detalhe_2026.csv (export Kayque)',
    'snapshot': '2026-09-30',
    'aviso': 'Detalhe complementar (fabricante/segmento/cliente) por cidade. Pode nao bater 1:1 com o total oficial do mapa (snapshots de datas diferentes).'
}
json.dump({'meta': meta, 'cidades': out}, open('cliente_detalhe.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('cidades com detalhe:', len(out), '| total linhas:', sum(len(v) for v in out.values()))
