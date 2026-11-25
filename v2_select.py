"""Benchmark v2 selection filter (PLAN_V2.md tests 2, 3 and 4), run 2026-10-28.

Reads the hashed CANDIDATES_V2.md and applies the exposure checks to every row. Writes nothing the
plan depends on: no input is built, no decoy panel is constructed, no prediction is run. Every raw
API response is cached under v2_selection_raw/ so the filter is reproducible without re-querying.

  test 2  no co-structure: RCSB search, sequence of the human enzyme at identity_cutoff 0.95 AND any
          PDB chemical component of the metabolite present as a non-polymer entity. Hits > 0 = FAIL.
  test 3  no deposited affinity: ChEMBL activities for (target of this UniProt accession, molecule of
          this metabolite) and BindingDB ligands for this UniProt matched on InChIKey skeleton.
          Hits > 0 in either = FAIL.
  test 4  human enzyme: gene symbol resolves to a reviewed human UniProt entry.

Chemical identity is resolved by PubChem name lookup (InChIKey) then UniChem connectivity search,
which gives the PDB component ids and ChEMBL ids sharing that skeleton. Skeleton matching (InChIKey
block 1) is deliberate: it ignores protonation and stereochemistry, so AMP(3-) and AMP are one
compound. Multi-gene rows resolve to the human isoform with the most PDB entries, per CANDIDATES_V2.md.

usage: python v2_select.py [stage]   stage in {chem, gene, test2, test3, table}; default runs all.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{HERE}/v2_selection_raw"; os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "boltzbench-v2-selection/1.0 (research; contact via repo)"}

# Metabolite as written in CANDIDATES_V2.md -> the PDB chemical component(s) that are that compound.
# Anchoring on the component dictionary rather than on a name lookup is deliberate: PubChem's record for
# "fructose 1,6-bisphosphate" (CID 445555) is the 2,5-anhydro analogue, which silently resolved to AHG/AHM
# and would have missed every FBP co-structure. Each id below is printed with the component dictionary's own
# name and formula by `v2_select.py chem` so the mapping can be audited. UniChem then expands each anchor to
# the other components and the ChEMBL molecules sharing its connectivity (anomers, stereoisomers, salts).
CCD_ANCHOR = {
    "ATP": ["ATP"], "ADP": ["ADP"], "AMP": ["AMP"], "GTP": ["GTP"], "GDP": ["GDP"], "GMP": ["5GP"],
    "UTP": ["UTP"], "CTP": ["CTP"], "dATP": ["DTP"], "dGTP": ["DGT"], "dTTP": ["TTP"], "dCTP": ["DCP"],
    "citrate": ["CIT"], "fructose-2,6-bisphosphate": ["FDP"], "fructose-1,6-bisphosphate": ["FBP"],
    "fructose-6-phosphate": ["F6P", "F6R"], "glucose-6-phosphate": ["G6P", "BG6", "A6P"],
    "phosphoenolpyruvate": ["PEP"], "palmitoyl-CoA": ["PKZ"], "acetyl-CoA": ["ACO"],
    "succinyl-CoA": ["SCA"], "malonyl-CoA": ["MLC"], "NADH": ["NAI"], "NADPH": ["NDP"], "NADP+": ["NAP"],
    "PRPP": ["PRP"], "phosphate": ["PO4"], "S-adenosylmethionine": ["SAM"], "N-acetylglutamate": ["NLG"],
    "oxaloacetate": ["OAA"], "sterol / lanosterol": ["LAN"], "SAICAR": ["SSS", "OK8"],
    "serine": ["SER"], "alanine": ["ALA"], "phenylalanine": ["PHE"], "leucine": ["LEU"],
    "arginine": ["ARG"], "glutamate": ["GLU"], "aspartate": ["ASP"],
}

# Literature synonyms for the PubMed screen only; they play no part in the exposure tests.
MET_SYNONYM = {
    "NADP+": ["NADP"], "NADPH": ["NADPH"], "NADH": ["NADH"],
    "fructose-2,6-bisphosphate": ["fructose 2,6-bisphosphate", "fructose-2,6-P2", "F26BP"],
    "fructose-1,6-bisphosphate": ["fructose 1,6-bisphosphate", "FBP"],
    "fructose-6-phosphate": ["fructose 6-phosphate"], "glucose-6-phosphate": ["glucose 6-phosphate"],
    "palmitoyl-CoA": ["palmitoyl-CoA", "palmitoyl coenzyme A", "long-chain acyl-CoA"],
    "acetyl-CoA": ["acetyl-CoA", "acetyl coenzyme A"], "succinyl-CoA": ["succinyl-CoA"],
    "malonyl-CoA": ["malonyl-CoA"], "S-adenosylmethionine": ["S-adenosylmethionine", "SAM", "AdoMet"],
    "N-acetylglutamate": ["N-acetylglutamate", "NAG"], "PRPP": ["phosphoribosyl pyrophosphate", "PRPP"],
    "SAICAR": ["SAICAR", "succinylaminoimidazolecarboxamide ribose-5'-phosphate"],
    "sterol / lanosterol": ["lanosterol", "sterol"], "phosphate": ["phosphate", "Pi"],
    "serine": ["serine", "L-serine"], "alanine": ["alanine", "L-alanine"],
    "leucine": ["leucine", "L-leucine"], "arginine": ["arginine", "L-arginine"],
    "glutamate": ["glutamate"], "aspartate": ["aspartate"], "phenylalanine": ["phenylalanine"],
    "citrate": ["citrate"], "oxaloacetate": ["oxaloacetate"], "phosphoenolpyruvate": ["phosphoenolpyruvate", "PEP"],
}

# Retained only to record what a name lookup would have given; not used for the filter.
CHEM_QUERY = {
    "ATP": "ATP", "ADP": "ADP", "AMP": "AMP", "GTP": "GTP", "GDP": "GDP", "GMP": "GMP",
    "UTP": "UTP", "CTP": "CTP", "dATP": "dATP", "dGTP": "dGTP", "dTTP": "dTTP", "dCTP": "dCTP",
    "citrate": "citrate", "fructose-2,6-bisphosphate": "fructose 2,6-bisphosphate",
    "fructose-1,6-bisphosphate": "fructose 1,6-bisphosphate",
    "glucose-6-phosphate": "glucose 6-phosphate", "fructose-6-phosphate": "fructose 6-phosphate",
    "phosphoenolpyruvate": "phosphoenolpyruvate", "palmitoyl-CoA": "palmitoyl-CoA",
    "serine": "L-serine", "alanine": "L-alanine", "phenylalanine": "L-phenylalanine",
    "leucine": "L-leucine", "arginine": "L-arginine", "glutamate": "L-glutamic acid",
    "aspartate": "L-aspartic acid", "SAICAR": "SAICAR", "acetyl-CoA": "acetyl-CoA",
    "succinyl-CoA": "succinyl-CoA", "malonyl-CoA": "malonyl-CoA", "NADH": "NADH",
    "NADPH": "NADPH", "NADP+": "NADP", "PRPP": "phosphoribosyl pyrophosphate",
    "phosphate": "phosphate", "S-adenosylmethionine": "S-adenosyl-L-methionine",
    "N-acetylglutamate": "N-acetyl-L-glutamic acid", "oxaloacetate": "oxaloacetic acid",
    "sterol / lanosterol": "lanosterol",
}


def get(url, cache, parse=json.loads, tries=3, pause=0.34, post=None):
    """Fetch url once and cache the raw body under v2_selection_raw/.

    RCSB answers a query with no hits with 204 and an empty body, which is a real zero, not a failure;
    it is cached as such and parsed to {} so callers read total_count 0.
    """
    def decode(s):
        return ({} if not s.strip() else parse(s)) if parse else s
    p = f"{RAW}/{cache}"
    if os.path.exists(p):
        return decode(open(p).read())
    hdr = dict(UA, **({"Content-Type": "application/json"} if post else {}))
    data = json.dumps(post).encode() if post else None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdr), timeout=120) as r:
                body = r.read().decode("utf-8", "replace")
            break
        except Exception as e:
            if i == tries - 1:
                body = json.dumps({"_error": f"{type(e).__name__}: {e}", "_url": url})
            time.sleep(2 * (i + 1))
    open(p, "w").write(body); time.sleep(pause)
    return decode(body)


def rcsb(query, cache):
    return get("https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(query)), cache)


def candidates():
    """The 73 rows of the hashed CANDIDATES_V2.md, in file order."""
    rows, seen = [], set()
    for line in open(f"{HERE}/CANDIDATES_V2.md"):
        m = re.match(r"^\|\s*([A-Z0-9/ ]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line)
        if not m or m.group(1).strip() in ("enzyme (gene)",) or set(m.group(1)) <= set("- "):
            continue
        genes = [g.strip() for g in m.group(1).split("/")]
        key = (m.group(1), m.group(2))
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(n=len(rows) + 1, gene_field=m.group(1).strip(), genes=genes,
                         regulator=m.group(2).strip(), direction=m.group(3).strip(), pathway=m.group(4).strip()))
    return rows


def stage_chem(rows):
    """metabolite -> verified PDB components, their skeletons, and the ChEMBL molecules sharing them."""
    out = {}
    for name in sorted({r["regulator"] for r in rows}):
        rec = dict(name=name, anchors=[], pdb_ids=[], chembl_ids=[], skeletons=[])
        for ccd in CCD_ANCHOR[name]:
            d = get(f"https://data.rcsb.org/rest/v1/core/chemcomp/{ccd}", f"ccd_{ccd}.json")
            c = d.get("chem_comp", {})
            key = (d.get("rcsb_chem_comp_descriptor") or {}).get("InChIKey", "")
            rec["anchors"].append(dict(ccd=ccd, ccd_name=c.get("name", ""), formula=c.get("formula", ""),
                                       type=c.get("type", ""), inchikey=key))
            if not key:
                continue
            rec["pdb_ids"].append(ccd); rec["skeletons"].append(key.split("-")[0])
            u = get("https://www.ebi.ac.uk/unichem/api/v1/connectivity", f"unichem_{key.split('-')[0]}.json",
                    post=dict(compound=key, type="inchikey", searchComponents=False))
            for s in (u.get("sources") or []):
                sid, cid, cmp = s.get("id"), str(s.get("compoundId", "")), s.get("comparison", {})
                if not cmp.get("connectivity", False):          # same skeleton only; H count and stereo may differ
                    continue
                if sid in (3, 5) and re.fullmatch(r"[A-Z0-9]{1,5}", cid):
                    rec["pdb_ids"].append(cid)
                elif sid == 1:
                    rec["chembl_ids"].append(cid)
        for k in ("pdb_ids", "chembl_ids", "skeletons"):
            rec[k] = sorted(set(rec[k]))
        out[name] = rec
    json.dump(out, open(f"{HERE}/v2_chem.json", "w"), indent=1)
    return out


def stage_gene(rows):
    """gene symbol -> reviewed human UniProt accession, sequence, PDB entry count."""
    out = {}
    for g in sorted({g for r in rows for g in r["genes"]}):
        d = get("https://rest.uniprot.org/uniprotkb/search?" + urllib.parse.urlencode(
            dict(query=f"gene_exact:{g} AND organism_id:9606 AND reviewed:true",
                 fields="accession,id,gene_primary,protein_name,sequence", format="json", size=5)),
            f"uniprot_{g}.json")
        res = d.get("results", [])
        # gene_exact also matches gene synonyms: "GCK" returns MAP4K2 (germinal centre kinase) as well as
        # glucokinase, so require the entry's own primary gene name to be the symbol asked for.
        exact = [e for e in res if any(n.get("geneName", {}).get("value", "").upper() == g.upper()
                                       for n in e.get("genes", []))]
        res = exact or res
        if not res:
            out[g] = dict(gene=g, accession=None, human=False); continue
        e = res[0]; acc = e["primaryAccession"]; seq = e["sequence"]["value"]
        n = rcsb({"query": {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": acc}}, "return_type": "entry",
            "request_options": {"return_counts": True}}, f"rcsb_count_{acc}.json").get("total_count", 0)
        pd_ = e.get("proteinDescription", {})
        syn = [pd_.get("recommendedName", {}).get("fullName", {}).get("value", "")]
        syn += [a.get("fullName", {}).get("value", "") for a in pd_.get("alternativeNames", [])]
        syn += [x.get("value", "") for n2 in e.get("genes", []) for x in n2.get("synonyms", [])]
        out[g] = dict(gene=g, accession=acc, uniprot_id=e.get("uniProtkbId"), human=True,
                      name=syn[0], synonyms=[s for s in dict.fromkeys(syn) if s],
                      length=len(seq), sequence=seq, pdb_entries=n)
    json.dump({k: {x: y for x, y in v.items() if x != "sequence"} for k, v in out.items()},
              open(f"{HERE}/v2_genes.json", "w"), indent=1)
    return out


def pick_gene(row, genes):
    """CANDIDATES_V2.md: multi-gene rows resolve to the human isoform with the most PDB entries."""
    cand = [genes[g] for g in row["genes"] if genes.get(g, {}).get("accession")]
    return max(cand, key=lambda g: g["pdb_entries"]) if cand else None


def stage_test2(rows, genes, chem):
    """RCSB: this enzyme (sequence identity >= 0.95) co-crystallised with this metabolite."""
    out = {}
    for r in rows:
        g = pick_gene(r, genes); c = chem[r["regulator"]]
        k = f"{r['n']:02d}"
        if not g or not c["pdb_ids"]:
            out[k] = dict(hits=None, note="no accession" if not g else "no PDB chemical component for this metabolite")
            continue
        # one query per component, so a FAIL names the component that caused it and can be audited
        per = {}
        for comp in c["pdb_ids"]:
            q = {"query": {"type": "group", "logical_operator": "and", "nodes": [
                {"type": "terminal", "service": "sequence", "parameters": {
                    "evalue_cutoff": 1, "identity_cutoff": 0.95, "sequence_type": "protein", "value": g["sequence"]}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id",
                    "operator": "exact_match", "value": comp}}]},
                "return_type": "entry", "request_options": {"return_counts": True}}
            d = rcsb(q, f"rcsb_t2_{g['accession']}_{comp}.json")
            per[comp] = d.get("total_count", 0)
        out[k] = dict(hits=sum(per.values()), per_component={x: y for x, y in per.items() if y},
                      accession=g["accession"], gene=g["gene"], comps=c["pdb_ids"])
    json.dump(out, open(f"{HERE}/v2_test2.json", "w"), indent=1)
    return out


def stage_test3(rows, genes, chem):
    """ChEMBL activities for the pair, and BindingDB ligands for the enzyme matched on skeleton."""
    from rdkit import Chem, RDLogger
    from rdkit.Chem.inchi import MolToInchiKey
    RDLogger.DisableLog("rdApp.*")
    C = "https://www.ebi.ac.uk/chembl/api/data"
    targets, bdb = {}, {}
    out = {}
    for r in rows:
        g = pick_gene(r, genes); c = chem[r["regulator"]]; k = f"{r['n']:02d}"
        if not g:
            out[k] = dict(note="no accession"); continue
        acc = g["accession"]
        if acc not in targets:
            d = get(f"{C}/target.json?target_components__accession={acc}&limit=50", f"chembl_target_{acc}.json")
            targets[acc] = [t["target_chembl_id"] for t in d.get("targets", [])]
        if acc not in bdb:
            raw = get(f"https://bindingdb.org/rest/getLigandsByUniprot?uniprot={acc}&cutoff=100000000"
                      f"&response=application/json", f"bindingdb_{acc}.json")
            hits = []
            resp = raw.get("getLindsByUniprotResponse", raw) if isinstance(raw, dict) else {}
            for a in (resp.get("bdb.affinities") or []):
                s = (a.get("bdb.smile") or "").strip()
                m = Chem.MolFromSmiles(s) if s else None
                if m:
                    try: hits.append((MolToInchiKey(m).split("-")[0], a.get("bdb.affinity_type"), a.get("bdb.affinity")))
                    except Exception: pass
            bdb[acc] = dict(n_records=len(resp.get("bdb.affinities") or []), parsed=hits)
        n_chembl, types, examples = 0, set(), []
        if targets[acc] and c["chembl_ids"]:
            d = get(f"{C}/activity.json?target_chembl_id__in={','.join(targets[acc])}"
                    f"&molecule_chembl_id__in={','.join(c['chembl_ids'])}&limit=20",
                    f"chembl_act_{acc}_{c['skeletons'][0] if c['skeletons'] else 'na'}.json")
            n_chembl = d.get("page_meta", {}).get("total_count", 0)
            for a in d.get("activities", [])[:20]:
                types.add(a.get("standard_type"))
                if len(examples) < 3:
                    examples.append(f"{a.get('molecule_chembl_id')} {a.get('standard_type')}="
                                    f"{a.get('standard_value')}{a.get('standard_units') or ''}")
        bm = [(t, v) for sk, t, v in bdb[acc]["parsed"] if sk in set(c["skeletons"])]
        out[k] = dict(chembl_targets=targets[acc], chembl_molecules=c["chembl_ids"], chembl_hits=n_chembl,
                      chembl_types=sorted(x for x in types if x), chembl_examples=examples,
                      bindingdb_records=bdb[acc]["n_records"], bindingdb_hits=len(bm),
                      bindingdb_matched=bm[:5], accession=acc)
    json.dump(out, open(f"{HERE}/v2_test3.json", "w"), indent=1)
    return out


def stage_test1(rows, genes):
    """PubMed screen for test 1. A screen, not the test: a hit shows a primary literature exists to read,
    and a zero marks the row for reading by hand before it is called folklore."""
    E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    out = {}
    for r in rows:
        g = pick_gene(r, genes); k = f"{r['n']:02d}"
        # The gene symbol alone is far too narrow: "PKM"[tiab] misses Keller 2012 on SAICAR, whose title says
        # "pyruvate kinase isoform M2". Search UniProt's alternative protein names and metabolite synonyms too.
        prot = [g["gene"] if g else r["genes"][0]] + (g.get("synonyms") or [] if g else [])
        met = {r["regulator"], CHEM_QUERY.get(r["regulator"], r["regulator"])} | set(MET_SYNONYM.get(r["regulator"], []))
        term = ("(" + " OR ".join(f'"{p}"[tiab]' for p in dict.fromkeys(prot)) + ") AND ("
                + " OR ".join(f'"{m}"[tiab]' for m in sorted(met)) + ") AND "
                "(allosteric[tiab] OR inhibit*[tiab] OR activat*[tiab] OR kinetic*[tiab] OR regulat*[tiab])")
        d = get(f"{E}/esearch.fcgi?db=pubmed&retmode=json&retmax=3&term={urllib.parse.quote(term)}",
                f"pubmed2_{k}.json", pause=0.4)
        ids = d.get("esearchresult", {}).get("idlist", [])
        n = int(d.get("esearchresult", {}).get("count", 0))
        titles = []
        if ids:
            s = get(f"{E}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}", f"pubmed2_sum_{k}.json", pause=0.4)
            for i in ids:
                rec = s.get("result", {}).get(i, {})
                titles.append(f"PMID {i} ({rec.get('pubdate', '')[:4]}) {rec.get('title', '')[:95]}")
        out[k] = dict(term=term, count=n, pmids=ids, titles=titles)
    json.dump(out, open(f"{HERE}/v2_test1.json", "w"), indent=1)
    return out


def stage_table(rows, genes, chem):
    """All 73 rows with the four test results, then the surviving panel."""
    t1 = json.load(open(f"{HERE}/v2_test1.json")); t2 = json.load(open(f"{HERE}/v2_test2.json"))
    t3 = json.load(open(f"{HERE}/v2_test3.json"))
    L = ["| # | enzyme (gene field) | resolved | regulator | T1 lit (PubMed n) | T2 co-structure | T3 affinity | T4 human | verdict |",
         "|---|---|---|---|---|---|---|---|---|"]
    panel = []
    for r in rows:
        k = f"{r['n']:02d}"; g = pick_gene(r, genes); a, b, c = t2[k], t3[k], t1[k]
        comp = ", ".join(f"{x}:{y}" for x, y in (a.get("per_component") or {}).items())
        p2 = a.get("hits") == 0
        p3 = not b.get("chembl_hits") and not b.get("bindingdb_hits")
        p4 = bool(g and g.get("human"))
        ok = p2 and p3 and p4
        if ok:
            panel.append((r, g))
        col1 = ("PASS" if c["count"] else "screen 0") + f" ({c['count']})"
        col2 = "PASS (0)" if p2 else f"FAIL ({a.get('hits')}: {comp})"
        col3 = "PASS" if p3 else f"FAIL (ChEMBL {b.get('chembl_hits')}, BindingDB {b.get('bindingdb_hits')})"
        who = f"{g['gene']} ({g['accession']})" if g else "-"
        L.append(f"| {r['n']} | {r['gene_field']} | {who} | {r['regulator']} | {col1} | {col2} | {col3} | "
                 f"{'PASS' if p4 else 'FAIL'} | {'**IN PANEL**' if ok else 'excluded'} |")
    return L, panel


def main():
    rows = candidates()
    print(f"{len(rows)} candidate rows parsed from CANDIDATES_V2.md")
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    chem = stage_chem(rows) if stage in ("all", "chem") else json.load(open(f"{HERE}/v2_chem.json"))
    if stage == "chem":
        for k, v in chem.items():
            a = "; ".join(f"{x['ccd']}={x['ccd_name'][:38]} [{x['formula']}]" for x in v["anchors"])
            print(f"{k:26s} {a}\n{'':26s} PDB={','.join(v['pdb_ids'])}\n{'':26s} ChEMBL={','.join(v['chembl_ids']) or '-'}")
        return
    genes = stage_gene(rows)
    if stage == "gene":
        for k, v in sorted(genes.items()):
            print(f"{k:10s} {v.get('accession') or 'NONE':10s} pdb_entries={v.get('pdb_entries')}")
        return
    if stage in ("all", "test1"):
        t1 = stage_test1(rows, genes)
        print(f"test 1 screen done: {sum(1 for v in t1.values() if v['count'] == 0)} rows with no PubMed hit")
    if stage in ("all", "test2"):
        t2 = stage_test2(rows, genes, chem)
        print(f"test 2 done: {sum(1 for v in t2.values() if v.get('hits') == 0)} rows with no co-structure")
    if stage in ("all", "test3"):
        t3 = stage_test3(rows, genes, chem)
        print(f"test 3 done: {sum(1 for v in t3.values() if not v.get('chembl_hits') and not v.get('bindingdb_hits'))} rows with no deposited affinity")


if __name__ == "__main__":
    main()
