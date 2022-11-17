class Infrastructure:
    def __init__(self, region, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        self.infrastructure = { 
            "provider": "aws", 
            "region": region,
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "network_configurations": {}, 
            "user_configurations": [],
            "security_group_configurations": [],
            "instances_configurations": []}

        self.add_network()
    
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
        self.infrastructure["instances_configurations"].append(instance)

    # Create instance for the infrastructure
    def create_instance(self, application_name, ami, instance_type, subnet_id, security_group_ids):
        instance = {
            "application_name": application_name,
            "ami": ami,
            "instance_type": instance_type,
            "subnet_id": subnet_id,
            "vpc_security_group_ids": security_group_ids
        }
        self.add_instance(instance)