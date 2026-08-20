import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

host = "93.91.234.4"
port = 7687
user = os.getenv("MEMGRAPH_USER", "amithsirisilla28@gmail.com")
pwd = os.getenv("MEMGRAPH_PASSWORD", "Jeemains@2022")

schemes = [
    f"bolt://{host}:{port}",
    f"bolt+s://{host}:{port}",
    f"bolt+ssc://{host}:{port}",
    f"neo4j://{host}:{port}",
    f"neo4j+s://{host}:{port}",
    f"neo4j+ssc://{host}:{port}",
]

print("Testing Memgraph schemes...")
for s in schemes:
    print(f"Trying scheme: {s}")
    try:
        driver = GraphDatabase.driver(s, auth=(user, pwd), connection_timeout=5)
        with driver.session() as session:
            res = session.run("RETURN 1 AS val").single()
            print(f"SUCCESS with {s}! Result: {res['val']}")
            driver.close()
            break
    except Exception as e:
        print(f"Failed {s}: {e}")
