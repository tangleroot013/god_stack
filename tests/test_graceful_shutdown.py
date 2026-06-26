import pytest
import asyncio
from daemon_core import DaemonCore

@pytest.mark.asyncio
async def test_shutdown_lifecycle_state_transition():
    core = DaemonCore(max_concurrent_workers=3)
    assert core.running is True
    
    # Simulate a manual shutdown call
    # Catching the SystemExit exception raised by sys.exit(0)
    with pytest.raises(SystemExit):
        await core.initiate_shutdown()
        
    assert core.running is False
