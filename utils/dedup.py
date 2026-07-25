import json,os

def is_duplicate(listing, filepath="listings.json"):
    #check if the file exists
    if not os.path.exists(filepath):
        return False

    else:
        with open(filepath,"r") as f:
            data = json.load(f)

    existing_hash = set()
    for item in data:
        existing_hash.add(item["hash"])
    
    return listing.hash in existing_hash
    
    
        
