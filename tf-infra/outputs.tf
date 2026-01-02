output "ecr_repository_url" {
  value = aws_ecr_repository.app_repo.repository_url
}

output "public_ip" {
  value = aws_instance.app_server.public_ip
}

output "s3_bucket_name" {
  value = aws_s3_bucket.app_bucket.id
}