data "aws_availability_zones" "available_zones" {
  state = "available"
}

resource "aws_subnet" "Subnet_AutoScaling" {
  count = 3
  vpc_id            = aws_vpc.VPC.id
  cidr_block        = ["172.16.11.0/24", "172.16.12.0/24", "172.16.13.0/24"][count.index]
  availability_zone = "${data.aws_availability_zones.available_zones.names[count.index]}"
  map_public_ip_on_launch = true

  tags = {
    Name = "Subnet_AutoScaling-proj-${count.index}"
  }
}

resource "aws_route_table_association" "Public_association_asg" {
    count = 3
    subnet_id      = aws_subnet.Subnet_AutoScaling[count.index].id
    route_table_id = aws_route_table.RT.id
}
