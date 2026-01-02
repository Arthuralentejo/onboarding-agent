variable "aws_region" {
  default = "us-east-1" # Região com mais serviços free tier
}

variable "project_name" {
  default = "gs2025"
}

# Você deve passar essas vars na hora do apply ou via arquivo .tfvars
variable "mongodb_connection_string" {
  description = "Connection string do MongoDB Atlas"
  sensitive   = true
}

variable "google_api_key" {
  description = "Chave de API do Google Gemini"
  sensitive   = true
}

variable "tavily_api_key" {
  description = "Chave de API do Tavily"
  sensitive   = true
}

variable "my_public_key" {
  description = "Chave pública SSH para acessar a instância EC2"
}

variable "log_collection_name" {
  default = "Collection para logs"
}

variable "database_name" {
  default = "Nome do banco de dados"
}

variable "collection_name" {
  default = "Nome da coleção"
}


