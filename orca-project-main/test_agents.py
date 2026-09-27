import sys
import json
from pfz_agent import pfz_agent
from geo_agent import geo_agent

def main():
    state = {"location": "Chennai"}
    
    print("Testing PFZ Agent...")
    try:
        pfz_res = pfz_agent(state)
        print(json.dumps(pfz_res, indent=2))
    except Exception as e:
        print(f"PFZ Agent Error: {e}")

    print("\nTesting Geo Agent...")
    try:
        geo_res = geo_agent(state)
        print(json.dumps(geo_res, indent=2))
    except Exception as e:
        print(f"Geo Agent Error: {e}")

if __name__ == "__main__":
    main()
