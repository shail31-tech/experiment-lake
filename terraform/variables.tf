variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "experimentlake"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}
