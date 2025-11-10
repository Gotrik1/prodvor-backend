
import socket
import sys

try:
    sock = socket.create_connection(('100.83.57.49', 5432), timeout=10)
    sock.close()
    print("SUCCESS: Connection to port 5432 is open.")
    sys.exit(0)
except Exception as e:
    print(f"FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
