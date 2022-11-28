import json
import os

def clear_console():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def write_json(data):
    with open(f'tf-{data["region"]}/config/{data["region"]}.tfvars.json','w') as f:
        json.dump(data, f, indent=4)

def write_iam_json(data):
    with open(f'iam/config/iam.tfvars.json','w') as f:
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

def create_iam_config_folder():
    os.system(f'cd iam && mkdir config &> /dev/null')
    os.system(f'cd iam/config && touch iam.tfvars.json &> /dev/null')

def create_new_region_dir(region):
    os.system(f'cp -r sample/ tf-{region}/ &> /dev/null')
    os.system(f'cd tf-{region} && mkdir config &> /dev/null')
    os.system(f'cd tf-{region}/config && touch {region}.tfvars.json &> /dev/null')

def tf_create_region(region):
    os.system(f'cd tf-{region} && terraform init &> /dev/null')

def tf_apply_changes(region):
    os.system(f'cd tf-{region} && terraform apply -var-file="config/{region}.tfvars.json" -auto-approve &> /dev/null')

def tf_destroy_region(region):
    os.system(f'cd tf-{region} && terraform destroy -var-file="config/{region}.tfvars.json" -auto-approve &> /dev/null')

def destroy_iam_infrastructure():
    os.system(f'cd iam && terraform destroy -var-file="config/iam.tfvars.json" -auto-approve &> /dev/null')

def remove_iam_config_file():
    os.system(f'cd iam/ && rm -rf config/ &> /dev/null')

def remove_region_dir(region):
    os.system(f'rm -rf tf-{region}/ &> /dev/null')

def read_tfstate_outputs(region):
    with open(f'tf-{region}/terraform.tfstate') as f:
        data = json.load(f)
    return data["outputs"]

def get_sec_groups(region):
    outputs = read_tfstate_outputs(region)
    sec_groups_names = []
    sec_groups_ids = []
    for sec_group in outputs["security_groups"]["value"]:
        sec_groups_names.append(f'{sec_group["name"]} - {sec_group["description"]}')
        sec_groups_ids.append(sec_group["id"])
    return sec_groups_names, sec_groups_ids

def get_sec_groups_to_list(region):
    outputs = read_tfstate_outputs(region)
    configurated_sec_groups = {}
    for sec_group in outputs["security_groups"]["value"]:
        configurated_sec_groups[sec_group["name"]] = {
            "id": sec_group["id"],
            "description": sec_group["description"],
            "ingress": sec_group["ingress"],
            "egress": sec_group["egress"],
            "owner_id": sec_group["owner_id"],
            "vpc_id": sec_group["vpc_id"]
        }
    return configurated_sec_groups

def get_instances(region):
    outputs = read_tfstate_outputs(region)
    configurated_instances = {}
    for instance in outputs["instances"]["value"]:
        configurated_instances[instance["tags"]["Name"]] = {
            "id": instance["id"],
            "instance_type": instance["instance_type"],
            "instance_state": instance["instance_state"],
            "public_ip": instance["public_ip"],
            "public_dns": instance["public_dns"],
            "key_name": instance["key_name"],
            "security_groups": instance["vpc_security_group_ids"]
        }
    return configurated_instances

def get_sec_groups_in_use(region):
    outputs = read_tfstate_outputs(region)
    sec_groups_in_use = []
    for instance in outputs["instances"]["value"]:
        sec_groups_in_use.extend(instance["vpc_security_group_ids"])
    return sec_groups_in_use

def tf_iam_apply_changes():
    os.system(f'cd iam && terraform apply -var-file="config/iam.tfvars.json" -auto-approve &> /dev/null')

def get_user_password(username):
    with open(f'iam/terraform.tfstate') as f:
        data = json.load(f)
    outputs = data["outputs"]
    return outputs["created_users"]["value"][username]

def json_policy_to_infra(policy, policy_name):
    statements = []
    for index in range(len(policy["Statement"])):
        file_actions = policy["Statement"][index]["Action"]
        if type(file_actions) == list:
            actions = file_actions
        else:
            actions = [file_actions]
        file_resources = policy["Statement"][index]["Resource"]
        if type(file_resources) == list:
            resources = file_resources
        else:
            resources = [file_resources]
        conditions = []
        if "Condition" in policy["Statement"][index].keys():
            for test in policy["Statement"][index]["Condition"].keys():
                for variable in policy["Statement"][index]["Condition"][test].keys():
                    if type(policy["Statement"][index]["Condition"][test][variable]) == list:
                        values = policy["Statement"][index]["Condition"][test][variable]
                    else:
                        values = [policy["Statement"][index]["Condition"][test][variable]]
                    conditions.append({"test": test, "variable": variable, "values": values})
        statements.append({"restriction_name":f"{policy_name}-{index}", "actions": actions, "resources": resources, "conditions": conditions})
    return statements

def get_all_instances_config():
    all_regions = all_created_regions_from_dir(all_tf_dirs())
    all_instances = {}
    for region in all_regions:
        all_instances[region] = get_instances(region)
    all_instances_config = []
    for region in all_instances.keys():
        for instance in all_instances[region].keys():
            all_instances_config.append({
                "name": instance,
                "region": region,
                "instance_type": all_instances[region][instance]["instance_type"],
                "instance_state": all_instances[region][instance]["instance_state"],
                "public_ip": all_instances[region][instance]["public_ip"],
                "public_dns": all_instances[region][instance]["public_dns"],
                "key_name": all_instances[region][instance]["key_name"],
                "security_groups": all_instances[region][instance]["security_groups"]
            })
    return all_instances_config

def copy_files_from_dir_to_dir(dir_to):
    os.system(f'cp -r "sample-HA/" {dir_to}')

def remove_HA_configurations(region):
    # all files in tf-us-east-1:
    all_files = [f for f in os.listdir(f'tf-{region}/') if os.path.isfile(os.path.join(f'tf-{region}/', f))]
    # delete HA files:
    for file in all_files:
        if file.split("-")[0] == "HA":
            os.system(f'rm -rf tf-{region}/{file}')

def get_lb_url(region):
    outputs = read_tfstate_outputs(region)
    return outputs["lb_endpoint"]["value"][0]