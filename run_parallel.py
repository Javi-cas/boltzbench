"""Parallel runner for the Boltz-2 benchmark (Amendment 2026-10-24b). Prediction settings are identical to run_all.py:
same inputs, `boltz predict --accelerator cpu --diffusion_samples 1 --output_format pdb`, ColabFold MSA for each protein's
first complex and that alignment reused for the protein's other complexes, same runs/<name>/ outputs, same timing.tsv.
Only the scheduling changes (2026-10-25): one queue, proteins shortest first by benchmark_plan.json length, all of a
protein's complexes consecutive (regulators first); N workers pull from it in order. A complex whose protein has no MSA
yet waits until the protein's first complex has written its alignment. Resumable: a complex is done when
predictions/<name>/ holds its model pdb, confidence json and affinity json. timing.tsv gets one row per complex the
moment it finishes (flushed and fsynced). Launch with launch.sh (nohup + caffeinate). Refuses to start if the pid in
logs/run_parallel.pid is a live run_parallel.py, or if running at nice > 0; writes its own pid. Each boltz runs in its own
process group; on SIGTERM/SIGINT the runner SIGKILLs those groups (boltz ignores SIGTERM) so none is orphaned.
2026-10-26: --min-len/--max-len restrict the queue to proteins in that length range (benchmark_plan.json) and --limit N
runs only the first N pending complexes, so the full plan can run in phases with different worker counts. A protein's MSA
is also found through the `msa:` line of an existing runs/<name>.yaml (accepted and reused runs point at their alignment
that way). timing.tsv rows: complex, returncode, seconds, precision (read from the installed boltz/main.py),
workers_x_threads, source.
usage: python run_parallel.py [--workers 3] [--threads T] [--min-len A] [--max-len B] [--limit N]"""
import argparse, glob, os, re, signal, subprocess, threading, time, json
def sysctl(k):
    try: return int(subprocess.run(["sysctl", "-n", k], capture_output=True, text=True).stdout)
    except ValueError: return None
pcores = sysctl("hw.perflevel0.physicalcpu") or os.cpu_count() or 8
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--threads", type=int)
ap.add_argument("--min-len", type=int, default=0); ap.add_argument("--max-len", type=int, default=10**6); ap.add_argument("--limit", type=int)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = f"{HERE}/runs"; os.makedirs(RUNS, exist_ok=True)
PIDF = f"{HERE}/logs/run_parallel.pid"; os.makedirs(f"{HERE}/logs", exist_ok=True)
def live_runner(pid):
    """True if pid is alive and is a run_parallel.py (not a recycled pid)."""
    try: os.kill(pid, 0)
    except (ProcessLookupError, PermissionError): return False
    return "run_parallel.py" in subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True).stdout
try: old = int(open(PIDF).read().split()[0])
except (FileNotFoundError, ValueError, IndexError): old = None
if old and old != os.getpid() and live_runner(old): raise SystemExit(f"refusing to start: run_parallel.py pid {old} is live ({PIDF})")
if os.nice(0) > 0: raise SystemExit(f"refusing to start at nice {os.nice(0)}: launch with launch.sh (nice 0)")
open(PIDF, "w").write(f"{os.getpid()}\n")
plan = json.load(open(f"{HERE}/benchmark_plan.json"))
files = sorted(glob.glob(f"{HERE}/inputs/*.yaml"), key=lambda f: (plan[os.path.basename(f).split("__")[0]]["length"],
               os.path.basename(f).split("__")[0], "__decoy" in f, f))
