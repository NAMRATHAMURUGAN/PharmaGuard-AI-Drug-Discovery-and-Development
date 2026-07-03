#!/usr/bin/env python
"""Test Warfarin + Aspirin DDI with fixed alias resolver."""

import requests
import json
import time
import threading
from layer8_dashboard import app

def run_app():
    """Run Flask in background."""
    app.run(debug=False, port=5000, use_reloader=False, threaded=True)

# Start server
thread = threading.Thread(target=run_app, daemon=True)
thread.start()
time.sleep(3)

# Test payload: Warfarin + Aspirin
payload = {
    'drug_name': 'Warfarin',
    'co_drug': 'Aspirin',
    'smiles': 'CC(CC1=CC=CC=C1)NC',  # Methamphetamine SMILES (for testing)
    'age': 35,
    'weight': 75,
    'egfr': 85,
    'alt': 20,
    'ast': 20,
    'gender': 'female',
    'conditions': 'hypertension',
    'dose_factor': 100
}

try:
    print("Testing: Warfarin + Aspirin (should be MAJOR)")
    print("-" * 50)
    
    resp = requests.post('http://127.0.0.1:5000/analyze', json=payload)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        
        print("\n✓ DDI Results:")
        print(f"  Level: {data.get('ddi_level')}")
        print(f"  Score: {data.get('ddi_score')}")
        print(f"  Method: {data.get('ddi_explanation', {}).get('method')}")
        print(f"  Lookup method: {data.get('ddi_explanation', {}).get('lookup_method')}")
        
        print("\n✓ Toxicity Results:")
        print(f"  Score: {data.get('toxicity_score')}")
        print(f"  Label: {data.get('toxicity_label')}")
        
        print("\n✓ Drug Names Resolved:")
        print(f"  drug_a: {data.get('drug_a')}")
        print(f"  drug_b: {data.get('drug_b')}")
        
        # Verify the fix worked
        expected_level = "Major"
        actual_level = data.get('ddi_level')
        
        if actual_level == expected_level:
            print(f"\n✅ SUCCESS: Got expected DDI level '{expected_level}'")
        else:
            print(f"\n❌ FAILED: Expected '{expected_level}', got '{actual_level}'")
    else:
        print(f"Error: {resp.text}")
        
except Exception as e:
    print(f"Error: {e}")
