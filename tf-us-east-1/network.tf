resource "aws_vpc" "VPC" {
    cidr_block           = var.network_configurations.vpcCIDRblock
    instance_tenancy     = var.network_configurations.instanceTenancy 
    enable_dns_support   = var.network_configurations.dnsSupport 
    enable_dns_hostnames = var.network_configurations.dnsHostNames
    tags = {
        Name = "VPC"
    }
} 

resource "aws_subnet" "Subnet" {
    vpc_id                  = aws_vpc.VPC.id
    cidr_block              = var.network_configurations.publicsCIDRblock
    map_public_ip_on_launch = var.network_configurations.mapPublicIP
    tags = {
        Name = "Subnet"
    }
}

resource "aws_internet_gateway" "IGW" {
    vpc_id = aws_vpc.VPC.id
    tags = {
        Name = "Internet gateway teste"
    }
} 

resource "aws_route_table" "RT" {
    vpc_id = aws_vpc.VPC.id
    tags = {
        Name = "Public Route table"
    }
}

resource "aws_route" "internet_access" {
    route_table_id         = aws_route_table.RT.id
    destination_cidr_block = var.network_configurations.publicdestCIDRblock
    gateway_id             = aws_internet_gateway.IGW.id
}

resource "aws_route_table_association" "Public_association" {
    subnet_id      = aws_subnet.Subnet.id
    route_table_id = aws_route_table.RT.id
}