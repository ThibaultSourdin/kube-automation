# ==============================================================================
# Oxygen project variables
# ==============================================================================
variable "ox_environment" {
  description = "Name of the AWS environment, typically prod, staging or dev."
  default     = "dev"
}

variable "ox_use_case" {
  description = "Name of the use case, typically the name of the service or application (e.g. bus-monitoring)."
  default     = "eks-automation"
}

variable "ox_version" {
  description = "Version of the use case, typically the version of the service or application (e.g. v1, used to tag resources in production)."
  default     = "v1"
}

variable "ox_reason" {
  description = "Optional reason for the deployment of the resources (used to tag resources in staging)."
  default     = null
}

variable "ox_developer" {
  description = "Optional name of the developer who deployed the resources (used to tag resources in dev)."
  default     = null
}

variable "ox_customer" {
  description = "Optional name of the customer for whom the resources are deployed (used to tag resources in production)."
  default     = null
}

# ==============================================================================
# AWS variables
# ==============================================================================
variable "aws_region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "eu-west-1"
}

variable "vpc_name" {
  description = "Name of the VPC (needed for connecting to RDS)"
  type        = string
  default     = "ox-infra-vpc-dev"
}

variable "ecr_mutation_enabled" {
  description = "Enable the mutation of the image tags in the ECR registries"
  type        = bool
  default     = true
}

variable "ecr_scan_on_push" {
  description = "Scan the image when pushed to the repository"
  type        = bool
  default     = false
}

variable "ecr_force_delete" {
  description = "Force the deletion of the ECR repository"
  type        = bool
  default     = false
}

variable "secret_recovery_window_in_days" {
  description = "Number of days to keep the secret in the recovery window"
  type        = number
  default     = 30
}

variable "artifact_bucket" {
  description = "S3 bucket to store artifacts."
  type        = string
  default     = "ox-artifacts-dev-eu-west-1"
}

# ==============================================================================
# Kubernetes variables
# ==============================================================================
variable "kubernetes_cluster_name" {
  description = "Name of the Kubernetes cluster"
  default     = "ox-eks-dev"
}

variable "kubernetes_namespace" {
  description = "Namespace where the Isolation Measure application is deployed"
  default     = "default"
}
