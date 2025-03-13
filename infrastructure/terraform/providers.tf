terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    region = "eu-west-1"
    bucket = "ox-tfstates-dev-eu-west-1"
    key    = "eks-automation/terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      ox_use_case = var.ox_use_case
    }
  }
}
