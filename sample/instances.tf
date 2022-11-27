locals {
  serverconfig = [
    for srv in var.instances_configuration : [
      for i in range(1, srv.no_of_instances+1) : {
        instance_name = "${srv.instance_name}-${i}"
        instance_type = srv.instance_type
        ami = srv.ami
        security_groups_ids = srv.security_groups_ids
        key_name = srv.key_name
      }
    ]
  ]
}
// We need to Flatten it before using it
locals {
  instances = flatten(local.serverconfig)
}

resource "aws_instance" "web" {
  for_each = {for server in local.instances: server.instance_name =>  server}
  ami           = each.value.ami
  instance_type = each.value.instance_type
  subnet_id = aws_subnet.Subnet.id
  vpc_security_group_ids = each.value.security_groups_ids
  key_name = each.value.key_name
  
  tags = {
    Name = "${each.value.instance_name}"
  }
}

output "instances" {
  value       = [for instance in aws_instance.web : instance]
  description = "All Machine details"
}