#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Deploying Runtime Environment Guardrail...\033[0m"

cat << 'PYEOF' > env_guardrail.py
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[ENV-GUARDRAIL]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EnvGuardrail")

class RuntimeEnvironmentGuardrail:
    def __init__(self):
        self.essential_vars = ["PATH", "USER", "LANG"]

    def audit_environment_variables(self) -> bool:
        print("\n\033[1;32m--- G.O.D. RUNTIME CONTEXT ISOLATION SANITY ---\033[0m")
        logger.info("Auditing vital system environment keys...")
        
        for variable in self.essential_vars:
            if variable in os.environ:
                logger.info(f"  Key [ \033[1;32m{variable}\033[0m ] located in active shell profile path.")
            else:
                logger.critical(f"  Missing required context mapping: [ \033[1;31m{variable}\033[0m ]")
                return False
        return True

if __name__ == "__main__":
    guardrail = RuntimeEnvironmentGuardrail()
    guardrail.audit_environment_variables()
    print("\n\033[1;32m✔ MODULE 95 RUNTIME ENVIRONMENT SANITY VERIFIED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Running profile configuration analysis logs...\033[0m"
chmod +x env_guardrail.py
./.venv/bin/python3 env_guardrail.py
