resource "aws_autoscaling_policy" "scale_down" {
  count = var.create_HA_infrastructure ? 1 : 0
  name                   = "web_service_scale_down"
  autoscaling_group_name = aws_autoscaling_group.web_service_asg[count.index].name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = -1
  cooldown               = 120
}

resource "aws_cloudwatch_metric_alarm" "scale_down" {
  count = var.create_HA_infrastructure ? 1 : 0
  alarm_description   = "Monitors CPU utilization for web_service ASG"
  alarm_actions       = [aws_autoscaling_policy.scale_down[count.index].arn]
  alarm_name          = "web_service_scale_down"
  comparison_operator = "LessThanOrEqualToThreshold"
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  threshold           = "20"
  evaluation_periods  = "2"
  period              = "120"
  statistic           = "Average"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web_service_asg[count.index].name
  }
}

resource "aws_autoscaling_policy" "scale_up" {
  count = var.create_HA_infrastructure ? 1 : 0
  name                   = "web_service_scale_up"
  autoscaling_group_name = aws_autoscaling_group.web_service_asg[count.index].name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 120
}

resource "aws_cloudwatch_metric_alarm" "scale_up" {
  count = var.create_HA_infrastructure ? 1 : 0
  alarm_description   = "Monitors CPU utilization for web_service ASG"
  alarm_actions       = [aws_autoscaling_policy.scale_up[count.index].arn]
  alarm_name          = "web_service_scale_up"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  threshold           = "60"
  evaluation_periods  = "2"
  period              = "120"
  statistic           = "Average"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web_service_asg[count.index].name
  }
}