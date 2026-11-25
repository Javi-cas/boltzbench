# Benchmark v2, selection step: result

Run 2026-10-28. `shasum -a 256 -c V2.sha256` passed for `PLAN_V2.md` and `CANDIDATES_V2.md` before any
database was queried, and neither file was edited. No prediction was run, no input was built and no decoy
panel was constructed. Script: `v2_select.py`. Every raw API response is cached under `v2_selection_raw/`
(about 400 files), so the filter can be re-derived without re-querying.

## Outcome

**32 of 73 candidate pairs survive all four tests.** PLAN_V2.md's stopping rule (fewer than 8 pairs, do not
run) is not triggered. At 32 pairs the panel is larger than v1's 12, so the critical value will be lower
and the power higher than the table in PLAN_V2.md, which stops at 20.

| test | pass | fail |
|---|---|---|
| 1, regulation established (PubMed screen) | 69 | 4 screened zero, all four verified by hand to have primary literature; none dropped |
| 2, no co-structure | 34 | 39 |
| 3, no deposited affinity (ChEMBL or BindingDB) | 64 | 9 |
| 4, human enzyme | 73 | 0 |
| **all four** | **32** | 41 |

Test 2 does nearly all the work. Only 2 pairs are eliminated by test 3 alone (CAD/UTP and CAD/PRPP); the
other 7 test-3 failures also lack nothing structurally, that is they fail test 2 as well.

## How each test was run

**Test 2, no co-structure.** RCSB search API, one query per chemical component so that each elimination
names the component that caused it. The protein side is a sequence search at `identity_cutoff` 0.95, not an
accession match, so a homolog above 95% identity in any organism counts, at any deposition date. The ligand
side is `rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id`, which matches the metabolite only
where it is present as a free ligand rather than as a polymer residue. Query date 2026-10-28.

**Test 3, no deposited affinity.** ChEMBL: every target whose components include the enzyme's UniProt
accession, crossed with every ChEMBL molecule sharing the metabolite's connectivity. BindingDB:
`getLigandsByUniprot` for the accession, with each returned ligand's SMILES converted to an InChIKey by
RDKit and compared on the skeleton (InChIKey block 1), which ignores protonation and stereochemistry.

**Test 4, human enzyme.** All 43 gene symbols resolve to a reviewed human UniProt entry. One correction was
needed: `gene_exact:GCK` returns MAP4K2 (germinal centre kinase) as well as glucokinase, because GCK is a
synonym for it, so the filter now requires the entry's own primary gene name to match. GCK is P35557.

**Multi-gene rows** resolved to the human isoform with the most PDB entries, as CANDIDATES_V2.md specifies:
PFKP (7 entries, over PFKL 6 and PFKM 1), IMPDH2 (25 over IMPDH1 18), CTPS2 (8 over CTPS1 7), ACACB (11 over
ACACA 10), PRKAG1 (23 over PRKAG2 0), HK1 (10 over HK2 4). **Two of these differ from v1**, which used PFKL
and CTPS1. The rule was fixed in the hashed file, so it stands, but the v1-to-v2 comparison is then not
quite like for like on those two enzymes.

## The sanity check, which did not come out as predicted

The four rows named as certain failures behave as follows.

| row | test 2 | test 3 |
|---|---|---|
| PRKAG1 / AMP | FAIL, 40 entries with AMP | FAIL, ChEMBL 13 records (EC50, Kd; AMP EC50 5900 nM) |
| GLUD1 / GTP | FAIL, 12 entries with GTP | **PASS** |
| G6PD / NADP+ | FAIL, 17 entries with NAP | **PASS** |
| PFKP / ATP | FAIL, 2 entries with ATP | **PASS** |

All four fail test 2, so the structural query is sound. Three of the four pass test 3. Your rule says that
means the query is broken, so I treated it as broken and went looking. The evidence says the queries work and
the two databases genuinely do not hold these measurements:

- The ChEMBL arm has a working positive control in the same set: PRKAG1/AMP returns 13 activities with the
  right types, found by the identical code path.
