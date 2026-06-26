import random
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("TelemetryCore")

class LatencyTelemetry:
    def __init__(self, target_nodes=None):
        self.nodes = target_nodes or ["Worker-00", "Worker-01", "Worker-02", "Broker-Edge", "Proxy-Alpha"]
        self.metrics_history = {}

    def sample_round_trip(self) -> dict:
        """Simulates network round-trip time (RTT) loops across proxy routes."""
        current_map = {}
        for source in self.nodes:
            current_map[source] = {}
            for target in self.nodes:
                if source == target:
                    current_map[source][target] = 0.0
                    continue
                
                base_latency = random.uniform(10.0, 150.0)
                if random.random() > 0.92:
                    base_latency += random.uniform(200.0, 450.0)
                
                current_map[source][target] = round(base_latency, 2)
        return current_map

    def generate_heatmap_string(self, matrix: dict) -> str:
        """Translates numerical floats into a terminal-renderable heatmap matrix."""
        lines = ["\n=== 📊 PROXY LATENCY MATRIX HEATMAP (RTT ms) ==="]
        
        # Fixed: Extracted literal string outside the expression block context
        label_text = "SRC \\ DST"
        header = f"{label_text:<12}" + "".join(f"| {node[:9]:<9}" for node in self.nodes)
        lines.append(header)
        lines.append("-" * len(header))
        
        for src in self.nodes:
            row_str = f"{src:<12}"
            for dst in self.nodes:
                val = matrix[src][dst]
                if val == 0.0:
                    symbol = "  --  "
                elif val < 50.0:
                    symbol = f"🟢 {int(val):<3}"  # Low Latency
                elif val < 150.0:
                    symbol = f"🟡 {int(val):<3}"  # Normal Transit
                else:
                    symbol = f"🔴 {int(val):<3}"  # High Jitter
                row_str += f"| {symbol:<9}"
            lines.append(row_str)
            
        lines.append("=================================================")
        return "\n".join(lines)

if __name__ == "__main__":
    telemetry = LatencyTelemetry()
    raw_matrix = telemetry.sample_round_trip()
    heatmap_output = telemetry.generate_heatmap_string(raw_matrix)
    print(heatmap_output)
