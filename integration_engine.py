import urllib.request
import sys

def poll_tcp_metrics(url="http://127.0.0.1:8000/metrics"):
    """Native standard-library client to query the TCP telemetry server."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read().decode("utf-8")
            print("\n\033[1;32m[TELEMETRY SUCCESS]\033[0m Received stream data:")
            print(data)
    except Exception as e:
        print(f"\n\033[1;31m[CONNECTION ERROR]\033[0m Failed to connect to metrics server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    poll_tcp_metrics()
