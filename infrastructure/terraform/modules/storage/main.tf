variable "app_name"           {}
variable "environment"        {}
variable "cluster_id"         {}
variable "subnet_group_name"  {}
variable "security_group_ids" { type = list(string) }
variable "node_type"          { default = "cache.r6g.large" }
variable "num_cache_clusters" { default = 1 }
variable "at_rest_encryption_enabled" { default = true }
variable "transit_encryption_enabled" { default = true }
variable "auth_token"         {
  default = null
  sensitive = true
}
variable "kms_key_id"         { default = null }
variable "snapshot_retention_limit" { default = 1 }
variable "tags"               {
  type = map(string)
  default = {}
}

resource "aws_s3_bucket" "main" {
  bucket        = "${var.app_name}-${var.environment}-assets"
  force_destroy = var.environment != "prod"

  tags = merge(var.tags, {
    Name        = "${var.app_name}-${var.environment}-assets"
    Environment = var.environment
  })
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = var.environment == "prod" ? "Enabled" : "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "transition_old_versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}

# ElastiCache Replication Group (Redis)
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = var.cluster_id
  description          = "QuantumNest Redis cluster for ${var.environment}"

  node_type            = var.node_type
  num_cache_clusters   = var.num_cache_clusters
  port                 = 6379

  subnet_group_name  = var.subnet_group_name
  security_group_ids = var.security_group_ids

  at_rest_encryption_enabled = var.at_rest_encryption_enabled
  transit_encryption_enabled = var.transit_encryption_enabled
  auth_token                 = var.transit_encryption_enabled ? var.auth_token : null
  kms_key_id                 = var.kms_key_id

  automatic_failover_enabled = var.num_cache_clusters > 1 ? true : false
  multi_az_enabled           = var.num_cache_clusters > 1 ? true : false

  snapshot_retention_limit = var.snapshot_retention_limit
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "sun:05:00-sun:07:00"

  auto_minor_version_upgrade = true
  apply_immediately          = var.environment != "prod"

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  tags = merge(var.tags, {
    Name        = var.cluster_id
    Environment = var.environment
  })
}

resource "aws_cloudwatch_log_group" "redis_slow" {
  name              = "/aws/elasticache/${var.cluster_id}/slow-logs"
  retention_in_days = 30

  tags = var.tags
}

output "s3_bucket_name"        { value = aws_s3_bucket.main.id }
output "s3_bucket_arn"         { value = aws_s3_bucket.main.arn }
output "cache_cluster_address" { value = aws_elasticache_replication_group.redis.primary_endpoint_address }
output "cache_cluster_id"      { value = aws_elasticache_replication_group.redis.id }
output "cache_port"            { value = aws_elasticache_replication_group.redis.port }
