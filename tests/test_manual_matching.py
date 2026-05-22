
def test_matching_logic():
    print("Testing Auto-Match Logic...")
    
    drills = {
        "d1": "Passing Triangle",
        "d2": "3v2 Shooting Drill",
        "d3": "Rondo 4v1",
        "d4": "Warmup Jog"
    }
    
    test_files = [
        ("passing-triangle.png", "d1"),
        ("3v2 shooting.jpg", "d2"),
        ("rondo-4v1-session.png", "d3"),
        ("random-image.jpg", None),
        ("warmup.png", "d4") # Partial match test
    ]
    
    passes = 0
    for fname, expected_id in test_files:
        raw_name = fname.split('.')[0].lower().replace("_", " ").replace("-", " ")
        
        match_id = None
        for did, dname in drills.items():
            dname_clean = dname.lower()
            # Logic from code:
            if raw_name in dname_clean or dname_clean in raw_name:
                match_id = did
                break
        
        # Exception for warmup which might match multiple or partial, but here matches "Warmup Jog" via "warmup" in "warmup jog"
        
        if match_id == expected_id:
            print(f"✅ PASS: '{fname}' matched to '{drills.get(match_id)}'")
            passes += 1
        else:
            print(f"❌ FAIL: '{fname}' matched to '{drills.get(match_id)}' (Expected: {expected_id})")
            
    print(f"Result: {passes}/{len(test_files)} passed")

if __name__ == "__main__":
    test_matching_logic()
