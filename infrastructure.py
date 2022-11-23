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
            "instances_configuration": [],
            "user_configurations": []}

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
    #                                    USERS
    # ==============================================================================
    # Add a user to the infrastructure
    def add_user(self, user):
        self.infrastructure["user_configurations"].append(user)


    # ==============================================================================
    #                               SECURITY GROUPS
    # ==============================================================================
    # Add a security group to the infrastructure
    def add_security_group(self, security_group):
        self.infrastructure["security_group_configurations"].append(security_group)

    def create_security_group(self, name, description):
        security_group = {
            "name": name,
            "description": description
        }
        self.add_security_group(security_group)

    def add_ingress(self, ingress, security_group_name):
        for index in range(len(self.infrastructure["security_group_configurations"])):
            if self.infrastructure["security_group_configurations"][index]["name"] == security_group_name:
                self.infrastructure["security_group_configurations"][index]["ingress_ports"].append(ingress)
    

    def create_ingress_for_sg(self, description, protocol, from_port, to_port, cidr_ip, security_group_name):
        ingress = {
            "id": int(max(self.infrastructure["security_group_configurations"].filter(lambda x: x["name"] == security_group_name)["ingress_ports"]["id"]) + 1),
            "description": description,
            "protocol": protocol,
            "from_port": from_port,
            "to_port": to_port,
            "cidr_ip": cidr_ip
        }
        self.add_ingress(ingress, security_group_name)


    # ==============================================================================
    #                                  INSTANCES
    # ==============================================================================
    # Add an instance to the infrastructure
    def add_instance(self, instance):
        self.infrastructure["instances_configuration"].append(instance)

    # Create instance for the infrastructure
    def create_instance(self, application_name, ami, instance_type, security_group_ids, key_name):
        instance = {
            "instance_name": application_name,
            "ami": ami,
            "instance_type": instance_type,
            "security_groups_ids": security_group_ids,
            "key_name": key_name
        }
        self.add_instance(instance)