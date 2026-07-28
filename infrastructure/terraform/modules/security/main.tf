variable "name"        {}
variable "environment" {}
variable "vpc_id"      {}
variable "private_subnets_cidr" {
  type = list(string)
  default = []
}
variable "public_subnets_cidr"  {
  type = list(string)
  default = []
}
variable "tags"        {
  type = map(string)
  default = {}
}

# Load Balancer Security Group
resource "aws_security_group" "lb" {
  name        = "${var.name}-lb-sg"
  description = "Security group for load balancer in ${var.environment}"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from internet (redirect to HTTPS)"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-lb-sg"
    Environment = var.environment
  })
}

# Application Security Group - only accessible from LB
resource "aws_security_group" "app" {
  name        = "${var.name}-app-sg"
  description = "Security group for ${var.name} application in ${var.environment}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.lb.id]
    description     = "HTTP from load balancer"
  }

  ingress {
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.lb.id]
    description     = "HTTPS from load balancer"
  }

  ingress {
    from_port       = 9090
    to_port         = 9090
    protocol        = "tcp"
    cidr_blocks     = var.private_subnets_cidr
    description     = "Metrics from private subnets"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-app-sg"
    Environment = var.environment
  })
}

# Database Security Group - only accessible from app
resource "aws_security_group" "db" {
  name        = "${var.name}-db-sg"
  description = "Security group for ${var.name} database in ${var.environment}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "PostgreSQL from application"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-db-sg"
    Environment = var.environment
  })
}

# Cache Security Group - only accessible from app
resource "aws_security_group" "cache" {
  name        = "${var.name}-cache-sg"
  description = "Security group for ${var.name} cache in ${var.environment}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Redis from application"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-cache-sg"
    Environment = var.environment
  })
}

output "app_security_group_id"      { value = aws_security_group.app.id }
output "db_security_group_id"       { value = aws_security_group.db.id }
output "database_security_group_id" { value = aws_security_group.db.id }
output "cache_security_group_id"    { value = aws_security_group.cache.id }
output "lb_security_group_id"       { value = aws_security_group.lb.id }
