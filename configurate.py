import json

def write_json(data):
    with open(f'{data["region"]}.tfvars.json','w') as f:
        json.dump(data, f, indent=4)