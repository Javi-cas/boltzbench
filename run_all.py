"""Run the benchmark with Boltz-2 on CPU, one complex at a time, resumable.
For each protein the regulator complex runs first with the ColabFold MSA server; its alignment is then
reused for that protein's decoys, so each protein is aligned once. Timing goes to runs/timing.tsv.
usage: python run_all.py [--only PRKAG1__AMP__true]   (the test run)"""
import argparse, glob, os, re, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("--only"); a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = f"{HERE}/runs"; os.makedirs(RUNS, exist_ok=True)
files = sorted(glob.glob(f"{HERE}/inputs/*.yaml"), key=lambda f: (os.path.basename(f).split("__")[0], "__decoy" in f))
if a.only: files = [f for f in files if os.path.basename(f).startswith(a.only)]
msa = {}
for f in files:
    name = os.path.basename(f)[:-5]; prot = name.split("__")[0]; out = f"{RUNS}/{name}"
    done = glob.glob(f"{out}/**/affinity_*.json", recursive=True)
    if done:
        print("done", name); continue
    y = open(f).read(); cmd_msa = []
    if prot in msa:
        y = re.sub(r"(      sequence: [A-Z]+\n)", rf"\1      msa: {msa[prot]}\n", y, count=1)
        tmp = f"{RUNS}/{name}.yaml"; open(tmp, "w").write(y); src = tmp
    else:
        src = f; cmd_msa = ["--use_msa_server"]
    cmd = ["boltz", "predict", src, "--out_dir", out, "--accelerator", "cpu", "--diffusion_samples", "1",
           "--output_format", "pdb"] + cmd_msa
    t0 = time.time(); print(">>", name, flush=True)
    r = subprocess.run(cmd)
    dt = time.time() - t0
    open(f"{RUNS}/timing.tsv", "a").write(f"{name}\t{r.returncode}\t{dt:.0f}\n")
    if r.returncode != 0:
        print("FAILED", name, "see output above"); continue
    if prot not in msa:
        found = glob.glob(f"{out}/**/msa/*.csv", recursive=True)
        if found: msa[prot] = os.path.abspath(found[0])
    print(f"   {name}: {dt / 60:.1f} min", flush=True)
