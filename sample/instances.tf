resource "aws_instance" "web" {
  for_each = {for instance in var.instances_configuration: instance.instance_name => instance}
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