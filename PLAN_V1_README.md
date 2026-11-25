# Can Boltz-2 tell which metabolites regulate which human enzymes? (CPU benchmark)

Plan fixed before any prediction (sha256 of this README, benchmark_plan.json, run_all.py and analyze.py in PLAN.sha256).

**Question.** Given a human metabolic enzyme and a metabolite, does Boltz-2 (open structure and affinity
model, MIT licence) rank the enzyme's known allosteric or regulatory metabolite above decoys?

**Benchmark (benchmark_plan.json).** 10 enzymes, 12 established regulator pairs: AMPK gamma-1 (PRKAG1) + AMP;
FBP1 + AMP; PKM + fructose-1,6-bisphosphate; GLUD1 + GTP and ADP; PRPS1 + ADP; CTPS1 + CTP; IMPDH2 + ATP;
PPAT + AMP; G6PD + structural NADP+; PFKL + ATP and citrate. Six decoys per enzyme, the same panel throughout:
two phosphorylated non-nucleotides (from 3-phosphoglycerate, glycerol-3-phosphate, PEP, ribose-5-phosphate,
glucose-6-phosphate, skipping any that is a substrate, product or effector of that enzyme), two size-matched
neutral sugars (sucrose, trehalose), two small metabolites (succinate, taurine). 72 single-chain predictions.

**Statistic.** For each pair, the share of the 6 decoys the regulator beats, on Boltz-2's binder probability
(primary) and predicted affinity (secondary). Aggregate: mean share across pairs against the null of a
uniform rank among 7 (one-sided, 100,000 draws). Reported separately: against the phosphorylated decoys only
(does the model just reward phosphate charge?) and for sites within one chain vs at subunit interfaces
(GLUD1, PRPS1), which single-chain inputs cannot form (the lesson from the pocket analysis).

**Caveats, stated in advance.** Most of these complexes have pre-2023 PDB structures, so they are probably in
Boltz-2's training data: this measures whether the model reproduces known biology, not discovery. Single-chain
inputs miss interface sites. One diffusion sample per complex on CPU.

## Run it (your Mac's own Terminal, not the sandbox)

    cd ~/scratch/boltzbench
    python3 -m venv .venv && source .venv/bin/activate      # Python 3.10 to 3.12
    pip install "boltz==2.0.3"
    python run_all.py --only PRKAG1__AMP__true                # test: first run downloads ~6.2 GB into ~/.boltz, then times one complex
    python run_all.py                                         # all 72, resumable; leave it overnight
    python analyze.py

Note: Boltz loads its checkpoints and molecule library as Python pickles (standard for PyTorch Lightning).
They come from the Boltz authors' Hugging Face repository (boltz-community/boltz-2).
