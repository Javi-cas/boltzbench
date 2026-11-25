"""Benchmark v2 preparation: Tanimoto covariate, decoy panels, Boltz inputs, cost estimate.

Nothing here is launched. Reads the 32 surviving pairs from the selection step (v2_table.md,
v2_test2.json, v2_chem.json, v2_genes.json), all of which were produced before AMENDMENT_V2_01.md
was written, and the three hashed files are untouched.

  ligands   for each panel enzyme, the chemical components appearing in any co-structure of that
            enzyme or a homolog above 95% identity. Same RCSB sequence query as test 2
            (identity_cutoff 0.95, evalue_cutoff 1), return_type entry, then the data API GraphQL
            for each entry's non-polymer components and their SMILES.
  tanimoto  AMENDMENT_V2_01.md item 2: maximum ECFP4 (Morgan radius 2, 2048 bit) Tanimoto between
            the regulator and any such ligand. Subset for the pre-specified secondary is < 0.70.
  decoys    PLAN_V2.md's unchanged rule: two phosphorylated non-nucleotides, two neutral sugars,
            two small metabolites, skipping any that is a substrate, product or effector of that
            enzyme and substituting the next in the phosphorylated list.
  inputs    one yaml per complex in inputs_v2/, identical in form to v1's inputs/.
  cost      wall-clock estimate from runs/timing.tsv against sequence length.

usage: python v2_prepare.py [stage ...]   stage in {ligands, tanimoto, screen, decoys, inputs, cost}
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{HERE}/v2_prep_raw"; os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "boltzbench-v2-prepare/1.0 (research; contact via repo)"}


def get(url, cache, parse=json.loads, tries=3, pause=0.34, post=None):
    """Fetch url once and cache the raw body. An empty body is a real zero, not a failure."""
    def decode(s):
        return ({} if not s.strip() else parse(s)) if parse else s
    p = f"{RAW}/{cache}"
    if os.path.exists(p):
        return decode(open(p).read())
    hdr = dict(UA, **({"Content-Type": "application/json"} if post else {}))
    data = json.dumps(post).encode() if post else None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdr), timeout=180) as r:
                body = r.read().decode("utf-8", "replace")
            break
        except Exception as e:
            if i == tries - 1:
                body = json.dumps({"_error": f"{type(e).__name__}: {e}", "_url": url})
            time.sleep(2 * (i + 1))
    open(p, "w").write(body); time.sleep(pause)
    return decode(body)


def panel():
    """The 32 surviving pairs, read back from the selection step's own table."""
    rows = []
    for line in open(f"{HERE}/v2_table.md"):
        if "IN PANEL" not in line:
            continue
        f = [x.strip() for x in line.strip().strip("|").split("|")]
        n, resolved, regulator = f[0], f[2], f[3]
        m = re.match(r"^(\S+)\s+\(([A-Z0-9]+)\)$", resolved)
        rows.append(dict(n=int(n), key=f"{int(n):02d}", gene=m.group(1), accession=m.group(2),
                         regulator=regulator))
    return rows


def stage_ligands():
    """Every chemical component in a co-structure of each panel enzyme (or homolog >= 95% identity)."""
    genes = json.load(open(f"{HERE}/v2_genes.json"))
    seqs = {g["accession"]: g["sequence"] for g in
            json.load(open(f"{HERE}/v2_sequences.json")).values()}
    out = {}
    for acc in sorted({r["accession"] for r in panel()}):
        q = {"query": {"type": "terminal", "service": "sequence", "parameters": {
                "evalue_cutoff": 1, "identity_cutoff": 0.95, "sequence_type": "protein",
                "value": seqs[acc]}},
             "return_type": "entry", "request_options": {"paginate": {"start": 0, "rows": 2000}}}
        d = get("https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(q)),
                f"entries_{acc}.json")
        entries = [x["identifier"] for x in d.get("result_set", [])]
        comps = {}
        for i in range(0, len(entries), 100):
            chunk = entries[i:i + 100]
            gql = ("{entries(entry_ids:%s){rcsb_id nonpolymer_entities{nonpolymer_comp{chem_comp"
                   "{id name formula_weight}}}}}" % json.dumps(chunk))
            g = get("https://data.rcsb.org/graphql", f"ligands_{acc}_{i}.json",
                    post={"query": gql})
            for e in (g.get("data", {}).get("entries") or []):
                for ne in (e.get("nonpolymer_entities") or []):
                    c = ne["nonpolymer_comp"]["chem_comp"]
                    comps.setdefault(c["id"], c["name"])
        out[acc] = dict(entries=len(entries), ligands=comps)
        print(f"{acc:10s} entries={len(entries):4d} ligands={len(comps):3d} "
              f"{','.join(sorted(comps))[:90]}", flush=True)
    json.dump(out, open(f"{HERE}/v2_ligands.json", "w"), indent=1)
    return out


