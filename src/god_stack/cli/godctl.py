import os
import sys
import subprocess

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    wrapped_script = os.path.join(current_dir, "godctl.sh")
    if not os.path.exists(wrapped_script):
        print(f"[ERROR] Wrapped godctl bash utility not found at: {wrapped_script}", file=sys.stderr)
        sys.exit(1)
    try:
        result = subprocess.run(["bash", wrapped_script] + sys.argv[1:])
        sys.exit(result.returncode)
    except Exception as e:
        print(f"[ERROR] Failed to execute wrapped godctl script: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
