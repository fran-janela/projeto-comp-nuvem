locals {
  serverconfig = [
    for srv in var.configuration : [{
        instance_name = "${srv.application_name}"
        instance_type = srv.instance_type
        ami = srv.ami
      }
    ]
  ]
}

// We need to Flatten it before using it
locals {
  instances = flatten(local.serverconfig)
}

resource "aws_instance" "web" {

  for_each = {for server in local.instances: server.instance_name => server}
  
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