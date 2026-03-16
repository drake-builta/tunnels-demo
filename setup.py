import requests
import io

import pandas as pd

inventory_xml_path = "https://www.fhwa.dot.gov/bridge/inspection/tunnel/inventory/download/2025NTI.xml"

response = requests.get(inventory_xml_path)

xml_content = response.content.replace(b'\x00', b'')

# Primary dataset (row per tunnel)
df =     pd.read_xml(io.BytesIO(xml_content), dtype="object", xpath="//TunnelInstance")

# Secondary dataset (row per tunnel element)
df_els = pd.read_xml(io.BytesIO(xml_content), dtype="object", xpath="//FHWAED")

# Export to csv
df.to_csv('tunnels.csv')
df_els.to_csv('elements.csv')
