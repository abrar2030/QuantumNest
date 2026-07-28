variable "app_name"         {}
variable "environment"      {}
variable "vpc_id"           {}
variable "cluster_name"     {}
variable "cluster_version"  { default = "1.29" }
variable "subnet_ids"       { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "instance_type"    { default = "t3.micro" }
variable "key_name"         { default = null }
variable "private_subnet_ids" {
  type = list(string)
  default = []
}
variable "kms_key_arn"      { default = "" }
variable "cluster_endpoint_public_access"       { default = true }
variable "cluster_endpoint_public_access_cidrs" {
  type = list(string)
  default = ["0.0.0.0/0"]
}
variable "cluster_enabled_log_types" {
  type = list(string)
  default = []
}
variable "node_groups" {
  type = any
  default = {}
}
variable "tags"             {
  type = map(string)
  default = {}
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.cluster_version
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids              = var.subnet_ids
    security_group_ids      = var.security_group_ids
    endpoint_public_access  = var.cluster_endpoint_public_access
    endpoint_private_access = true
    public_access_cidrs     = var.cluster_endpoint_public_access_cidrs
  }

  dynamic "encryption_config" {
    for_each = var.kms_key_arn != "" ? [1] : []
    content {
      resources = ["secrets"]
      provider {
        key_arn = var.kms_key_arn
      }
    }
  }

  enabled_cluster_log_types = var.cluster_enabled_log_types

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]

  tags = merge(var.tags, {
    Name        = var.cluster_name
    Environment = var.environment
  })
}

# EKS Cluster IAM Role
resource "aws_iam_role" "eks_cluster" {
  name = "${var.cluster_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

# EKS Node Groups
resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = each.key
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = var.subnet_ids

  instance_types = lookup(each.value, "instance_types", ["m5.large"])
  capacity_type  = lookup(each.value, "capacity_type", "ON_DEMAND")

  scaling_config {
    desired_size = lookup(each.value, "desired_capacity", 2)
    min_size     = lookup(each.value, "min_capacity", 1)
    max_size     = lookup(each.value, "max_capacity", 10)
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry,
  ]

  tags = merge(var.tags, {
    Name        = "${var.cluster_name}-${each.key}"
    Environment = var.environment
  })
}

# EKS Node IAM Role
resource "aws_iam_role" "eks_node" {
  name = "${var.cluster_name}-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_node_policy" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "eks_container_registry" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Launch Template for ASG (non-EKS workloads)
resource "aws_launch_template" "app" {
  name_prefix   = "${var.app_name}-${var.environment}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name

  network_interfaces {
    associate_public_ip_address = false
    security_groups             = var.security_group_ids
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.tags, {
      Name        = "${var.app_name}-${var.environment}"
      Environment = var.environment
    })
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -euo pipefail
    dnf update -y
    dnf install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ec2-user
  EOF
  )
}

resource "aws_autoscaling_group" "app" {
  name                = "${var.app_name}-${var.environment}-asg"
  vpc_zone_identifier = length(var.private_subnet_ids) > 0 ? var.private_subnet_ids : var.subnet_ids
  min_size            = 2
  max_size            = 5
  desired_capacity    = 2

  health_check_type         = "ELB"
  health_check_grace_period = 300

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  dynamic "tag" {
    for_each = merge(var.tags, {
      Name        = "${var.app_name}-${var.environment}-asg"
      Environment = var.environment
    })
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}

resource "aws_lb" "app" {
  name               = "${var.app_name}-${substr(var.environment, 0, 4)}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.security_group_ids
  subnets            = var.subnet_ids

  drop_invalid_header_fields = true
  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = merge(var.tags, {
    Name        = "${var.app_name}-${var.environment}-lb"
    Environment = var.environment
  })
}

resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-${substr(var.environment, 0, 4)}-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/health/ready"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  stickiness {
    type    = "lb_cookie"
    enabled = false
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

output "cluster_endpoint"                    { value = aws_eks_cluster.main.endpoint }
output "cluster_name"                        { value = aws_eks_cluster.main.name }
output "cluster_certificate_authority_data"  { value = aws_eks_cluster.main.certificate_authority[0].data }
output "instance_ids"                        { value = [] }
output "instance_public_ips"                 { value = [] }
output "load_balancer_dns"                   { value = aws_lb.app.dns_name }
