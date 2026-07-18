variable "aws_region" {
  description = "AWS region for the dev environment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name."
  type        = string
  default     = "experimentlake"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}
