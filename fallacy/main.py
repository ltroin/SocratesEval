import sys
import glob
import subprocess

def run_scripts(pattern: str):
    """
    Find all Python scripts matching the given pattern in the current directory,
    sort them by filename, and execute each one sequentially.
    """
    scripts = sorted(glob.glob(pattern))
    if not scripts:
        print(f"No scripts found for pattern: {pattern}")
        return
    for script in scripts:
        print(f">>> Running {script} ...")
        # Execute the script using the current Python interpreter
        subprocess.run([sys.executable, script], check=True)
        print(f"<<< Finished {script}")

def main():
    # Step 1: Run all explanation_{model}.py scripts
    run_scripts("explanation_*.py")

    # Step 2: Run merge.py after all explanation scripts are finished
    print(">>> Running merge.py ...")
    subprocess.run([sys.executable, "merge.py"], check=True)
    print("<<< Finished merge.py")

    # Step 3: Run all evaluator_{model}.py scripts
    run_scripts("evaluator_*.py")

if __name__ == "__main__":
    main()