by_prot = {}
for f in files: by_prot.setdefault(os.path.basename(f).split("__")[0], []).append(f)
lock = threading.Lock(); threads = str(a.threads or max(1, pcores // a.workers))
import boltz.main as _bm
precision = "fp32" if "precision=32," in open(_bm.__file__).read() else "bf16-mixed"
env = dict(os.environ, OMP_NUM_THREADS=threads, MKL_NUM_THREADS=threads)
children = set()
def stop(sig, frame):
    for p in list(children):
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
    print(f"stopped by signal {sig}; killed {len(children)} boltz process groups, no timing rows written", flush=True)
    os._exit(128 + sig)
for s in (signal.SIGTERM, signal.SIGINT): signal.signal(s, stop)      # SIGHUP stays ignored (nohup)

def done(name):
    p = glob.glob(f"{RUNS}/{name}/**/predictions/{name}", recursive=True)
    return bool(p) and all(glob.glob(f"{p[0]}/{pat}") for pat in (f"{name}_model_0.pdb", f"confidence_{name}_model_0.json",
                                                                 f"affinity_{name}.json"))
def msa_of(prot):
    """raw alignment of this protein, once complete (boltz writes processed/msa/*.npz only after the csv)."""
    for f in by_prot[prot]:
        d = glob.glob(f"{RUNS}/{os.path.basename(f)[:-5]}/boltz_results_*")
        if d and glob.glob(f"{d[0]}/processed/msa/*.npz") and glob.glob(f"{d[0]}/msa/*.csv"):
            return os.path.abspath(glob.glob(f"{d[0]}/msa/*.csv")[0])
    for f in by_prot[prot]:
        y = f"{RUNS}/{os.path.basename(f)[:-5]}.yaml"
        m = os.path.exists(y) and re.search(r"^      msa: (\S+)$", open(y).read(), re.M)
        if m and os.path.exists(m.group(1)): return m.group(1)
    return None

fetching, msa_ready = set(), {p: threading.Event() for p in by_prot}
for p in by_prot:
    if msa_of(p): msa_ready[p].set()

def run(f):
    name = os.path.basename(f)[:-5]; prot = name.split("__")[0]; out = f"{RUNS}/{name}"
    with lock:
        fetch = not msa_ready[prot].is_set() and prot not in fetching
        if fetch: fetching.add(prot)
    if fetch:
        src = f; extra = ["--use_msa_server"]
    else:
        msa_ready[prot].wait(); msa = msa_of(prot)
        y = re.sub(r"(      sequence: [A-Z]+\n)", rf"\1      msa: {msa}\n", open(f).read(), count=1)
        src = f"{RUNS}/{name}.yaml"; open(src, "w").write(y); extra = []
    cmd = ["boltz", "predict", src, "--out_dir", out, "--accelerator", "cpu", "--diffusion_samples", "1", "--output_format", "pdb"] + extra
    t0 = time.time(); print(f">> {name} ({plan[prot]['length']} aa, {threads} threads{', fetching MSA' if fetch else ''})", flush=True)
    with open(f"{RUNS}/{name}.log", "w") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        children.add(proc)
        while proc.poll() is None:
            if fetch and not msa_ready[prot].is_set() and msa_of(prot): msa_ready[prot].set()
            time.sleep(10)
    children.discard(proc)
    if fetch and not msa_ready[prot].is_set():
        if not msa_of(prot): print(f"   {prot}: no MSA from {name}; its other complexes will fail", flush=True)
        msa_ready[prot].set()
    dt = time.time() - t0
    with lock, open(f"{RUNS}/timing.tsv", "a") as t:
        t.write(f"{name}\t{proc.returncode}\t{dt:.0f}\t{precision}\t{a.workers}x{threads}\trun_parallel.py\n"); t.flush(); os.fsync(t.fileno())
    print(f"   {name}: {'OK' if proc.returncode == 0 else 'FAILED (see runs/' + name + '.log)'} {dt / 60:.0f} min", flush=True)

queue = [f for f in files if not done(os.path.basename(f)[:-5])
         and a.min_len <= plan[os.path.basename(f).split("__")[0]]["length"] <= a.max_len][:a.limit]
print(f"{pcores} performance cores; {a.workers} workers x {threads} threads; precision {precision}; "
      f"length {a.min_len}-{a.max_len}{f'; limit {a.limit}' if a.limit else ''}", flush=True)
print(f"{len(queue)} of {len(files)} complexes to run now, shortest protein first: "
      f"{[(p, plan[p]['length']) for p in by_prot]}", flush=True)
def worker():
    while True:
        with lock:
            if not queue: return
            f = queue.pop(0)
        run(f)
ws = [threading.Thread(target=worker) for _ in range(a.workers)]
for w in ws: w.start()
for w in ws:
    while w.is_alive(): w.join(5)                            # timed join so the main thread can take signals
left = [os.path.basename(f)[:-5] for f in files if not done(os.path.basename(f)[:-5])]
print("ALL DONE" if not left else f"phase finished; {len(left)} of {len(files)} not yet complete: {left}", flush=True)
