"""run_all.py -- executes the whole pipeline in order (run from the scripts/ folder)."""
import subprocess, sys
for s in ["00_export_data.py", "01_verify_tables.py", "02_composite_score.py", "03_sensitivity.py", "04_figures.py", "05_reproduce_from_stored_scores.py"]:
    print(f"\n===== {s} =====")
    r = subprocess.run([sys.executable, s])
    if r.returncode: sys.exit(r.returncode)
