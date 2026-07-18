variable "name_prefix" {
  description = "Prefix used for resource names."
  type        = string
}

variable "account_id" {
  description = "AWS account ID used to make bucket names globally unique."
  type        = string
}

variable "aws_region" {
  description = "AWS region used to make bucket names globally unique."
  type        = string
}