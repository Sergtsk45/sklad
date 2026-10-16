"""Baseline-бенчмарк поиска товаров (план 2026-10-17-product-search-v2.md).

Данные prod в репозиторий не кладутся. Выгрузка (read-only psql на prod):

  catalog.csv:
  \copy (select p.id pid, t.id tid, t.active,
         coalesce(t.name->>'ru_RU', t.name->>'en_US') name, t.default_code,
         t.x_search_name tx from product_product p
         join product_template t on t.id=p.product_tmpl_id
         where t.active and p.active) to stdout with csv header
  pairs.csv:
  \copy (select l.id, l.name_raw, l.product_id, r.create_date::date d
         from object_request_line l join object_request r on r.id=l.request_id
         where l.product_id is not null and coalesce(l.name_raw,'')<>'')
         to stdout with csv header

Запуск:
  python3 docs/plans/2026-10-17-product-search-v2-bench.py <dir с csv> \
      custom_addons/custom_product_search/models/product_search_utils.py

Режимы: A — список товаров (ilike), B — автокомплит как на prod,
C — B с пересчитанным индексом, D — прототип (токены + префикс + fuzzy).
"""
import csv, re, sys, importlib.util, difflib
B = sys.argv[1]
spec = importlib.util.spec_from_file_location("u", sys.argv[2]); u = importlib.util.module_from_spec(spec); spec.loader.exec_module(u)
norm = u.normalize_product_search_text
cat = list(csv.DictReader(open(B + "/catalog.csv")))
pairs = [p for p in csv.DictReader(open(B + "/pairs.csv"))]
pid_ok = {c["pid"] for c in cat}
pairs = [p for p in pairs if p["product_id"] in pid_ok]
for c in cat:
    c["fresh"] = norm(c["name"]); c["low"] = c["name"].lower(); c["tx"] = c["tx"] or ""
cat.sort(key=lambda c: (c["default_code"] or "", c["low"], int(c["pid"])))
LIMIT = 8

def list_view(q):
    ql = q.lower()
    return [c["pid"] for c in cat if ql in c["low"] or (c["default_code"] and ql in c["default_code"].lower())]

def name_search(q, field):
    std = list_view(q)[:LIMIT]
    if len(std) >= LIMIT: return std
    n = norm(q); toks = n.split()
    res = list(std)
    for c in cat:
        if c["pid"] in res: continue
        s = c[field]
        if n in s or (len(toks) > 1 and all(t in s for t in toks)):
            res.append(c["pid"])
            if len(res) >= LIMIT: break
    return res

# Прототип: токены буквы/цифры, префикс-совпадение, ранжирование по доле совпавших токенов
SPLIT = re.compile(r"[a-zа-я]+|\d+(?:\.\d+)?")
def toks(s): return SPLIT.findall(norm(s))
def stem(t): return t[:5] if len(t) > 5 and not t[0].isdigit() else t
for c in cat: c["pt"] = [stem(t) for t in toks(c["name"])]
def proto(q):
    qt = [stem(t) for t in toks(q)]
    if not qt: return []
    scored = []
    for c in cat:
        hit = sum(1 for t in qt if any(nt.startswith(t) or (len(t) >= 4 and difflib.SequenceMatcher(None, t, nt).ratio() >= 0.8) for nt in c["pt"]))
        if hit: scored.append((-(hit / len(qt)), -hit / max(len(c["pt"]), 1), c["pid"]))
    scored.sort()
    return [s[2] for s in scored[:LIMIT]]

modes = {"A список товаров": list_view, "B выпадающий (как на prod)": lambda q: name_search(q, "tx"),
         "C выпадающий, индекс пересчитан": lambda q: name_search(q, "fresh"), "D прототип": proto}
rows = []
for name, fn in modes.items():
    found = top1 = 0; miss = []
    for p in pairs:
        r = fn(p["name_raw"])[:LIMIT]
        if p["product_id"] in r:
            found += 1; top1 += r[0] == p["product_id"]
        else: miss.append(p["name_raw"])
    rows.append((name, found, top1))
    print("%-34s found@8 %3d/%d (%.0f%%)  top1 %3d (%.0f%%)" % (name, found, len(pairs), 100*found/len(pairs), top1, 100*top1/len(pairs)))
    if name.startswith("C"): print("   misses C e.g.:", miss[:12])
# Короткие запросы как в списке: первые 2 слова
print("-- short queries (first 2 words)")
for name, fn in modes.items():
    f = sum(1 for p in pairs if p["product_id"] in fn(" ".join(p["name_raw"].split()[:2]))[:LIMIT])
    print("%-34s found@8 %3d/%d (%.0f%%)" % (name, f, len(pairs), 100*f/len(pairs)))
for q in ["болт 16", "болт 16х70", "болт м16х70 оцинк", "гайка м16", "кран шаровый ду 50", "отвод 57х3,5", "болд м16"]:
    print("Q", q, {k[0]: len(fn(q)) for k, fn in modes.items()})
