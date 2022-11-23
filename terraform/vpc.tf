################################################################
# VPC Resources us-east-1
################################################################
data "aws_availability_zones" "azs" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.192.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    "Name" = "mwaa-main-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    "Name" = "mwaa-main-igw"
  }
}

resource "aws_internet_gateway_attachment" "main" {
  internet_gateway_id = aws_internet_gateway.main.id
  vpc_id              = aws_vpc.main.id
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.192.10.0/24"
  map_public_ip_on_launch = true
  availability_zone       = element(data.aws_availability_zones.azs.names, 0)

  tags = {
    "Name" = "public-subnet-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.192.11.0/24"
  map_public_ip_on_launch = true
  availability_zone       = element(data.aws_availability_zones.azs.names, 1)

  tags = {
    "Name" = "public-subnet-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.192.20.0/24"
  map_public_ip_on_launch = false
  availability_zone       = element(data.aws_availability_zones.azs.names, 0)

  tags = {
    "Name" = "private-subnet-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.192.21.0/24"
  map_public_ip_on_launch = false
  availability_zone       = element(data.aws_availability_zones.azs.names, 1)

  tags = {
    "Name" = "private-subnet-2"
  }
}

resource "aws_eip" "public_1" {
  vpc        = true
  depends_on = [aws_internet_gateway_attachment.main]
}

resource "aws_eip" "public_2" {
  vpc        = true
  depends_on = [aws_internet_gateway_attachment.main]
}

resource "aws_nat_gateway" "public_1" {
  subnet_id  = aws_subnet.public_1.id
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "public_2" {
  subnet_id  = aws_subnet.public_2.id
  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  lifecycle {
    ignore_changes = all
  }

  tags = {
    "Name" = "Main-Region-RT-Airflow-Public"
  }
}

resource "aws_main_route_table_association" "public" {
  vpc_id         = aws_vpc.main.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private_1" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.public_1.id
  }

  lifecycle {
    ignore_changes = all
  }

  tags = {
    "Name" = "Main-Region-RT-Airflow-Private"
  }
}

resource "aws_main_route_table_association" "private_1" {
  vpc_id         = aws_vpc.main.id
  route_table_id = aws_route_table.private_1.id
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private_1.id
}

resource "aws_route_table" "private_2" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.public_2.id
  }

  lifecycle {
    ignore_changes = all
  }

  tags = {
    "Name" = "Main-Region-RT-Airflow-Private-2"
  }
}

resource "aws_main_route_table_association" "private_2" {
  vpc_id         = aws_vpc.main.id
  route_table_id = aws_route_table.private_1.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private_2.id
}
