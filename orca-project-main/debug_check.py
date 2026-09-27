"""One-off debug script: prints every real 'Layer' name IMD is currently
returning, so we can see exactly what text exists right now (rather than
guessing) and confirm whether the keyword matching is working correctly."""

from data_layer import _fetch_all_sea_bulletins, _fetch_all_coastal_bulletins

sea = _fetch_all_sea_bulletins()
coastal = _fetch_all_coastal_bulletins()

print("=== SEA BULLETIN LAYERS ===")
if isinstance(sea, list):
    for b in sea:
        print("-", b.get("Layer"))
else:
    print("Unexpected response:", sea)

print("\n=== COASTAL BULLETIN LAYERS ===")
if isinstance(coastal, list):
    for b in coastal:
        print("-", b.get("Layer"))
else:
    print("Unexpected response:", coastal)
