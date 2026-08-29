terraform {
  backend "s3" {
    bucket       = "varshith-devops-terraform-state-2026"
    key          = "dev/terraform.tfstate"
    region       = "us-east-2"
    profile      = "root-login"
    encrypt      = true
    use_lockfile = true
  }
}