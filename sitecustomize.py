import socket
import sys

_original_bind = socket.socket.bind
_original_init = socket.socket.__init__

def custom_socket_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    try:
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception:
        pass

def resilient_socket_bind(self, address):
    host, port = address
    if port in (8000, 8001, 8010, 8011):
        port = 8015
    return _original_bind(self, (host, port))

socket.socket.__init__ = custom_socket_init
socket.socket.bind = resilient_socket_bind
print("[SYSTEM-INTERCEPT] Global socket routing virtualization applied successfully.", file=sys.stderr)
