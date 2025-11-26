terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # backend "s3" {
  #   bucket = "your-tfstate-bucket"
  #   key    = "chatbot/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

#------------------------------------------------------------------------------
# Scaffold of core resources (commented templates)
#------------------------------------------------------------------------------

# Networking (VPC, subnets, NAT)
# module "vpc" {
#   source  = "terraform-aws-modules/vpc/aws"
#   version = "~> 5.0"
#   name = "${var.project_name}-${var.environment}"
#   cidr = "10.0.0.0/16"
#   azs  = ["${var.aws_region}a", "${var.aws_region}b"]
#   private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
#   public_subnets  = ["10.0.11.0/24", "10.0.12.0/24"]
#   enable_nat_gateway = true
#   single_nat_gateway = true
#   tags = {
#     Project     = var.project_name
#     Environment = var.environment
#   }
# }

# RDS PostgreSQL (multi-AZ, encrypted)
# module "rds" {
#   source  = "terraform-aws-modules/rds/aws"
#   version = "~> 6.0"
#   identifier = "${var.project_name}-${var.environment}"
#   engine               = "postgres"
#   engine_version       = "15.5"
#   instance_class       = "db.t4g.medium"
#   allocated_storage    = 50
#   max_allocated_storage = 200
#   username             = var.db_username
#   password             = var.db_password
#   db_name              = var.db_name
#   multi_az             = true
#   storage_encrypted    = true
#   backup_retention_period = 7  # days
#   backup_window           = "03:00-04:00"
#   vpc_security_group_ids = [] # add SGs
#   subnet_ids           = module.vpc.private_subnets
#   publicly_accessible  = false
#   skip_final_snapshot  = false
#   tags = {
#     Project     = var.project_name
#     Environment = var.environment
#   }
# }

# ElastiCache Redis (cluster disabled)
# module "redis" {
#   source  = "terraform-aws-modules/elasticache/aws"
#   version = "~> 5.0"
#   engine         = "redis"
#   engine_version = "7.0"
#   node_type      = "cache.t4g.micro"
#   num_cache_nodes = 1
#   subnet_group_name = "${var.project_name}-${var.environment}-redis"
#   subnet_ids     = module.vpc.private_subnets
#   security_group_ids = [] # add SGs
#   tags = {
#     Project     = var.project_name
#     Environment = var.environment
#   }
# }

# S3 bucket for uploads / PDFs
# resource "aws_s3_bucket" "files" {
#   bucket = "${var.project_name}-${var.environment}-files"
#   acl    = "private"
#   tags = {
#     Project     = var.project_name
#     Environment = var.environment
#   }
#   server_side_encryption_configuration {
#     rule {
#       apply_server_side_encryption_by_default {
#         sse_algorithm = "AES256"
#       }
#     }
#   }
#   versioning {
#     enabled = true
#   }
#   lifecycle_rule {
#     id      = "pdf_retention"
#     enabled = true
#     filter  { prefix = "pdfs/" }
#     expiration { days = 180 }
#   }
#   lifecycle_rule {
#     id      = "temp_uploads"
#     enabled = true
#     filter  { prefix = "temp/" }
#     expiration { days = 30 }
#   }
#   lifecycle_rule {
#     id      = "logs_retention"
#     enabled = true
#     filter  { prefix = "logs/" }
#     expiration { days = 14 }
#   }
# }

# IAM roles for ECS tasks (API/workers)
# resource "aws_iam_role" "ecs_task_role" {
#   name = "${var.project_name}-${var.environment}-task"
#   assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume_role.json
#   tags = {
#     Project     = var.project_name
#     Environment = var.environment
#   }
# }
#
# data "aws_iam_policy_document" "ecs_tasks_assume_role" {
#   statement {
#     effect = "Allow"
#     principals {
#       type        = "Service"
#       identifiers = ["ecs-tasks.amazonaws.com"]
#     }
#     actions = ["sts:AssumeRole"]
#   }
# }
#
# resource "aws_iam_role_policy_attachment" "task_s3" {
#   role       = aws_iam_role.ecs_task_role.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
# }

# ECS/Fargate, ALB, ACM, and CloudFront would be added here referencing the VPC.

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "chatbot"
}

variable "environment" {
  description = "Environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  default     = "CHANGE_ME"
  sensitive   = true
}

variable "db_name" {
  description = "Default database name"
  type        = string
  default     = "chatbot"
}
