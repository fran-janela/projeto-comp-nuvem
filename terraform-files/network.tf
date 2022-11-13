resource "aws_vpc" "VPC_teste" {
    cidr_block           = var.vpcCIDRblock
    instance_tenancy     = var.instanceTenancy 
    enable_dns_support   = var.dnsSupport 
    enable_dns_hostnames = var.dnsHostNames
    tags = {
        Name = "VPC teste"
    }
} 

resource "aws_subnet" "Public_subnet" {
    vpc_id                  = aws_vpc.VPC_teste.id
    cidr_block              = var.publicsCIDRblock
    map_public_ip_on_launch = var.mapPublicIP 
    availability_zone       = var.availabilityZone
    tags = {
        Name = "Public subnet"
    }
}