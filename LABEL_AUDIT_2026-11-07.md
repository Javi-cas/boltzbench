# Label audit of the v2 panel, 7 November 2026

Post-hoc. Each of the 32 pairs was checked against primary literature to answer two questions: does a
verifiable citation exist, and does the regulation hold for the human protein named in the panel. Done by
four parallel literature agents, one per pathway block. Every citation below was verified against at least
one renderable bibliographic source; nothing was reconstructed from memory, and pairs with no verifiable
primary source are recorded as NOT FOUND rather than given a plausible reference.

**Outcome: 14 of 32 pairs carry a flag.** Four are invalid, three are keyed to the wrong protein, seven are
mechanism-mislabelled or rest on thin evidence.

## A. Invalid: the regulation does not hold for the human protein, or is not a regulation (4)

| pair | finding | source |
|---|---|---|
| PHGDH / serine | Directly tested and absent in human. Serine feedback via the ACT domain is a bacterial type III PGDH property; human PHGDH is type I with the serine-binding residues mutated. | Murtas et al. 2021 Int J Mol Sci 22:4231 (tested directly, no inhibition); Unterlass et al. 2017 Oncotarget; Riva et al. 2024 Protein Sci |
| PC / aspartate | Aspartate inhibits microbial and fungal PC. Vertebrate PC is insensitive and is inhibited by glutamate instead. | Zeczycki, St. Maurice & Attwood 2010; Adina-Zada et al. 2012. Nearest primary is Rhizobium etli (Sirithanakorn et al. 2014) |
| OGDH / AMP | AMP activation is bacterial and plant. The animal complex is activated by ADP, Pi and Ca2+. | Strumilo 2005 Biochemistry (Moscow) 70:726. Nearest primary is cauliflower (Wedding & Black 1971) |
| ADSS2 / GTP | GTP is a substrate of adenylosuccinate synthetase (IMP + Asp + GTP to adenylosuccinate + GDP + Pi), not an effector. The panel scored this pair 1.000 on both metrics. | Reaction stoichiometry; Van der Weyden & Kelley 1974 characterises the human placental activity but predates isoform cloning |

## B. Keyed to the wrong protein (3)

All three ask the model to dock a ligand onto a subunit that does not carry its site, which single-chain
input makes worse.

| pair | where the site actually is |
|---|---|
| PDHA1 / NADH | NADH inhibits versus NAD+ at the E3 component, the shared dihydrolipoyl dehydrogenase DLD (P09622), not PDHA1 |
| OGDH / NADH | Same: E3 / DLD, not the OGDH E1 subunit |
| PDHA1 / acetyl-CoA | Product inhibition at the E2 transacetylase site competing with CoA, plus indirect action through the acetyl-CoA/CoA ratio activating PDH kinase, which phosphorylates PDHA1. Not a direct allosteric site on P08559 |

## C. Mechanism mislabelled, or evidence thin (7)

| pair | finding |
|---|---|
| CS / NADH | In eukaryotic enzymes NADH competes at the acetyl-CoA site (isosteric). Genuinely allosteric NADH inhibition is specific to Gram-negative bacteria. Harford & Weitzman 1975 (pig heart against Bacillus megaterium and Pseudomonas aeruginosa) |
| PGD / NADPH | Product inhibition, not established allosteric feedback. No human primary paper found; the modern 6PGD literature reserves NADPH feedback for G6PD |
| PPAT / PRPP | PRPP is the substrate, so this is substrate-driven reversal of nucleotide inhibition, not heterotropic activation. Holmes, Wyngaarden & Kelley 1973 JBC 248:6035 |
| ACACB / palmitoyl-CoA | No study on purified or recombinant human ACC2. Classical work is avian (Goodridge 1972) and rat adipose (Halestrap & Denton 1974), both effectively ACC1 |
| PFKP / phosphoenolpyruvate | PEP is a canonical allosteric inhibitor of bacterial PFK-1, not mammalian. The only human evidence is one 2020 measurement (Fernandes et al., ATP specificity constant down 40%) |
| HMGCR / lanosterol | Insig-mediated sterol-accelerated degradation through the sterol-sensing domain, not allosteric inhibition of catalysis. Song, Javitt & DeBose-Boyd 2005 Cell Metab 1:179 |
| SAMTOR / S-adenosylmethionine | SAMTOR is a SAM-binding sensor upstream of mTORC1, not a metabolic enzyme with a catalytic activity to inhibit. Gu et al. 2017 Science 358:813 |

## D. The 18 that hold, with their best citation

