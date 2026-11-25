# v2 candidate pairs, enumerated 2026-10-28 before any exposure check

**This list is fixed and hashed before any PDB, ChEMBL or BindingDB query is run.** Which pairs
survive the filter is the result of the filter, not of my judgement about which ones would be
interesting. Nothing is added after the checks begin and nothing is removed except by the four tests
in PLAN_V2.md.

## Enumeration rule, applied

Sweep these pathways in order and list every human enzyme with documented allosteric or feedback
regulation, and every metabolite documented to regulate it: glycolysis, gluconeogenesis, TCA cycle,
pentose phosphate, purine synthesis, pyrimidine synthesis, ribonucleotide reduction, amino acid
synthesis and catabolism, fatty acid synthesis and oxidation, urea cycle, and cellular energy and
amino acid sensing.

**No pair was skipped because I expected it to have a structure.** Several below are certain to fail
test 2, including the twelve that formed v1; they are listed anyway so that the filter's output is
reproducible from this file alone.

## Candidates

| enzyme (gene) | regulator | direction | pathway |
|---|---|---|---|
| PFKL / PFKM / PFKP | ATP | inhibitor | glycolysis |
| PFKL / PFKM / PFKP | citrate | inhibitor | glycolysis |
| PFKL / PFKM / PFKP | fructose-2,6-bisphosphate | activator | glycolysis |
| PFKL / PFKM / PFKP | AMP | activator | glycolysis |
| PFKL / PFKM / PFKP | phosphoenolpyruvate | inhibitor | glycolysis |
| HK1 / HK2 | glucose-6-phosphate | inhibitor | glycolysis |
| GCK | fructose-6-phosphate | inhibitor (via GKRP) | glycolysis |
| GCK | palmitoyl-CoA | inhibitor | glycolysis |
| PKM | fructose-1,6-bisphosphate | activator | glycolysis |
| PKM | serine | activator | glycolysis |
| PKM | alanine | inhibitor | glycolysis |
| PKM | phenylalanine | inhibitor | glycolysis |
| PKM | SAICAR | activator | glycolysis |
| PKLR | fructose-1,6-bisphosphate | activator | glycolysis |
| PKLR | alanine | inhibitor | glycolysis |
| PDHA1 | acetyl-CoA | inhibitor | pyruvate oxidation |
| PDHA1 | NADH | inhibitor | pyruvate oxidation |
| FBP1 | AMP | inhibitor | gluconeogenesis |
| FBP1 | fructose-2,6-bisphosphate | inhibitor | gluconeogenesis |
| PC | acetyl-CoA | activator | gluconeogenesis |
| PC | aspartate | inhibitor | gluconeogenesis |
| CS | NADH | inhibitor | TCA |
| CS | succinyl-CoA | inhibitor | TCA |
| IDH3A | ADP | activator | TCA |
| IDH3A | ATP | inhibitor | TCA |
| IDH3A | NADH | inhibitor | TCA |
| OGDH | succinyl-CoA | inhibitor | TCA |
| OGDH | NADH | inhibitor | TCA |
| OGDH | AMP | activator | TCA |
| SDHA | oxaloacetate | inhibitor | TCA |
| G6PD | NADPH | inhibitor | pentose phosphate |
| G6PD | NADP+ | structural / required | pentose phosphate |
| PGD | NADPH | inhibitor | pentose phosphate |
| PPAT | AMP | inhibitor | purine synthesis |
| PPAT | GMP | inhibitor | purine synthesis |
| PPAT | ADP | inhibitor | purine synthesis |
| PPAT | PRPP | activator | purine synthesis |
| PRPS1 | ADP | inhibitor | purine synthesis |
| PRPS1 | GDP | inhibitor | purine synthesis |
| PRPS1 | phosphate | activator | purine synthesis |
| IMPDH1 / IMPDH2 | GTP | inhibitor | purine synthesis |
| IMPDH1 / IMPDH2 | ATP | activator | purine synthesis |
| ADSS2 | GTP | substrate / regulator | purine synthesis |
| CAD | UTP | inhibitor | pyrimidine synthesis |
| CAD | PRPP | activator | pyrimidine synthesis |
| CTPS1 / CTPS2 | CTP | inhibitor | pyrimidine synthesis |
| CTPS1 / CTPS2 | GTP | activator | pyrimidine synthesis |
| RRM1 | dATP | inhibitor | ribonucleotide reduction |
| RRM1 | ATP | activator | ribonucleotide reduction |
| RRM1 | dGTP | specificity | ribonucleotide reduction |
| RRM1 | dTTP | specificity | ribonucleotide reduction |
| TK1 | dTTP | inhibitor | nucleotide salvage |
| DCK | dCTP | inhibitor | nucleotide salvage |
| PHGDH | serine | inhibitor | amino acid synthesis |
| GLS | phosphate | activator | glutamine catabolism |
| GLS | glutamate | inhibitor | glutamine catabolism |
| GLUD1 | GTP | inhibitor | glutamate dehydrogenase |
| GLUD1 | ADP | activator | glutamate dehydrogenase |
| GLUD1 | leucine | activator | glutamate dehydrogenase |
| GLUD1 | palmitoyl-CoA | inhibitor | glutamate dehydrogenase |
| CBS | S-adenosylmethionine | activator | transsulfuration |
| MAT2A | S-adenosylmethionine | inhibitor | methionine cycle |
| ACACA / ACACB | citrate | activator | fatty acid synthesis |
| ACACA / ACACB | palmitoyl-CoA | inhibitor | fatty acid synthesis |
| CPT1A | malonyl-CoA | inhibitor | fatty acid oxidation |
| HMGCR | sterol / lanosterol | inhibitor | sterol synthesis |
| CPS1 | N-acetylglutamate | activator | urea cycle |
| PRKAG1 / PRKAG2 | AMP | activator | energy sensing |
| PRKAG1 / PRKAG2 | ADP | activator | energy sensing |
| PRKAG1 / PRKAG2 | ATP | antagonist | energy sensing |
| SESN2 | leucine | sensor ligand | amino acid sensing |
| CASTOR1 | arginine | sensor ligand | amino acid sensing |
| SAMTOR | S-adenosylmethionine | sensor ligand | amino acid sensing |

**73 candidate pairs.** Multi-gene rows (PFK isoforms, IMPDH1/2, CTPS1/2, ACACA/B, PRKAG1/2) are
resolved to a single human gene at check time by taking the isoform with the most PDB entries, so that
test 2 is applied to the best-characterised member and the filter is conservative.

## What happens next

The three exposure checks in PLAN_V2.md are applied to every row. The surviving set is the panel, and
it is reported with its size whatever that size is. If fewer than 8 survive, PLAN_V2.md's stopping rule
applies and the benchmark is not run.
