import json,os

def read_listings( filepath="listings.json"):
    if not os.path.exists(filepath):
        return []
    else:
        with open(filepath,"r") as f:
            data = json.load(f)
            return data

def write_listings(listing, filepath="listings.json"):
    with open(filepath,"w") as response:
        json.dump(listing,response,indent = 4)