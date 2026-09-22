"""Debug script: test NOAA ERDDAP satellite data queries directly, before
wiring them into the real pipeline. This is deliberately separate from
data_layer.py so we can verify the exact working query/dataset/variable
names first - we got burned once already (INCOIS) by integrating before
confirming things actually work end-to-end.

Run with: python debug_erddap.py
"""

import requests

# Kochi, India - a real coastal point to test against
TEST_LAT = 9.9312
TEST_LON = 76.2673
BOX = 0.3  # degrees around the point (~30km) - matches typical PFZ range

lat_min, lat_max = TEST_LAT - BOX, TEST_LAT + BOX
lon_min, lon_max = TEST_LON - BOX, TEST_LON + BOX


def test_sst():
    print("=== Testing SST (jplMURSST41 / analysed_sst, polarwatch.noaa.gov) ===")
    url = (
        "https://polarwatch.noaa.gov/erddap/griddap/jplMURSST41.json"
        f"?analysed_sst[(last)][({lat_min}):({lat_max})][({lon_min}):({lon_max})]"
    )
    print(f"URL: {url}")
    try:
        resp = requests.get(url, timeout=20)
        print(f"Status: {resp.status_code}")
        print(f"First 500 chars: {resp.text[:500]}")
    except Exception as e:
        print(f"ERROR: {e}")


def test_chlorophyll():
    print("\n=== Testing Chlorophyll (erdMH1chla8day / chlor_a, polarwatch.noaa.gov) ===")
    url = (
        "https://polarwatch.noaa.gov/erddap/griddap/erdMH1chla8day.json"
        f"?chlor_a[(last)][({lat_min}):({lat_max})][({lon_min}):({lon_max})]"
    )
    print(f"URL: {url}")
    try:
        resp = requests.get(url, timeout=20)
        print(f"Status: {resp.status_code}")
        print(f"First 500 chars: {resp.text[:500]}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    test_sst()
    test_chlorophyll()
