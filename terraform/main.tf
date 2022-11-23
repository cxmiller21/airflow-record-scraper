resource "aws_s3_bucket" "airflow" {
  bucket = "cm-apache-airflow-bucket"

  tags = {
    Name        = "cm-apache-airflow-bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "airflow" {
  bucket = aws_s3_bucket.airflow.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "airflow" {
  bucket = aws_s3_bucket.airflow.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_mwaa_environment" "airflow" {
  airflow_configuration_options = {
    "core.default_task_retries" = 3
    "core.parallelism"          = 1
  }

  environment_class = "mw1.small"

  dag_s3_path           = "dags/"
  execution_role_arn    = aws_iam_role.airflow.arn
  name                  = "apache-airflow-project"
  webserver_access_mode = "PUBLIC_ONLY"
  max_workers           = 2

  network_configuration {
    security_group_ids = [aws_security_group.airflow.id]
    subnet_ids = [
      aws_subnet.private_1.id,
      aws_subnet.private_2.id
    ]
  }

  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }
    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }
    task_logs {
      enabled   = true
      log_level = "INFO"
    }
    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }
    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  source_bucket_arn = aws_s3_bucket.airflow.arn
}
