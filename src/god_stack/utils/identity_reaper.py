import logging

class IdentityReaper:
    """Automates identity lifecycle management by pruning 'BURNED' masks."""
    def __init__(self, monitor, stealth):
        self.monitor = monitor
        self.stealth = stealth
        self.logger = logging.getLogger("IdentityReaper")

    def run_reap_cycle(self) -> int:
        """Purges identities flagged as BURNED by the health matrix."""
        reaped_count = 0
        # Iterate over the Monitor's internal stats (using full UA keys)
        for ident_id in list(self.monitor.stats.keys()):
            stats = self.monitor.stats[ident_id]
            total = sum(stats.values())
            
            # Calculate reputation: status is BURNED if success rate < 50%
            success_rate = (stats["success"] / total * 100) if total > 0 else 100

            # Prune if burned and a sufficient sample size (e.g., > 5 missions) exists
            if success_rate < 50 and total > 5:
                self.logger.warning(f"🪦 Reaping BURNED identity: [{ident_id[:8]}...] (Rate: {success_rate:.1f}%)")

                # 1. Clear from Health Monitor stats
                del self.monitor.stats[ident_id]

                # 2. Safely remove from StealthManager's rotation matrix if attribute exists
                if hasattr(self.stealth, 'ua_gen') and hasattr(self.stealth.ua_gen, 'matrix'):
                    if ident_id in self.stealth.ua_gen.matrix:
                        self.stealth.ua_gen.matrix.remove(ident_id)
                        self.logger.info("♻️ Identity purged from active rotation matrix.")
                else:
                    self.logger.debug("Identity removed from telemetry queue tracking bounds.")

                reaped_count += 1
        return reaped_count
