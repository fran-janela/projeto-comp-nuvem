from functions import *
import os

class IAM_Infrastructure:
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        self.IAM_infra = { 
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "policies_configurations": [], 
            "users_configurations": [],
            "user_policy_attachments": []}

        self.load_policies_from_folder()

    def set_infrastructure(self, json_file_name):
        self.IAM_infra = read_json(json_file_name)

    def clear_infrastructure(self):
        AWS_ACCESS_KEY_ID = self.IAM_infra["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = self.IAM_infra["AWS_SECRET_ACCESS_KEY"]
        self.IAM_infra = {
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "policies_configurations": [],
            "users_configurations": [],
            "user_policy_attachments": []}
        destroy_iam_infrastructure()
        remove_iam_config_file()

    # ==============================================================================
    #                                    POLICYS
    # ==============================================================================
    def add_policy(self, policy):
        self.IAM_infra["policies_configurations"].append(policy)

    def load_policies_from_folder(self):
        # read all json files from iam/policies/ folder:
        # get all file names from folder
        files = [f for f in os.listdir("iam/policies/") if os.path.isfile(os.path.join("iam/policies/", f))]
        policies = []
        for file in files:
            data = read_json("iam/policies/" + file)
            policy_name = file.split(".")[0]
            statements = []
            for index in range(len(data["Statement"])):
                file_actions = data["Statement"][index]["Action"]
                if type(file_actions) == list:
                    actions = file_actions
                else:
                    actions = [file_actions]
                file_resources = data["Statement"][index]["Resource"]
                if type(file_resources) == list:
                    resources = file_resources
                else:
                    resources = [file_resources]
                conditions = []
                if "Condition" in data["Statement"][index].keys():
                    for test in data["Statement"][index]["Condition"].keys():
                        for variable in data["Statement"][index]["Condition"][test].keys():
                            if type(data["Statement"][index]["Condition"][test][variable]) == list:
                                values = data["Statement"][index]["Condition"][test][variable]
                            else:
                                values = [data["Statement"][index]["Condition"][test][variable]]
                            conditions.append({"test": test, "variable": variable, "values": values})
                statements.append({"restriction_name":f"{policy_name}-{index}", "actions": actions, "resources": resources, "conditions": conditions})
            policies.append({"name": policy_name, "statements": statements})
        created_policies_names = [ policy["name"] for policy in self.IAM_infra["policies_configurations"]]
        for policy in policies:
            if policy["name"] not in created_policies_names:
                self.add_policy(policy)

    
    def create_policy(self, policy_name, actions, resources):
        self.add_policy({
            "name": policy_name,
            "restriction": {
                "restriction_name": policy_name,
                "actions": actions,
                "resources": resources,
            }
        })

    # ==============================================================================
    #                                    USERS
    # ==============================================================================
    def create_user(self, username):
        self.IAM_infra["users_configurations"].append({"username": username})
    
    def delete_user(self, username):
        for i in range(len(self.IAM_infra["users_configurations"])):
            if self.IAM_infra["users_configurations"][i]["username"] == username:
                del self.IAM_infra["users_configurations"][i]
                break
        reloaded_user_policy_attachments = []
        for j in range(len(self.IAM_infra["user_policy_attachments"])):
            if self.IAM_infra["user_policy_attachments"][j]["username"] != username:
                reloaded_user_policy_attachments.append(self.IAM_infra["user_policy_attachments"][j])
        self.IAM_infra["user_policy_attachments"] = reloaded_user_policy_attachments
                

    # ==============================================================================
    #                             POLICYS ATTACHMENTS
    # ==============================================================================
    def attach_policy(self, username, policy_name):
        used_keys = [attached["key"] for attached in self.IAM_infra["user_policy_attachments"]]
        new_key = int(max(used_keys)) + 1 if len(used_keys) > 0 else 0
        self.IAM_infra["user_policy_attachments"].append({"key": new_key, "username": username, "policy_name": policy_name})

    def detach_policy(self, username, policy_name):
        for i in range(len(self.IAM_infra["user_policy_attachments"])):
            if self.IAM_infra["user_policy_attachments"][i]["username"] == username and self.IAM_infra["user_policy_attachments"][i]["policy_name"] == policy_name:
                del self.IAM_infra["user_policy_attachments"][i]
                break

        