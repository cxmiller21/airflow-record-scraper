terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket = "terraform-remote-state-2211"
    key    = "apache/airflow"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}
