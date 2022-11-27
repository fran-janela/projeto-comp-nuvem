resource "aws_launch_configuration" "web_service" {
  count = var.create_HA_infrastructure ? 1 : 0
  name_prefix     = "webServer-Chico-AutoScalling-"
  image_id        = var.image_id
  instance_type   = "t2.micro"
  security_groups = [aws_security_group.web_service_AutoScalling_instance_sec_group[count.index].id]
  key_name        = var.key_name

  lifecycle {
    create_before_destroy = true
  }
}