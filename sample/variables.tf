variable "region" {
  type = string
  default = "us-east-1"
}

variable "AWS_ACCESS_KEY_ID" {
  type = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  sensitive = true
}

variable "instances_configuration" {
  description = "The total configuration, List of Objects/Dictionary"
  type = list(object({
    no_of_instances = number
    instance_name = string
    instance_type    = string
    ami              = string
    security_groups_ids = list(string)
    key_name = string
  }))
}

variable "security_group_configurations" {
  description = "The total configuration, List of Objects/Dictionary"
  type = list(object({
    sg_name = string
    sg_description = string
    ingress_ports = list(object({
      id = number
      description = string
      from_port = number
      to_port = number
      protocol = string
      cidr_blocks = list(string)
    }))
    egress_ports = list(object({
      id = number
      description = string
      from_port = number
      to_port = number
      protocol = string
      cidr_blocks = list(string)
    }))
  }))
}

variable "network_configurations" {
  description = "The total configuration, List of Objects/Dictionary"
  type = object({
    vpcCIDRblock = string
    instanceTenancy = string
    dnsSupport = bool
    dnsHostNames = bool
    publicsCIDRblock = string
    mapPublicIP = bool
    publicdestCIDRblock = string
  })
}