resource "aws_lb" "web_service_lb" {
  count = var.create_HA_infrastructure ? 1 : 0
  name               = "Webserver-Chico-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web_service_lb_sec_group[count.index].id]
  subnets            = aws_subnet.Subnet_AutoScaling.*.id
}

resource "aws_lb_listener" "web_service_lb_listener" {
  count = var.create_HA_infrastructure ? 1 : 0
  load_balancer_arn = aws_lb.web_service_lb[count.index].arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_service_lb_tg[count.index].arn
  }
}

resource "aws_lb_target_group" "web_service_lb_tg" {
  count = var.create_HA_infrastructure ? 1 : 0
  name     = "AutoScalling-WebService"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.VPC.id
}

output "lb_endpoint" {
  description = "URL of load balancer"
  value = [for lb in aws_lb.web_service_lb : lb.dns_name]
}