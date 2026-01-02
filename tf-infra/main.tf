provider "aws" {
  region = var.aws_region
}

# =========================================================================
# 1. REDE (NETWORKING) - Criando do Zero
# =========================================================================

# Criar a VPC (Rede Virtual)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Criar o Internet Gateway (Porta para a Internet)
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Criar a Subnet Pública
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

# Tabela de Roteamento (Rota para Internet)
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Associar a Tabela de Roteamento à Subnet
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# =========================================================================
# 2. ARMAZENAMENTO (S3 e ECR)
# =========================================================================

resource "aws_s3_bucket" "app_bucket" {
  bucket_prefix = "${var.project_name}-logs-"
  force_destroy = true
}

resource "aws_ecr_repository" "app_repo" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

# =========================================================================
# 3. SEGURANÇA (IAM e Security Groups)
# =========================================================================

# Security Group (Firewall)
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Role e Policies (Permissão para EC2 acessar S3 e ECR)
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-role-v2" # Mudei o nome para evitar conflito se o antigo ficou preso

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "s3_policy" {
  name = "${var.project_name}-s3-policy-v2"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.app_bucket.arn,
          "${aws_s3_bucket.app_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ecr" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-profile-v2"
  role = aws_iam_role.ec2_role.name
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key-v2"
  public_key = var.my_public_key
}

# =========================================================================
# 4. COMPUTAÇÃO (EC2)
# =========================================================================

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"

  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  # Vincula à subnet pública que criamos
  subnet_id = aws_subnet.public_subnet.id

  # Script de inicialização
  # Inclui criação de SWAP para evitar travamento da memória
  user_data = <<-EOF
    #!/bin/bash
    dnf update -y
    dnf install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    
    # Espera rede estabilizar
    sleep 10

    # Login ECR
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${aws_ecr_repository.app_repo.repository_url}

    # Run Container
    docker run -d \
      --restart always \
      -p 8501:8501 \
      -e STREAMLIT_SERVER_PORT=8501 \
      -e GOOGLE_API_KEY="${var.google_api_key}" \
      -e MONGODB_CONNECTION_STRING="${var.mongodb_connection_string}" \
      -e DATABASE="${var.database_name}" \
      -e COLLECTION="${var.collection_name}" \
      -e LOG_COLLECTION="${var.log_collection_name}" \
      -e TAVILY_API_KEY="${var.tavily_api_key}" \
      -e S3_BUCKET_NAME="${aws_s3_bucket.app_bucket.bucket}" \
      ${aws_ecr_repository.app_repo.repository_url}:latest
  EOF

  tags = {
    Name = "gs2025-app-server"
  }

  depends_on = [aws_internet_gateway.igw, aws_iam_role_policy_attachment.attach_ecr]
}