def smiles_for(comp_ids):
    """SMILES for PDB chemical components, from the data API, cached in blocks."""
    out, ids = {}, sorted(set(comp_ids))
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        gql = ("{chem_comps(comp_ids:%s){rcsb_id chem_comp{id name formula_weight}"
               "rcsb_chem_comp_descriptor{SMILES_stereo SMILES}}}" % json.dumps(chunk))
        g = get("https://data.rcsb.org/graphql", f"smiles_{chunk[0]}_{len(chunk)}_{i}.json",
                post={"query": gql})
        for c in (g.get("data", {}).get("chem_comps") or []):
            d = c.get("rcsb_chem_comp_descriptor") or {}
            s = d.get("SMILES_stereo") or d.get("SMILES")
            if s:
                out[c["rcsb_id"]] = dict(smiles=s, name=(c.get("chem_comp") or {}).get("name"),
                                         mw=(c.get("chem_comp") or {}).get("formula_weight"))
    return out


def stage_tanimoto():
    """AMENDMENT_V2_01.md item 2: max ECFP4 Tanimoto, regulator against every co-structure ligand."""
    from rdkit import Chem, RDLogger, DataStructs
    from rdkit.Chem import rdFingerprintGenerator
    RDLogger.DisableLog("rdApp.*")
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

    def fp(smi):
        m = Chem.MolFromSmiles(smi)
        return gen.GetFingerprint(m) if m else None

    lig = json.load(open(f"{HERE}/v2_ligands.json"))
    chem = json.load(open(f"{HERE}/v2_chem.json"))
    rows = panel()
    need = {c for v in lig.values() for c in v["ligands"]}
    need |= {a["ccd"] for r in rows for a in chem[r["regulator"]]["anchors"]}
    sm = smiles_for(need)
    unparsed = sorted(c for c in need if c not in sm)
    fps = {c: fp(v["smiles"]) for c, v in sm.items()}
    bad = sorted(c for c, f in fps.items() if f is None)
    print(f"{len(need)} components, {len(unparsed)} without SMILES {unparsed}, "
          f"{len(bad)} unparsable {bad}", flush=True)

    out = []
    for r in rows:
        anchors = [a["ccd"] for a in chem[r["regulator"]]["anchors"]]
        best, best_lig, pairs = 0.0, None, []
        for c in sorted(lig[r["accession"]]["ligands"]):
            if fps.get(c) is None:
                continue
            t = max((DataStructs.TanimotoSimilarity(fps[a], fps[c])
                     for a in anchors if fps.get(a) is not None), default=None)
            if t is None:
                continue
            pairs.append((c, round(t, 3)))
            if t > best:
                best, best_lig = t, c
        pairs.sort(key=lambda x: -x[1])
        out.append(dict(n=r["n"], gene=r["gene"], accession=r["accession"],
                        regulator=r["regulator"], anchors=anchors,
                        n_ligands=len(lig[r["accession"]]["ligands"]),
                        max_tanimoto=round(best, 3), nearest=best_lig,
                        nearest_name=(sm.get(best_lig) or {}).get("name"),
                        top5=pairs[:5], subset=best < 0.70))
    json.dump(out, open(f"{HERE}/v2_tanimoto.json", "w"), indent=1)
    for o in out:
        print(f"{o['n']:3d} {o['gene']:7s} {o['regulator'][:26]:26s} "
              f"max={o['max_tanimoto']:.3f} vs {o['nearest'] or '-':6s} "
              f"n_lig={o['n_ligands']:3d} {'SUBSET' if o['subset'] else ''}", flush=True)
    print(f"\nsubset (< 0.70): {sum(o['subset'] for o in out)} of {len(out)}", flush=True)
    return out


