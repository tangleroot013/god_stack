Adapter for stunning-octo-funicular

A minimal adapter shim (stunning_octo_adapter.py) has been added to this repo.
It exposes an `adapter` object with a `run(args: List[str]) -> int` method.

This allows stunning-octo-funicular to import the adapter directly (or call it
via PYTHONPATH) and run safe maintenance commands in the context of this repo.

Usage:

  PYTHONPATH=/path/to/god_stack python -c "import stunning_octo_adapter; stunning_octo_adapter.adapter.run(['--exec'])"