| pair | citation | species / isoform note |
|---|---|---|
| PFKP / citrate | Fernandes et al. 2020 Biochem J 477:4425 (IC50 177 uM) | human PFKP. Classical work (Garland, Randle & Newsholme 1963; Pogson & Randle 1966) is rat heart PFKM |
| PFKP / fructose-2,6-bisphosphate | Fernandes et al. 2020 (AC50 9.13 uM) | human PFKP. Effector discovered on rat liver PFKL (Van Schaftingen, Hue & Hers 1980) |
| PFKP / AMP | Fernandes et al. 2020 (ATP specificity +220%) | human PFKP. Classical attribution (Passonneau & Lowry 1962) is textbook-level with no single establishing paper |
| GCK / palmitoyl-CoA | Dawson CM & Hales CN 1969 BBA 176:657 (PMID 5800058, DOI 10.1016/0005-2760(69)90238-0); Tippett & Neet 1982 JBC 257:12839 | rat liver |
| PKM / SAICAR | Keller, Tan & Lee 2012 Science 338:1069 | human, PKM2-specific |
| PKLR / alanine | Fenton & Hutchinson 2009 ABB 484:16; Llorente, Marco & Sols 1970 EJB 13:45 | human recombinant liver PK; classical is rat |
| FBP1 / fructose-2,6-bisphosphate | Van Schaftingen & Hers 1981 PNAS 78:2861 (PMID 6265919, DOI 10.1073/pnas.78.5.2861); co-discovered independently by Pilkis et al. 1981 JBC 256:3619 (PMID 6260770) | rat liver |
| CS / succinyl-CoA | Smith & Williamson 1971 FEBS Lett 18:35 | bovine heart (species assignment secondhand) |
| OGDH / succinyl-CoA | Kiselevsky, Ostrovtsova & Strumilo 1990 Acta Biochim Pol 37:135 (Ki about 81 uM) | human heart complex, not isolated E1 |
| G6PD / NADPH | Luzzatto 1967 BBA 146:18 | human erythrocyte |
| PPAT / GMP | Caskey, Ashton & Wyngaarden 1964 JBC 239:2570; Holmes et al. 1973 JBC 248:144 | pigeon liver; human enzyme. Two-site mechanism, 6-oxopurine site |
| PPAT / ADP | same two papers | 6-aminopurine site |
| CTPS2 / GTP | Levitzki & Koshland 1972 Biochemistry 11:241; Kassel et al. 2010 JBC 285:33727 | E. coli; human CTPS2-specific |
| RRM1 / dGTP | Eriksson, Thelander & Akerman 1979 Biochemistry 18:2948 | calf thymus. Correctly the specificity site on R1, not the activity site |
| DCK / dCTP | Kim & Ives 1989 Biochemistry 28:9043 | human. End-product inhibition at the active site rather than a separate allosteric site |
| GLUD1 / palmitoyl-CoA | Kawaguchi & Bloch 1976 JBC 251:1406 | mammalian liver GDH. The one explicitly human paper (Son et al. 2012) used GLUD2, not GLUD1 |
| ACACB / citrate | Locke et al. 2008 ABB 475:72 | human recombinant ACC2, isoform-resolved against ACC1 (>1000-fold vs about 4-fold) |
| CPT1A / malonyl-CoA | McGarry, Mannaerts & Foster 1977 J Clin Invest 60:265 | rat liver |

## E. Effect on the result

| label set | n | MW baseline | Boltz-2 binder prob. | critical value | hard subset |
|---|---|---|---|---|---|
| as published | 32 | 0.854 | 0.766 | 0.599 | 0.583 (n=8, p 0.27) |
| minus 4 invalid | 28 | 0.893 | 0.780 | 0.601 | 0.528 (n=6, p 0.46) |
| minus invalid and mis-keyed | 25 | 0.880 | 0.773 | 0.607 | 0.528 (n=6, p 0.46) |
| strict, minus all 14 | 18 | 0.870 | 0.741 | 0.630 | 0.633 (n=5, p 0.22) |

The central finding is unaffected: the molecular-weight baseline outranks Boltz-2's binder probability in
every label set, by a wider margin after cleaning. The decomposition is unaffected: the subset weight cannot
solve stays indistinguishable from chance throughout.

The registered positive narrows. Published it is 0.766 against a 0.599 bar; under the strictest label set it
is 0.741 against 0.630. It still clears, on roughly half the cushion.

## F. Verification limits

NCBI E-utilities, Crossref API, Europe PMC REST and Semantic Scholar are blocked at the egress proxy
used for the analysis, and pubmed.ncbi.nlm.nih.gov, jbc.org, sciencedirect.com and wiley.com refuse
automated fetches, so the citations below were first confirmed through publisher pages, Wikidata and
Scilit records, institutional repositories, and verbatim reference-list entries in accessible PMC
articles, each cross-checked against at least one independent source.

The fields left open by that pass were closed on 16 November 2026 against MEDLINE records read
through Europe PMC in a browser: Holmes et al. 1973 is PMID 4348202, Van der Weyden & Kelley 1974 is
PMID 4436310 (indexed with the second author as Kelly), and Kassel et al. 2010 is PMID 20739275 with
DOI 10.1074/jbc.M110.178566. The eukaryotic citrate synthase in Harford & Weitzman 1975 is pig heart,
and Van Schaftingen & Hers 1981 is rat liver, both from the MeSH records. Dawson & Hales 1969 carries
DOI 10.1016/0005-2760(69)90238-0. The Pilkis et al. 1981 co-discovery of fructose-2,6-bisphosphate
inhibition of FBP1 was confirmed directly (JBC 256:3619-3622, PMID 6260770) rather than through a
review's attribution.

Two fields remain open and are not used in the manuscript: the species in Bremer 1969, whose
citation in the per-pair table does not resolve to a unique 1969 record, and the content of
Garland 1964 as distinct from Garland, Randle & Newsholme 1963.

The GTP activation constants attributed to Kassel et al. 2010 in this table are quoted from a review
and were not read from the paper itself; the paper reports the kinetics of the human CTPS isozymes
including activity at physiological GTP.
