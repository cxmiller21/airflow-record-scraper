# resource "aws_lb" "main" {
#   name               = "main-lb-airflow"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.alb.id]
#   subnets            = [aws_subnet.public_1.id]
#   tags = {
#     Name = "airflow-LB"
#   }
# }

# resource "aws_lb_target_group" "main_tg" {
#   name        = "app-lb-tg"
#   port        = 8080
#   target_type = "instance"
#   vpc_id      = aws_vpc.main.id
#   protocol    = "HTTP"

#   health_check {
#     enabled  = true
#     interval = 10
#     path     = "/airflow"
#     port     = 8080
#     protocol = "HTTP"
#     matcher  = "200-299"
#   }

#   tags = {
#     Name = "airflow-target-group"
#   }
# }

# resource "aws_lb_listener" "http" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = "80"
#   protocol          = "HTTP"
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.main_tg.arn
#   }
# }

# resource "aws_lb_target_group_attachment" "airflow_main" {
#   target_group_arn = aws_lb_target_group.main_tg.arn
#   target_id        = aws_instance.airflow.id
#   port             = 8080
# }
