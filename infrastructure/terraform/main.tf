data "aws_caller_identity" "current" {}

resource "aws_servicecatalogappregistry_application" "scaling_app" {
  name        = "${local.ox_header}app${local.ox_footer}"
  description = "Automate dev EKS scaling"
}
