variable "db_name"           {}
variable "environment"       {}
variable "db_instance_class" { default = "db.t3.small" }
variable "db_username"       { sensitive = true }
variable "db_password"       { sensitive = true }
variable "private_subnet_ids"  { type = list(string) }
variable "security_group_ids"  { type = list(string) }
variable "storage_encrypted"   { default = true }
variable "kms_key_id"          { default = null }
variable "multi_az"            { default = false }
variable "backup_retention_period" { default = 7 }
variable "deletion_protection"  { default = false }
variable "skip_final_snapshot"  { default = true }
variable "final_snapshot_identifier" { default = null }
variable "monitoring_role_arn"  { default = null }
variable "tags"                 {
  type = map(string)
  default = {}
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.db_name}-${var.environment}-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name        = "${var.db_name}-${var.environment}-subnet-group"
    Environment = var.environment
  })
}

resource "aws_db_parameter_group" "postgres" {
  name   = "${var.db_name}-${var.environment}-pg14"
  family = "postgres14"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "ssl"
    value = "1"
  }

  tags = merge(var.tags, {
    Name = "${var.db_name}-${var.environment}-parameter-group"
  })
}

resource "aws_db_instance" "main" {
  identifier     = "${var.db_name}-${var.environment}"
  engine         = "postgres"
  engine_version = "14.12"
  instance_class = var.db_instance_class

  allocated_storage     = var.environment == "prod" ? 1000 : 100
  max_allocated_storage = var.environment == "prod" ? 5000 : 500
  storage_type          = "gp3"
  storage_encrypted     = var.storage_encrypted
  kms_key_id            = var.kms_key_id

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  parameter_group_name   = aws_db_parameter_group.postgres.name
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids

  multi_az               = var.multi_az
  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.final_snapshot_identifier

  performance_insights_enabled          = true
  performance_insights_kms_key_id       = var.kms_key_id
  performance_insights_retention_period = var.environment == "prod" ? 731 : 7

  monitoring_interval = 60
  monitoring_role_arn = var.monitoring_role_arn

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  auto_minor_version_upgrade  = true
  apply_immediately           = var.environment != "prod"

  copy_tags_to_snapshot = true

  tags = merge(var.tags, {
    Name        = "${var.db_name}-${var.environment}"
    Environment = var.environment
  })
}

output "db_instance_endpoint"  { value = aws_db_instance.main.endpoint }
output "db_instance_id"        { value = aws_db_instance.main.id }
output "db_endpoint"           { value = aws_db_instance.main.endpoint }
output "db_subnet_group_name"  { value = aws_db_subnet_group.main.name }