DECOY_NAME = {"3PG": "3-phosphoglycerate", "G3P": "glycerol 3-phosphate", "PEP": "phosphoenolpyruvate",
              "R5P": "ribose 5-phosphate", "G6P": "glucose 6-phosphate", "SUC": "sucrose",
              "TRE": "trehalose", "SIN": "succinate", "TAU": "taurine"}
POOL_PHOS = ["3PG", "G3P", "PEP", "R5P", "G6P"]
POOL_SUGAR = ["SUC", "TRE"]
POOL_SMALL = ["SIN", "TAU"]

ENZ_SYNONYM = {
    "PFKP": ["phosphofructokinase"], "GCK": ["glucokinase", "hexokinase IV"],
    "PKM": ["pyruvate kinase M2", "pyruvate kinase"], "PKLR": ["pyruvate kinase", "PKLR"],
    "PDHA1": ["pyruvate dehydrogenase"], "FBP1": ["fructose-1,6-bisphosphatase"],
    "PC": ["pyruvate carboxylase"], "CS": ["citrate synthase"],
    "OGDH": ["oxoglutarate dehydrogenase", "alpha-ketoglutarate dehydrogenase"],
    "G6PD": ["glucose-6-phosphate dehydrogenase"], "PGD": ["6-phosphogluconate dehydrogenase"],
    "PPAT": ["amidophosphoribosyltransferase", "glutamine phosphoribosylpyrophosphate amidotransferase"],
    "ADSS2": ["adenylosuccinate synthetase"], "CTPS2": ["CTP synthase", "CTP synthetase"],
    "RRM1": ["ribonucleotide reductase"], "DCK": ["deoxycytidine kinase"],
    "PHGDH": ["phosphoglycerate dehydrogenase"], "GLUD1": ["glutamate dehydrogenase"],
    "ACACB": ["acetyl-CoA carboxylase"], "CPT1A": ["carnitine palmitoyltransferase"],
    "HMGCR": ["HMG-CoA reductase", "hydroxymethylglutaryl-CoA reductase"],
    "SAMTOR": ["SAMTOR"]}


def stage_screen():
    """PubMed safety net: does the literature link this enzyme to this decoy as a regulator?

    A screen, not a test. Counts only steer which combinations are adjudicated by hand.
    """
    genes = sorted({r["gene"] for r in panel()})
    out = {}
    for g in genes:
        for d in POOL_PHOS + POOL_SUGAR + POOL_SMALL:
            enz = " OR ".join(f'"{s}"[tiab]' for s in ENZ_SYNONYM[g])
            term = (f'({enz}) AND "{DECOY_NAME[d]}"[tiab] AND '
                    f'(inhibit*[tiab] OR activat*[tiab] OR allosteric[tiab] OR effector[tiab] '
                    f'OR substrate[tiab] OR binds[tiab] OR binding[tiab])')
            u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json"
                 "&retmax=3&term=" + urllib.parse.quote(term))
            r = get(u, f"screen_{g}_{d}.json", pause=0.40)
            n = int(r.get("esearchresult", {}).get("count", 0))
            out[f"{g}|{d}"] = dict(n=n, pmids=r.get("esearchresult", {}).get("idlist", []), term=term)
    json.dump(out, open(f"{HERE}/v2_decoy_screen.json", "w"), indent=1)
    for g in genes:
        row = " ".join(f"{d}:{out[f'{g}|{d}']['n']:<4d}" for d in POOL_PHOS + POOL_SUGAR + POOL_SMALL)
        print(f"{g:8s} {row}", flush=True)
    return out


# Candidate decoys skipped for an enzyme because they are its substrate, product or effector, with
# the reason recorded so the panel can be audited. Checked three ways: the catalysed reaction; the
# enzyme's own co-structure ligand set (a decoy bound in a deposited structure of the enzyme is
# flagged by v2_decoy_flags.json); and a PubMed screen (v2_decoy_screen.json), whose counts are
# co-mention noise and were used only to pick what to read.
EXCLUDE = {
    "PFKP":  {"PEP": "inhibitor of PFK-1, and the regulator of panel pair 5"},
    "GCK":   {"G6P": "reaction product"},
    "PKM":   {"PEP": "substrate"},
    "PKLR":  {"PEP": "substrate; bound in 2VGB/2VGF/2VGG/2VGI"},
    "G6PD":  {"G6P": "substrate; bound as BG6 in deposited structures"},
    "PGD":   {"3PG": "inhibitor: human 6PGD complexed with 3-phosphoglycerate, PDB 4GWK, "
                     "Hitosugi et al. Cancer Cell 2012",
              "R5P": "isomer of the reaction product ribulose-5-phosphate"},
    "PHGDH": {"3PG": "substrate; bound in deposited structures"},
    "PPAT":  {"R5P": "precursor of the substrate PRPP"},
}
# no exclusion among the nine candidates: PDHA1, FBP1, PC, CS, OGDH, ADSS2, CTPS2, RRM1, DCK,
# GLUD1, ACACB, CPT1A, HMGCR, SAMTOR.


