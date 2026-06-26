import re
from pathlib import Path

target = Path("utils/broadcast_server.py")
content = target.read_text()

# Locate the main block and inject the resource limit code cleanly
patch = """if __name__ == "__main__":
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target_limit = min(65535, hard)
        resource.setrlimit(resource.RLIMIT_NOFILE, (target_limit, hard))
        print(f"🔓 OS File Descriptor Limits bumped to: {target_limit}")
    except Exception as limit_err:
        print(f"⚠️ Could not bump file limits: {limit_err}")"""

# Replace standard main entry point
if 'if __name__ == "__main__":' in content:
    content = content.replace('if __name__ == "__main__":', patch)
    target.write_text(content)
    print("✅ utils/broadcast_server.py successfully patched!")
else:
    print("❌ Could not automatically find the __main__ block. Please edit the file manually.")