- Human GLUD1 is **not in ChEMBL at all** as a target. A direct search for glutamate dehydrogenase returns
  Bos taurus (CHEMBL4628) and Rattus (CHEMBL2176833), not P00367. The zero is the database, not the filter.
- PFKP (CHEMBL2972) and G6PD (CHEMBL5347) do have targets, carrying 228 and 797 activities respectively, so
  the targets were found; ATP and NADP simply are not among the molecules measured against them.
- The BindingDB arm parsed **2,260 of 2,260** returned ligands to an InChIKey, and a self-test confirms the
  matcher fires. None of those ligands is any of the 40 candidate metabolites.
- BindingDB returns an empty body for 4 accessions (GLUD1, SESN2, PPAT, SAMTOR). Re-queried live, each gives
  HTTP 200 with 0 bytes, consistently, so these are real absences rather than dropped requests.

The underlying reason is that ChEMBL and BindingDB are medicinal-chemistry resources. They record
drug-like compounds screened against targets, not classical enzymology on endogenous metabolites, which
lives in BRENDA and SABIO-RK. **This weakens test 3 as an exposure control considerably**: it bounds what
the affinity head could have seen from these two deposited sources, and PLAN_V2.md already says as much,
but in practice it eliminates almost nothing (2 pairs on its own). If the intent was to control the affinity
head, BRENDA or SABIO-RK would have to be added, and that would be a change to the registered rule.

## Two further things worth knowing before the panel is used

**Half the panel is chemically adjacent to an exposed pair.** The rule is per-pair, so these pass as written,
and I have not dropped them. But for 16 of the 32, the same enzyme is co-crystallised with a different
candidate metabolite, often a near neighbour at what is likely the same site:

- G6PD passes on NADPH while 17 entries hold NADP+ (a redox state apart, same site).
- RRM1 passes on dGTP while dATP, dTTP and ATP are all bound in deposited structures.
- PPAT passes on GMP, ADP and PRPP while AMP is bound.
- CTPS2 passes on GTP while CTP is bound; FBP1 passes on fructose-2,6-bisphosphate while AMP is bound;
  PKM passes on SAICAR while FBP, serine, alanine and phenylalanine are all bound.
- Also PFKP (ATP bound), GCK (F6P), PKLR (FBP), PC (acetyl-CoA), GLUD1 (GTP, ADP, leucine), ACACB.

A reader can reasonably say these pairs are not free of memorisation exposure in the sense the plan intends,
only free of exposure to that exact ligand. Tightening this would be a change to the registered rule and
would need an amendment; I have not made one.

**Test 1 is the weakest of the four as run.** A PubMed term search is a screen, not a test. Its zeros were
nomenclature artifacts: PKM/SAICAR screened zero because UniProt calls the protein "Pyruvate kinase PKM"
while the literature says "pyruvate kinase M2". Targeted searches confirm primary literature for every
low-scoring survivor (PKM/SAICAR n=9, ADSS2/GTP n=39, CTPS2/GTP n=16, PFKP/PEP n=236, RRM1/dGTP n=78,
GLUD1/palmitoyl-CoA n=27). **No row was dropped as folklore.** What I verified is that primary literature
exists and is on topic; I did not read 73 papers to confirm each regulation is established specifically by
kinetics or mutagenesis, so test 1 should be read as "literature exists" rather than as the full test.

## The surviving panel, 32 pairs