def stage_decoys():
    """PLAN_V2.md's unchanged rule, applied per enzyme, with every substitution recorded."""
    genes = {}
    for r in panel():
        genes.setdefault(r["gene"], r["accession"])
    out, short = {}, []
    for g in sorted(genes):
        ex = EXCLUDE.get(g, {})
        phos, skipped = [], []
        for d in POOL_PHOS:
            if len(phos) == 2:
                break
            if d in ex:
                skipped.append((d, ex[d]))
            else:
                phos.append(d)
        if len(phos) < 2:
            short.append(g)
        sugar = [d for d in POOL_SUGAR if d not in ex]
        small = [d for d in POOL_SMALL if d not in ex]
        out[g] = dict(accession=genes[g], decoys=phos + sugar + small,
                      substitutions=[dict(skipped=d, reason=w) for d, w in skipped],
                      not_reached=[d for d in ex if d not in [x for x, _ in skipped]])
        sub = "; ".join(f"-{d} ({w[:48]})" for d, w in skipped) or "none"
        print(f"{g:8s} {','.join(out[g]['decoys']):28s} {sub}", flush=True)
    if short:
        raise SystemExit(f"phosphorylated list exhausted for {short}: stopping rather than inventing "
                         f"a replacement, per the instruction")
    json.dump(out, open(f"{HERE}/v2_decoys.json", "w"), indent=1)
    return out


YAML = """version: 1
sequences:
  - protein:
      id: A
      sequence: {seq}
  - ligand:
      id: L
      ccd: {ccd}
properties:
  - affinity:
      binder: L
"""


def stage_inputs():
    """One yaml per complex in inputs_v2/, byte-identical in form to v1's inputs/.

    Decoys belong to the enzyme, not to the pair, exactly as in v1, where GLUD1's and PFKL's two
    regulators each shared one six-decoy panel. So the 32 pairs x 7 complexes are evaluated over
    32 regulator complexes plus 6 per enzyme, not over 224 separate predictions.
    """
    seqs = json.load(open(f"{HERE}/v2_sequences.json"))
    chem = json.load(open(f"{HERE}/v2_chem.json"))
    dec = json.load(open(f"{HERE}/v2_decoys.json"))
    rows = panel()
    d = f"{HERE}/inputs_v2"; os.makedirs(d, exist_ok=True)
    plan, written = {}, []
    for g in sorted(dec):
        regs = [chem[r["regulator"]]["anchors"][0]["ccd"] for r in rows if r["gene"] == g]
        plan[g] = dict(uniprot=dec[g]["accession"], length=seqs[g]["length"], regulators=regs,
                       decoys=dec[g]["decoys"], excluded=sorted(EXCLUDE.get(g, {})),
                       pairs=[r["n"] for r in rows if r["gene"] == g])
        for ccd, kind in [(c, "true") for c in regs] + [(c, "decoy") for c in dec[g]["decoys"]]:
            name = f"{g}__{ccd}__{kind}"
            open(f"{d}/{name}.yaml", "w").write(YAML.format(seq=seqs[g]["sequence"], ccd=ccd))
            written.append(name)
    json.dump(plan, open(f"{HERE}/benchmark_plan_v2.json", "w"), indent=1)
    n_true = sum(len(v["regulators"]) for v in plan.values())
    n_dec = sum(len(v["decoys"]) for v in plan.values())
    print(f"{len(written)} input files in inputs_v2/: {n_true} regulator + {n_dec} decoy complexes "
          f"over {len(plan)} enzymes", flush=True)
    print(f"{len(rows)} pairs x 7 = {len(rows) * 7} pair-complex slots, "
          f"{len(written)} distinct predictions (decoys shared per enzyme, as in v1)", flush=True)
    return plan


