resource "aws_security_group" "sg" {
  for_each = {for sg in var.security_group_configurations: sg.sg_name => sg}
  name        = each.value.sg_name
  description = each.value.sg_description
  vpc_id      = aws_vpc.VPC.id

  dynamic "ingress" {
    for_each = each.value.ingress_ports
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
  dynamic "egress" {
    for_each = each.value.egress_ports
    content {
      description = egress.value.description
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }

  tags = {
    Name = each.value.sg_name
  }
}

output "security_groups" {
  value       = [for sg in aws_security_group.sg : sg]
  description = "All Security Group details"
}