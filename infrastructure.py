from functions import *
class Infrastructure:
    def __init__(self, region, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        self.infrastructure = { 
            "provider": "aws", 
            "region": region,
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "network_configurations": {}, 
            "security_group_configurations": [],
            "instances_configuration": []}

        self.available_instnce_types = [
            "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "t2.xlarge", "t2.2xlarge",
            "t3.nano", "t3.micro", "t3.small", "t3.medium", "t3.large", "t3.xlarge", "t3.2xlarge"]

        self.ami_reference = {
            "us-east-1": "ami-00a0e0b890ae17d65",
            "us-east-2": "ami-0b4577d77dac11b84",
            "us-west-1": "ami-07ca31583160e0a93",
            "us-west-2": "ami-0cc5d32378afd3b57",
            "sa-east-1": "ami-084fadaa5d7882916",
            "eu-west-1": "ami-082bec92abb02aba4",
            "eu-west-2": "ami-0f0741503c767a317",
            "eu-west-3": "ami-03a5d4b9a3dba6ebe",
            "eu-central-1": "ami-0a474432ef48429a7",
            "ap-southeast-1": "ami-0ec559e18e8ed6466",
            "ap-southeast-2": "ami-0bb85ffded6e32670",
            "ap-northeast-1": "ami-04705b95f49850f5e",
            "ap-northeast-2": "ami-0cf362b88b0395b94",
            "ap-northeast-3": "ami-0cf362b88b0395b94",
            "ca-central-1": "ami-0191b23c592e9a01b",
            "cn-north-1": "ami-0764541358866f84e",
            "cn-northwest-1": "ami-02441dea73a15a612",  
            "us-gov-west-1": "ami-02642d561d662175f",
            "us-gov-east-1": "ami-01c308292da9fe7f5"
        }

        self.add_network()
        self.add_default_security_group()

    # Set infrastructure with a json file
    def set_infrastructure(self, json_file_name):
        self.infrastructure = read_json(json_file_name)

    # Get infrastructure
    def get_infrastructure(self):
        return self.infrastructure
    
    # ==============================================================================
    #                                    NETWORK
    # ==============================================================================
    # Add a default network configuration to the infrastructure
    def add_network(self):
        net_config = {
            "vpcCIDRblock": "10.0.0.0/16",
            "instanceTenancy": "default",
            "dnsSupport": True,
            "dnsHostNames": True,
            "publicsCIDRblock": "10.0.1.0/24",
            "mapPublicIP": True,
            "publicdestCIDRblock": "0.0.0.0/0"
        }
        self.infrastructure["network_configurations"] = net_config

    def add_default_security_group(self):
        default_sg = {
            "sg_name": "defaultSSH", 
            "sg_description": "Default Security Group for SSH",
            "ingress_ports": [{
                "id": 0,
                "description": "SSH",
                "from_port": 22,
                "to_port": 22,
                "protocol": "tcp",
                "cidr_blocks": ["0.0.0.0/0"]
            }],
            "egress_ports": [{
                "id": 0,
                "description": "All",
                "from_port": 0,
                "to_port": 0,
                "protocol": "-1",
                "cidr_blocks": ["0.0.0.0/0"]
            }]
        }
        self.infrastructure["security_group_configurations"].append(default_sg)

    # ==============================================================================
    #                               SECURITY GROUPS
    # ==============================================================================
    # Add a security group to the infrastructure
    def add_security_group(self, security_group):
        self.infrastructure["security_group_configurations"].append(security_group)

    def create_security_group(self, name, description):
        security_group = {
            "sg_name": name,
            "sg_description": description,
            "ingress_ports": [],
            "egress_ports": []
        }
        self.add_security_group(security_group)

    def delete_sec_group(self, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                del self.infrastructure["security_group_configurations"][index]
                break
                

    def add_ingress(self, ingress, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                self.infrastructure["security_group_configurations"][index]["ingress_ports"].append(ingress)
    

    def create_ingress_for_sg(self, description, protocol, from_port, to_port, cidr_blocks, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                break
        if len(self.infrastructure["security_group_configurations"][index]["ingress_ports"]) == 0:
            id = 0
        else:
            id = self.infrastructure["security_group_configurations"][index]["ingress_ports"][-1]["id"] + 1
        ingress = {
            "id": id,
            "description": description,
            "protocol": protocol,
            "from_port": int(from_port),
            "to_port": int(to_port),
            "cidr_blocks": cidr_blocks
        }
        self.add_ingress(ingress, security_group_name)

    def remove_ingress_rule_from_sg(self, id, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                for index2 in range(len(self.infrastructure["security_group_configurations"][index]["ingress_ports"])):
                    if self.infrastructure["security_group_configurations"][index]["ingress_ports"][index2]["id"] == id:
                        del self.infrastructure["security_group_configurations"][index]["ingress_ports"][index2]
                        break
                break

    def add_egress(self, egress, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                self.infrastructure["security_group_configurations"][index]["egress_ports"].append(egress)

    def create_egress_for_sg(self, description, protocol, from_port, to_port, cidr_blocks, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                break
        if len(self.infrastructure["security_group_configurations"][index]["egress_ports"]) == 0:
            id = 0
        else:
            id = self.infrastructure["security_group_configurations"][index]["egress_ports"][-1]["id"] + 1
        egress = {
            "id": id,
            "description": description,
            "protocol": protocol,
            "from_port": int(from_port),
            "to_port": int(to_port),
            "cidr_blocks": cidr_blocks
        }
        self.add_egress(egress, security_group_name)

    def remove_egress_rule_from_sg(self, id, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["sg_name"] == security_group_name:
                for index2 in range(len(self.infrastructure["security_group_configurations"][index]["egress_ports"])):
                    if self.infrastructure["security_group_configurations"][index]["egress_ports"][index2]["id"] == id:
                        del self.infrastructure["security_group_configurations"][index]["egress_ports"][index2]
                        break
                break


    # ==============================================================================
    #                                  INSTANCES
    # ==============================================================================
    # Add an instance to the infrastructure
    def add_instance(self, instance):
        self.infrastructure["instances_configuration"].append(instance)

    # Create instance for the infrastructure
    def create_instance(self, application_name, count, ami, instance_type, security_group_ids, key_name):
        instance = {
            "instance_name": application_name,
            "no_of_instances": count,
            "ami": ami,
            "instance_type": instance_type,
            "security_groups_ids": security_group_ids,
            "key_name": key_name
        }
        self.add_instance(instance)

    # Delete an instance from the infrastructure
    def delete_instance(self, instance_name):
        for index in range(len(self.infrastructure["instances_configuration"])):
            if self.infrastructure["instances_configuration"][index]["instance_name"] == instance_name:
                del self.infrastructure["instances_configuration"][index]

    def update_number_of_instances(self, instance_name, count):
        for index in range(len(self.infrastructure["instances_configuration"])):
            if self.infrastructure["instances_configuration"][index]["instance_name"] == instance_name:
                self.infrastructure["instances_configuration"][index]["no_of_instances"] = count

    def update_instance_security_groups(self, instance_name, security_group_ids):
        for index in range(len(self.infrastructure["instances_configuration"])):
            if self.infrastructure["instances_configuration"][index]["instance_name"] == instance_name:
                self.infrastructure["instances_configuration"][index]["security_groups_ids"] = security_group_ids