def stage_cost():
    """Wall-clock and memory estimate from v1's measured runs, per target length."""
    import numpy as np
    plan1 = json.load(open(f"{HERE}/benchmark_plan.json"))
    obs = []
    for line in open(f"{HERE}/runs/timing.tsv"):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        if f[3] == "fp32" and f[4] == "3x5":
            obs.append((plan1[f[0].split("__")[0]]["length"], float(f[2])))
    L = np.array([x for x, _ in obs]); T = np.array([t for _, t in obs])
    b, a = np.polyfit(np.log(L), np.log(T), 1); k = np.exp(a)
    err = np.median(abs(k * L ** b - T) / T)
    quad = np.polyfit(L, T, 2)
    # v1's own queue: 67 complexes, 44.5 cpu-slot hours, launched 2026-10-26 11:12:09 and ALL DONE
    # 2026-10-27 02:39:56, so 15.46 h wall against 14.82 h ideal. 3-worker packing was near perfect.
    REALISATION = 1.04
    # per-process peak RSS, fitted on the two measured points (331 aa 16.9 GB, 780 aa 23.3 GB)
    rb = (23.3 - 16.9) / (780 ** 2 - 331 ** 2); ra = 16.9 - rb * 331 ** 2

    def secs(x): return k * x ** b
    def rss(x): return ra + rb * x ** 2

    plan = json.load(open(f"{HERE}/benchmark_plan_v2.json"))
    rows = sorted(plan.items(), key=lambda kv: -kv[1]["length"])
    print(f"fit on {len(obs)} v1 complexes (fp32, 3 workers x 5 threads, 318-780 aa):")
    print(f"  T = {k:.4g} * L^{b:.3f} s, median error {err*100:.1f}%")
    print(f"  peak RSS = {ra:.1f} + {rb:.3g}*L^2 GB per boltz process\n")
    print(f"{'enzyme':8s} {'len':>5s} {'cplx':>4s} {'s/cplx':>7s} {'cpu-h':>7s} {'RSS GB':>7s} "
          f"{'workers':>7s}  note")
    tot_s = tot_wall = 0.0
    for g, v in rows:
        n = len(v["regulators"]) + len(v["decoys"]); s = secs(v["length"]); m = rss(v["length"])
        w = 3 if m * 3 <= 110 else (2 if m * 2 <= 110 else 1)
        note = "beyond fitted range" if v["length"] > 780 else ""
        if m > 110:
            w, note = 1, "WILL NOT FIT in 128 GB"
        tot_s += n * s; tot_wall += n * s / w
        print(f"{g:8s} {v['length']:5d} {n:4d} {s:7.0f} {n*s/3600:7.1f} {m:7.1f} {w:7d}  {note}")
    print(f"\ntotal {sum(len(v['regulators'])+len(v['decoys']) for _, v in rows)} complexes, "
          f"{tot_s/3600:.0f} cpu-slot hours")
    print(f"  3 workers throughout (ignores memory): {tot_s/3/3600/24:.1f} days")
    print(f"  memory-aware worker counts:            {tot_wall/3600/24:.1f} days")
    qt = qw = 0.0
    for g, v in rows:
        n = len(v["regulators"]) + len(v["decoys"]); s = float(np.polyval(quad, v["length"]))
        m = rss(v["length"]); w = 3 if m * 3 <= 110 else (2 if m * 2 <= 110 else 1)
        qt += n * s; qw += n * s / w
    print(f"  quadratic fit instead of the power law:  {qw/3600/24:.1f} days memory-aware "
          f"({qt/3600:.0f} cpu-slot hours)")
    print(f"  x{REALISATION} for v1's measured scheduling realisation: "
          f"{tot_wall*REALISATION/3600/24:.1f} to {qw*REALISATION/3600/24:.1f} days")
    big = [g for g, v in rows if rss(v["length"]) > 110]
    if big:
        s2 = sum((len(v["regulators"]) + len(v["decoys"])) * secs(v["length"])
                 for g, v in rows if g not in big)
        w2 = sum((len(v["regulators"]) + len(v["decoys"])) * secs(v["length"]) /
                 (3 if rss(v["length"]) * 3 <= 110 else 2 if rss(v["length"]) * 2 <= 110 else 1)
                 for g, v in rows if g not in big)
        print(f"  excluding {','.join(big)}: {s2/3600:.0f} cpu-slot hours, "
              f"{w2/3600/24:.1f} days memory-aware")
    return None
