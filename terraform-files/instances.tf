resource "aws_instance" "web" {

  for_each = {for instance in var.instances_configuration: instance.instance_name => instance}
  
  ami           = each.value.ami
  instance_type = each.value.instance_type
  tags = {
    Name = "${each.value.instance_name}"
  }
}

output "instances" {
  value       = "${aws_instance.web}"
  description = "All Machine details"
}