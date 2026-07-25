import json,os
from urllib.request import urlopen

#json string
json_data = '''
{
    "people": [
        {
            "name": "Fatima",
            "Age": 23,
            "phone_no": "03121234567",
            "liscense": false
        },
        {
            "name": "Faiqa",
            "Age": 22,
            "phone_no": "03121289767",
            "liscense": false
        }
    ]
}
'''
#json.loads: str -> python dict
python_obj = json.loads(json_data)
print(python_obj)
#checks the data type
print(type(python_obj))
print(type(python_obj["people"]))

#json.dumps: python dict -> str
json_str = json.dumps(python_obj)
print(json_str)
#check the data type
print(type(json_str))


#read JSON into Python
with open("test.json","r") as f:
    data = json.load(f)
print(data)
print(type(data))

#to access specific values
print(data ["employees"][0]["name"])

#modifies salary
data["employees"][1]["salary"] = 70000



# Write updated dictionary back to the JSON file
with open("test.json", "w") as f:
    json.dump(data, f, indent=4) 
#in order to check whether the file/folder exits
if os.path.exists("test.json"):
    with open("test.json","r") as f:
        data = json.load(f)
    print(data)
    print(type(data))
    #to access specific values
    print(data ["employees"][0]["name"])
    #modifies salary
    data["employees"][1]["salary"] = 40000 
    # Write updated dictionary back to the JSON file
    with open("test.json", "w") as f:
        json.dump(data, f, indent=4)
    
else:
    data = []
    print("ERROR, The file doesnt exists.")

#working with API
with urlopen("https://api.github.com") as response:
    source = response.read().decode("utf-8")
    print(type(source))

    data = json.loads(source)
    print(json.dumps(data,indent=2))