| # | enzyme | UniProt | regulator | direction | pathway |
|---|---|---|---|---|---|
| 2 | PFKP | Q01813 | citrate | inhibitor | glycolysis |
| 3 | PFKP | Q01813 | fructose-2,6-bisphosphate | activator | glycolysis |
| 4 | PFKP | Q01813 | AMP | activator | glycolysis |
| 5 | PFKP | Q01813 | phosphoenolpyruvate | inhibitor | glycolysis |
| 8 | GCK | P35557 | palmitoyl-CoA | inhibitor | glycolysis |
| 13 | PKM | P14618 | SAICAR | activator | glycolysis |
| 15 | PKLR | P30613 | alanine | inhibitor | glycolysis |
| 16 | PDHA1 | P08559 | acetyl-CoA | inhibitor | pyruvate oxidation |
| 17 | PDHA1 | P08559 | NADH | inhibitor | pyruvate oxidation |
| 19 | FBP1 | P09467 | fructose-2,6-bisphosphate | inhibitor | gluconeogenesis |
| 21 | PC | P11498 | aspartate | inhibitor | gluconeogenesis |
| 22 | CS | O75390 | NADH | inhibitor | TCA |
| 23 | CS | O75390 | succinyl-CoA | inhibitor | TCA |
| 27 | OGDH | Q02218 | succinyl-CoA | inhibitor | TCA |
| 28 | OGDH | Q02218 | NADH | inhibitor | TCA |
| 29 | OGDH | Q02218 | AMP | activator | TCA |
| 31 | G6PD | P11413 | NADPH | inhibitor | pentose phosphate |
| 33 | PGD | P52209 | NADPH | inhibitor | pentose phosphate |
| 35 | PPAT | Q06203 | GMP | inhibitor | purine synthesis |
| 36 | PPAT | Q06203 | ADP | inhibitor | purine synthesis |
| 37 | PPAT | Q06203 | PRPP | activator | purine synthesis |
| 43 | ADSS2 | P30520 | GTP | substrate / regulator | purine synthesis |
| 47 | CTPS2 | Q9NRF8 | GTP | activator | pyrimidine synthesis |
| 50 | RRM1 | P23921 | dGTP | specificity | ribonucleotide reduction |
| 53 | DCK | P27707 | dCTP | inhibitor | nucleotide salvage |
| 54 | PHGDH | O43175 | serine | inhibitor | amino acid synthesis |
| 60 | GLUD1 | P00367 | palmitoyl-CoA | inhibitor | glutamate dehydrogenase |
| 63 | ACACB | O00763 | citrate | activator | fatty acid synthesis |
| 64 | ACACB | O00763 | palmitoyl-CoA | inhibitor | fatty acid synthesis |
| 65 | CPT1A | P50416 | malonyl-CoA | inhibitor | fatty acid oxidation |
| 66 | HMGCR | P04035 | sterol / lanosterol | inhibitor | sterol synthesis |
| 73 | SAMTOR | Q1RMZ1 | S-adenosylmethionine | sensor ligand | amino acid sensing |

Enzymes represented: 22. [Corrected 2026-11-15: this line read 20, which disagreed with the 22 distinct genes in the table below and with `benchmark_plan_v2.json`, which holds 22 and is what the analysis and the manuscript use. The error was in this sentence only; no count used downstream was affected.] PFKP contributes 4 pairs, PPAT 3, OGDH 3, PDHA1, CS and ACACB 2 each. Pairs from
one enzyme share a protein and so are not independent in the way the uniform-rank null assumes; v1 had the
same property (GLUD1 and PFKL each contributed 2 of 12) but it is more pronounced here.

## Chemical identity, and one correction made during the run

Metabolites are anchored on PDB chemical components, each verified against the component dictionary's own
name and formula, then expanded through UniChem to the components and ChEMBL molecules sharing the same
connectivity. An earlier version resolved names through PubChem instead, and that was wrong: PubChem's record
for "fructose 1,6-bisphosphate" (CID 445555) is the 2,5-anhydro analogue, which resolved to components AHG
and AHM and missed every FBP co-structure. Anchoring on the component dictionary fixed it. Fructose-2,6- and
fructose-1,6-bisphosphate are correctly distinguished (FDP against FBP).

One consequence to note: skeleton matching pulls in epimers, so glucose-6-phosphate also matches mannose-6-
phosphate (M6P, M6D), and common additives count as co-structures (phosphate as PO4, free amino acids as
ALA, SER, GLU). This makes test 2 slightly over-eager, which shrinks the panel rather than inflating it.

## Files

`v2_select.py` (the filter), `v2_chem.json`, `v2_genes.json`, `v2_test1.json`, `v2_test2.json`,
`v2_test3.json`, `v2_table.md` (all 73 rows with the four results), `v2_selection_raw/` (every raw response),
`logs/v2_*_stage.log`.

Stopping here as instructed: nothing is built and nothing is run.
