import os
import sys
import socket
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

console = Console(force_terminal=True, legacy_windows=False)
load_dotenv()

def extract_hostname(endpoint):
    if not endpoint:
        return None
    if "://" in endpoint:
        parsed = urlparse(endpoint)
        netloc = parsed.netloc or parsed.path
        return netloc.split(":")[0]
    return endpoint.split(":")[0]

def lookup_geo(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city", "Unknown")
            region = data.get("regionName", "Unknown")
            country = data.get("country", "Unknown")
            org = data.get("org", data.get("isp", "Unknown"))
            lat = data.get("lat")
            lon = data.get("lon")
            return f"{city}, {region} ({country})", org, f"{lat}, {lon}"
    except Exception as e:
        return "Lookup failed", str(e), "N/A"
    return "Unknown", "Unknown", "N/A"

def main():
    console.print("[bold magenta]============================================================[/bold magenta]")
    console.print("[bold magenta]          DATABASE CLOUD REGION & GEOLOCATION PROBE          [/bold magenta]")
    console.print("[bold magenta]============================================================[/bold magenta]\n")
    
    endpoints = [
        ("CognoDB Cloud", os.getenv("COGNODB_URI")),
        ("Neo4j AuraDB Free", os.getenv("NEO4J_URI")),
        ("Memgraph Cloud", os.getenv("MEMGRAPH_URI")),
        ("FalkorDB Cloud", os.getenv("FALKORDB_HOST")),
        ("ArangoDB Oasis Cloud", os.getenv("ARANGODB_URL")),
    ]
    
    table = Table(title="Database Physical Location & Cloud Datacenter Audit")
    table.add_column("Database", style="cyan", no_wrap=True)
    table.add_column("Hostname / Host", style="dim")
    table.add_column("Resolved IP", style="magenta")
    table.add_column("Physical Location", style="bold yellow")
    table.add_column("ISP / Cloud Provider", style="green")
    table.add_column("US East Match?", style="bold green")
    
    for name, raw_ep in endpoints:
        host = extract_hostname(raw_ep)
        if not host:
            table.add_row(name, "N/A", "N/A", "N/A", "N/A", "[red]NO[/red]")
            continue
            
        try:
            ip = socket.gethostbyname(host)
            location, org, coords = lookup_geo(ip)
            
            # Check if location or org indicates US East (Virginia, Washington D.C., Ohio, North Carolina, etc.)
            is_us_east = any(kw in location.lower() for kw in ["virginia", "ashburn", "washington", "ohio", "north carolina", "new york", "new jersey", "us-east"]) or "us-east" in host.lower()
            
            match_str = "[bold green]YES (US East)[/bold green]" if is_us_east else f"[yellow]{location}[/yellow]"
            table.add_row(name, host, ip, location, org, match_str)
        except Exception as e:
            table.add_row(name, host, "DNS Failed", str(e), "N/A", "[red]ERROR[/red]")
            
    console.print(table)

if __name__ == "__main__":
    main()
