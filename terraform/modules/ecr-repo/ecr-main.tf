
resource "aws_ecr_repository" "lambda_repo" {
  name = var.repo_name

  tags = var.default_tags

  force_delete         = true
}

resource "docker_build" "lambda_build" {
  name = "order-analytics-image"
  path = "."
}

resource "aws_ecr_image" "lambda_build" {
  repository_name = aws_ecr_repository.lambda_repo.name
  image_tag       = "latest"
  image           = docker_build.lambda_build.name
}