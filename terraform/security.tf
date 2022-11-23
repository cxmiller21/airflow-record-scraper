data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

# resource "aws_security_group" "alb" {
#   name        = "main-lb-sg-airflow"
#   description = "Allow 443 and traffic to airflow SG"
#   vpc_id      = aws_vpc.main.id

#   ingress {
#     description = "Allow 443 from anywhere"
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   ingress {
#     description = "Allow 80 from anywhere for redirects"
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

resource "aws_security_group" "airflow" {
  name        = "main-sg-airflow"
  description = "Allow TCP/8443 & TPC/22"
  vpc_id      = aws_vpc.main.id

  # Temp
  # allow all traffic from my IP
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = -1
    self      = true
  }

  #   ingress {
  #     description = "Allow 22 from local IP"
  #     from_port   = 22
  #     to_port     = 22
  #     protocol    = "tcp"
  #     cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  #   }

  #   ingress {
  #     description = "Allow 80 from local IP"
  #     from_port   = 80
  #     to_port     = 80
  #     protocol    = "tcp"
  #     cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  #   }

  #   ingress {
  #     description = "Allow 5432 from local IP"
  #     from_port   = 5432
  #     to_port     = 5432
  #     protocol    = "tcp"
  #     cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  #   }

  #   ingress {
  #     description = "Allow 8443 from local IP"
  #     from_port   = 8443
  #     to_port     = 8443
  #     protocol    = "tcp"
  #     cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  #   }

  # ingress {
  #   description     = "Allow 8080 to airflow api from local IP"
  #   from_port       = 8080
  #   to_port         = 8080
  #   protocol        = "tcp"
  #   cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  # }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
