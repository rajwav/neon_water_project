import os
import io
import zipfile
import requests
import pandas as pd

TOKEN = os.environ["NEON_API_TOKEN"]

BASE = "https://data.neonscience.org/api/v0"

# Start with 5 freshwater sites.
SITES = [
    "ARIK",
    "BARC",
    "BIGC",
    "BLDE",
    "BLUE",
]

YEARS = [2024, 2025]

HEADERS = {
    "X-API-Token": TOKEN
}

OUTPUT_DIR = "neon_raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_month_package(site, month):
    url = f"{BASE}/data/package/DP1.20288.001/{site}/{month}?package=basic"

    print(f"Downloading {site} {month} ...")

    response = requests.get(url, headers=HEADERS, timeout=120)
    response.raise_for_status()

    return response.content


def extract_waq(zip_bytes, site, month):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:

        files = [
            name for name in z.namelist()
            if "waq_instantaneous" in name
            and name.endswith(".csv")
        ]

        if not files:
            print(f"  No waq_instantaneous file found.")
            return

        for filename in files:

            output = os.path.join(
                OUTPUT_DIR,
                f"{site}_{month}_{os.path.basename(filename)}"
            )

            with z.open(filename) as source, open(output, "wb") as target:
                target.write(source.read())

            print(f"  Saved: {output}")


for site in SITES:

    for year in YEARS:

        for month_num in range(1, 13):

            month = f"{year}-{month_num:02d}"

            try:
                package = get_month_package(site, month)
                extract_waq(package, site, month)

            except requests.HTTPError as e:
                print(f"  Skipping {site} {month}: {e}")

            except Exception as e:
                print(f"  Error {site} {month}: {e}")


print("\nDownload complete.")

