locals {
  # Lowercase variables
  ox_environment = lower(var.ox_environment)
  ox_use_case    = lower(var.ox_use_case)
  ox_version     = var.ox_version != null ? lower(var.ox_version) : null
  ox_reason      = var.ox_reason != null ? lower(var.ox_reason) : null
  ox_developer   = var.ox_developer != null ? lower(var.ox_developer) : null
  ox_customer    = var.ox_customer != null ? lower(var.ox_customer) : null

  # Compute the header depending on the environment and available variables
  ox_header = (local.ox_environment == "prod") ? (local.ox_customer != null) ? (local.ox_version != null) ? "ox-${local.ox_use_case}-${local.ox_customer}-${local.ox_version}-" : "ox-${local.ox_use_case}-${local.ox_customer}-" : (local.ox_version != null) ? "ox-${local.ox_use_case}-${local.ox_version}-" : "ox-${local.ox_use_case}-" : "ox-${local.ox_use_case}-"

  # Compute the footer depending on the environment and available variables
  ox_footer = (local.ox_environment == "prod") ? "" : (local.ox_environment == "staging") ? (local.ox_reason != null) ? "-staging-${local.ox_reason}" : "-staging" : (local.ox_developer != null) ? "-dev-${local.ox_developer}" : "-dev"

  tags = merge(
    aws_servicecatalogappregistry_application.scaling_app.application_tag,
    {
      "ox_use_case" = local.ox_use_case
    }
  )
}
