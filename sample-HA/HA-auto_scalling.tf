resource "aws_autoscaling_group" "web_service_asg" {
  count = var.create_HA_infrastructure ? 1 : 0
  name                 = "web-service"
  min_size             = 2
  max_size             = 5
  desired_capacity     = 2
  launch_configuration = aws_launch_configuration.web_service[count.index].name
  vpc_zone_identifier  = aws_subnet.Subnet_AutoScaling.*.id

  lifecycle { 
    ignore_changes = [desired_capacity, target_group_arns]
  }

  tag {
    key                 = "Name"
    value               = "HA-Instance-AutoScaling"
    propagate_at_launch = true
  }
}


resource "aws_autoscaling_attachment" "web_service_AutoScalling_attachment" {
  count = var.create_HA_infrastructure ? 1 : 0
  autoscaling_group_name = aws_autoscaling_group.web_service_asg[count.index].id
  lb_target_group_arn   = aws_lb_target_group.web_service_lb_tg[count.index].arn
}