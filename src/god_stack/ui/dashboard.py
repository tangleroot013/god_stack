# ==============================================================================
# G.O.D. STACK COMMAND CENTER (ui/dashboard.py)
# Architecture: Rich Terminal User Interface (TUI) - Patched Alignment Matrix
# ==============================================================================

import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box

console = Console()

def generate_proxy_table() -> Table:
    """Generates a live-updating table of active egress routes."""
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("Node IP", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="green")
    table.add_column("Latency", justify="right", style="magenta")
    
    # Mock data for dashboard verification
    table.add_row("159.65.245.255:80", "ACTIVE", "142ms")
    table.add_row("174.138.119.88:80", "ACTIVE", "210ms")
    table.add_row("37.49.224.15:3128", "ACTIVE", "305ms")
    return table

def generate_system_status() -> Panel:
    """Generates the overall health and metrics panel."""
    status_text = (
        "[bold green]SYSTEM ONLINE[/bold green]\n"
        "Active Daemons: [cyan]4[/cyan]\n"
        "Proxy Mesh: [cyan]18 Nodes[/cyan]\n"
        "CAPTCHA Bypasses (1hr): [magenta]12[/magenta]\n"
        "Total Data Extracted: [yellow]4.2 GB[/yellow]"
    )
    return Panel(status_text, title="[bold white]Matrix Health[/bold white]", border_style="blue")

def build_layout() -> Layout:
    """Constructs the TUI grid layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="left_panel", ratio=2),
        Layout(name="right_panel", ratio=1)
    )
    
    # FIX: Wrap content in a Text object to handle justification correctly
    header_text = Text("G.O.D. STACK COMMAND CENTER v1.5.0", style="bold cyan", justify="center")
    
    layout["header"].update(Panel(header_text, style="white on dark_blue"))
    layout["left_panel"].update(Panel(generate_proxy_table(), title="[bold]Active Egress Routing[/bold]"))
    layout["right_panel"].update(generate_system_status())
    
    return layout

if __name__ == "__main__":
    # Render the live dashboard for testing verification
    with Live(build_layout(), refresh_per_second=4, screen=True):
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            pass
