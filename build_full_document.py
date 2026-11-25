"""Assemble the single shareable boltzbench document: main text, supplementary
figures, supplementary tables. Sources: manuscript.md, LABEL_AUDIT_2026-11-07.md,
v2_table.md. Writes boltzbench_full_<date>.md and the matching PDF.
Nothing here edits manuscript.md."""
import re, subprocess, sys
from pathlib import Path

DATE = "2026-11-16"
HERE = Path(__file__).parent

ms = (HERE / "manuscript.md").read_text()
ms = ms.split("## BEFORE SUBMISSION")[0].rstrip().rstrip("-").rstrip()
ms = ms.replace("*Draft, 7 November 2026*", "*Draft, 16 November 2026*")

# 1. lift the supplementary-figure block out of the body; it moves to the back
m = re.search(r"\n## Supplementary figures\n(.*?)\n## Data and code availability\n",
              ms, re.S)
if not m:
    sys.exit("supplementary figure block not found")
supp_figs = m.group(1).strip()
ms = ms[:m.start()] + "\n## Data and code availability\n" + ms[m.end():]

# the S4 stub lives with the tables now, not with the figures
supp_figs = re.sub(r"\n\*\*S4\.\*\*.*?(?=\n\n|\Z)", "", supp_figs, flags=re.S).strip()

# 2. the label-audit table is in this document now, not only in the deposit
ms = ms.replace(
    "**The full per-pair table**, with the verdict, the best citation, the species and isoform "
    "actually studied and the unverified fields for all 32 pairs, is deposited with the analysis "
    "as the label audit.",
    "**The full per-pair audit** is Supplementary Table S1 below, with the verdict, the best "
    "citation and the species and isoform actually studied for all 32 pairs.")
ms = ms.replace("The per-pair table with all citations and flags is deposited.",
                "The per-pair table with all citations and flags is Supplementary Table S1.")

# 3. supplementary tables, built from the working records
audit = (HERE / "LABEL_AUDIT_2026-11-07.md").read_text()
audit = audit.split("\n", 1)[1]                      # drop its own H1
audit = audit.replace("Post-hoc. Each of the 32 pairs", "Each of the 32 pairs")
audit = audit.replace("The registered positive narrows.", "The primary result narrows.")
audit = re.sub(r"^## ([A-F])\.", r"**\1.**", audit, flags=re.M)
audit = audit.strip()

# the 9-column screen table is emitted as LaTeX: pandoc's own table is too narrow
raw = [l for l in (HERE / "v2_table.md").read_text().strip().split("\n") if l.startswith("|")]
body = [l for l in raw[2:]]
HDR = ["\\#", "enzyme (gene field)", "resolved", "regulator", "T1 lit (PubMed n)",
       "T2 co-structure", "T3 affinity", "T4 human", "verdict"]
W = [0.025, 0.105, 0.085, 0.145, 0.085, 0.175, 0.135, 0.055, 0.075]

def tex(cell):
    cell = cell.strip()
    bold = cell.startswith("**") and cell.endswith("**")
    cell = cell.strip("*")
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("#", r"\#"), ("_", r"\_"), ("~", r"\textasciitilde{}")):
        cell = cell.replace(a, b)
    return "\\textbf{" + cell + "}" if bold else cell

CAPTION_S2 = (
    "Every pair collected, with its result on each of the four tests described in Methods and the "
    "resulting verdict. Test 1, on-topic primary literature, reports the PubMed hit count. Test 2, "
    "absence of a co-structure, reports the PDB chemical component codes found and their entry counts, "
    "so each elimination names its cause. Test 3 is absence of a binding measurement in ChEMBL and "
    "BindingDB. Test 4 requires a reviewed human UniProt entry whose primary gene name matches. "
    "A pair enters the panel only by passing all four.")

rows = []
for line in body:
    cells = [c for c in line.strip().strip("|").split("|")]
    rows.append(" & ".join(tex(c) for c in cells) + r" \\")
spec = "".join(">{\\raggedright\\arraybackslash}p{%.3f\\linewidth}" % w for w in W)
panel = "\n".join([
    r"\begin{landscape}",
    r"\subsubsection*{Table S2. Candidate screen, all %d enzyme-metabolite pairs}" % len(body),
    CAPTION_S2, r"\vspace{0.6em}", r"\footnotesize",
    r"\begin{longtable}{@{}" + spec + r"@{}}",
    r"\toprule", " & ".join(HDR) + r" \\", r"\midrule", r"\endfirsthead",
    r"\toprule", " & ".join(HDR) + r" \\", r"\midrule", r"\endhead",
    *rows,
    r"\bottomrule", r"\end{longtable}", r"\end{landscape}"])
n_rows = len(body)

doc = f"""{ms}

\\newpage

# Supplementary information

## Supplementary figures

{supp_figs}

\\newpage

## Supplementary tables

### Table S1. Label audit of the 32 pairs

{audit}

\\newpage

{panel}
"""

out_md = HERE / f"boltzbench_full_{DATE}.md"
out_md.write_text(doc)
out_pdf = HERE / f"boltzbench_full_{DATE}.pdf"
subprocess.run(["pandoc", str(out_md), "-o", str(out_pdf),
                "--pdf-engine=xelatex", "-H", str(HERE / "_full_header.tex")], check=True)
print(f"wrote {out_md.name} ({len(doc.splitlines())} lines) and {out_pdf.name}")
