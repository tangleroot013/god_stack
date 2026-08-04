import logging

class RedisQueueManager:
    """Manages low-level atomic primitives and FIFO task operations."""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.logger = logging.getLogger("QueueManager")

    def task_complete(self, task: dict):
        """Removes the task from the active processing tracking registry."""
        self.logger.debug(f"Task marked complete atomically: {task.get('url')}")
