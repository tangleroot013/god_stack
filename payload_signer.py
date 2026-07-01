#!/usr/bin/env python3
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("GodStack.PayloadSigner")

class PayloadSigner:
    def __init__(self, secret_key: str = "god_stack_default_secure_core_key_2026"):
        self.secret_key = secret_key.encode('utf-8')

    def generate_signed_frame(self, data: Dict[str, Any]) -> Tuple[str, str]:
        serialized = json.dumps(data, sort_keys=True)
        signature = hmac.new(self.secret_key, serialized.encode('utf-8'), hashlib.sha256).hexdigest()
        return serialized, signature

    def verify_frame(self, serialized_data: str, provided_signature: str) -> bool:
        expected_signature = hmac.new(self.secret_key, serialized_data.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_signature, provided_signature)
