resource "aws_security_group" "web_service_AutoScalling_instance_sec_group" {
  count = var.create_HA_infrastructure ? 1 : 0
  name = "HA-instance-sg"
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web_service_lb_sec_group[count.index].id]
  }

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.web_service_lb_sec_group[count.index].id]
  }

  vpc_id = aws_vpc.VPC.id
}

resource "aws_security_group" "web_service_lb_sec_group" {
  count = var.create_HA_infrastructure ? 1 : 0
  name = "HA-lb-sg"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  vpc_id = aws_vpc.VPC.id
}