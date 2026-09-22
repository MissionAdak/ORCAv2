"""One-off debug script: calls the INCOIS PFZ scraper directly and prints
the raw result, so we can see exactly what came back (or what error
occurred) instead of guessing."""

from data_layer import get_incois_pfz

result = get_incois_pfz("Kochi")
print("=== RAW RESULT ===")
print(result)
