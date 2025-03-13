resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.ox_header}lambda${local.ox_footer}"
  retention_in_days = 7
}

resource "aws_iam_role" "lambda" {
  description = "Role for EKS Automation lambda function"
  name        = "${local.ox_header}lambda${local.ox_footer}"
  tags        = local.tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda" {
  name        = "${local.ox_header}lambda${local.ox_footer}"
  description = "Policy for EKS Automation lambda function"
  tags        = local.tags
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.ox_header}api${local.ox_footer}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeSubnets",
          "ec2:AssignPrivateIpAddresses",
          "ec2:UnassignPrivateIpAddresses",
          "ec2:DeleteNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ]
        Resource = "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*/*"
      },
      {
        Effect = "Allow",
        Action = [
          "ec2:DescribeNetworkInterfaces"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
        ]
        Resource = [
          "arn:aws:eks:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.kubernetes_cluster_name}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda.arn
}

resource "aws_eks_access_entry" "lambda" {
  cluster_name  = var.kubernetes_cluster_name
  principal_arn = aws_iam_role.lambda.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "lambda" {
  cluster_name  = var.kubernetes_cluster_name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  principal_arn = aws_iam_role.lambda.arn

  access_scope {
    type = "cluster"
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../.stimio/src/lambda"
  output_path = "${path.module}/../../.stimio/build/lambda.zip"
}

resource "aws_lambda_function" "lambda" {
  function_name = "${local.ox_header}lambda${local.ox_footer}"
  description   = "EKS automation"
  runtime       = "python3.12"
  handler       = "src.lambda_handler.handler"
  filename      = data.archive_file.lambda.output_path
  role          = aws_iam_role.lambda.arn
  timeout       = 30
  memory_size   = 1024
  tags          = local.tags

  source_code_hash               = data.archive_file.lambda.output_base64sha256

  environment {
    variables = {
      CLUSTER_NAME = var.kubernetes_cluster_name
    }
  }
}
