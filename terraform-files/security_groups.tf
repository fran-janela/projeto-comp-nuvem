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

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = each.value.sg_name
  }
}

output "security_groups" {
  value       = [for sg in aws_security_group.sg : sg]
  description = "All Security Group details"
}