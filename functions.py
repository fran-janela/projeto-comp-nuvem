import json
import os

def write_json(data):
    with open(f'tf-{data["region"]}/config/{data["region"]}.tfvars.json','w') as f:
        json.dump(data, f, indent=4)

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def all_tf_dirs():
    all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    tf_subdirs = []
    for subdir in all_subdirs:
        if subdir.split("-")[0] == "tf":
            tf_subdirs.append(subdir)
    return tf_subdirs

def all_created_regions_from_dir(tf_dirs):
    all_created_regions = []
    for tf_dir in tf_dirs:
        all_created_regions.append("-".join(tf_dir.split("-")[1:]))
    return all_created_regions

def get_region_from_dir(tf_dir):
    return "-".join(tf_dir.split("-")[1:])

def create_new_region_dir(region):
    os.system(f'cp -r sample/ tf-{region}/')

def tf_create_region(region):
    os.system(f'cd tf-{region} && terraform init')

def tf_apply_changes(region):
    os.system(f'cd tf-{region} && terraform apply -var-file="config/{region}.tfvars.json" -auto-approve')

def tf_destroy_region(region):
    os.system(f'cd tf-{region} && terraform destroy -var-file="config/{region}.tfvars.json" -auto-approve')

def remove_region_dir(region):
    os.system(f'rm -rf tf-{region}/')