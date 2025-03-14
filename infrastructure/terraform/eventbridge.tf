resource "aws_iam_role" "scheduler" {
  description = "Role for EventBridge scheduler."
  name        = "${local.ox_header}scheduler${local.ox_footer}"
  tags        = local.tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = "351370433122"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  name = "${local.ox_header}scheduler${local.ox_footer}"
  role = aws_iam_role.scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          "${aws_lambda_function.lambda.arn}:*",
          aws_lambda_function.lambda.arn
        ]
      },
    ]
  })
}

resource "aws_scheduler_schedule" "scale_down" {
  name       = "${local.ox_header}scale-down${local.ox_footer}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 21 ? * 2,3,4,5,6 *)"

  target {
    arn      = aws_lambda_function.lambda.arn
    role_arn = aws_iam_role.scheduler.arn
    input = jsonencode(
      {
        scaling_mode = "down"
      }
    )
  }
}


resource "aws_scheduler_schedule" "scale_up" {
  name       = "${local.ox_header}scale-up${local.ox_footer}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 7 ? * 2,3,4,5,6 *)"

  target {
    arn      = aws_lambda_function.lambda.arn
    role_arn = aws_iam_role.scheduler.arn
    input = jsonencode(
      {
        scaling_mode = "up"
      }
    )
  }
}
