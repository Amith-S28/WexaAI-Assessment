import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

host = "98.91.234.6"
port = 7687
pwd = os.getenv("MEMGRAPH_PASSWORD", "Jeemains@2022")
users = ["memgraph", "amithsirisilla28@gmail.com", ""]

schemes = [
    f"bolt+ssc://{host}:{port}",
    f"bolt+s://{host}:{port}",
    f"bolt://{host}:{port}",
    f"neo4j+ssc://{host}:{port}",
    f"neo4j+s://{host}:{port}",
]

print(f"Testing Memgraph on {host}:{port}...")

found = False
for u in users:
    for s in schemes:
        try:
            auth = (u, pwd) if u else None
            driver = GraphDatabase.driver(s, auth=auth, connection_timeout=4)
            with driver.session() as session:
                res = session.run("RETURN 1 AS val").single()
                print(f"[OK] SUCCESS with scheme: {s}, user: '{u}'! Result: {res['val']}")
                driver.close()
                found = True
                break
        except Exception as e:
            # print(f"Failed {s} with user '{u}': {e}")
            pass
    if found:
        break

if not found:
    print("Could not connect with tested combinations. Testing raw TCP ping...")
    import socket, time
    t0 = time.perf_counter_ns()
    try:
        sock = socket.create_connection((host, port), timeout=5)
        t1 = time.perf_counter_ns()
        sock.close()
        print(f"Raw TCP to {host}:{port} SUCCESS in {(t1-t0)/1e6:.2f} ms! (Issue is authentication/protocol)")
    except Exception as err:
        print(f"Raw TCP to {host}:{port} FAILED: {err}")
