#!/usr/bin/env python3
import logging
import time

logger = logging.getLogger("MatrixDaemon")

class DataAlchemist:
    @staticmethod
    def optimize_array_processing(raw_payloads: list) -> list:
        """
        Executes single-pass fast filtering over raw dictionary matrices.
        Optimized to circumvent loop-overhead metrics bloat.
        """
        start_time = time.perf_counter()
        processed_records = []
        append_record = processed_records.append  # Localized pointer reference
        
        for record in raw_payloads:
            if not isinstance(record, dict):
                continue
                
            title = record.get("title", "").strip()
            url = record.get("url", "").strip()
            score = record.get("score", 0)
            
            if not title or not url:
                continue
                
            append_record({
                "title": title,
                "url": url,
                "score": int(score) if isinstance(score, (int, float)) else 0,
                "processed_at": int(time.time())
            })
            
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"✨ [ALCHEMIST] Vectorized transformation batch completed in {duration_ms:.3f}ms")
        return processed_records
