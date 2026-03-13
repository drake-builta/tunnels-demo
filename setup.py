import requests
import io

import pandas as pd
import duckdb

inventory_xml_path = "https://www.fhwa.dot.gov/bridge/inspection/tunnel/inventory/download/2025NTI.xml"

response = requests.get(inventory_xml_path)

xml_content = response.content.replace(b'\x00', b'')

# Create and connect to a persistent database file
conn = duckdb.connect(database="nti_2025.duckdb")

# Primary dataset (row per tunnel)
df =     pd.read_xml(io.BytesIO(xml_content), dtype="object", xpath="//TunnelInstance")
conn.execute("CREATE TABLE tunnels AS SELECT * FROM df")

# Secondary dataset (row per tunnel element)
df_els = pd.read_xml(io.BytesIO(xml_content), dtype="object", xpath="//FHWAED")
conn.execute("CREATE TABLE elements AS SELECT * FROM df_els")

conn.close()
