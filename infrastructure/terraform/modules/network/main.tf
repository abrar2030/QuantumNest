variable "name"             {}
variable "environment"      {}
variable "vpc_cidr"         {}
variable "azs"              { type = list(string) }
variable "private_subnets"  { type = list(string) }
variable "public_subnets"   { type = list(string) }
variable "database_subnets" { type = list(string) }
variable "enable_nat_gateway"    { default = true }
variable "enable_dns_hostnames"  { default = true }
variable "enable_dns_support"    { default = true }
variable "flow_log_destination_arn" { default = "" }
variable "tags"             {
  type = map(string)
  default = {}
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = var.enable_dns_support
  enable_dns_hostnames = var.enable_dns_hostnames

  tags = merge(var.tags, {
    Name        = "${var.name}-vpc"
    Environment = var.environment
  })
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnets)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name        = "${var.name}-public-subnet-${count.index + 1}"
    Environment = var.environment
    "kubernetes.io/role/elb" = "1"
  })
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = var.azs[count.index]

  tags = merge(var.tags, {
    Name        = "${var.name}-private-subnet-${count.index + 1}"
    Environment = var.environment
    "kubernetes.io/role/internal-elb" = "1"
  })
}

resource "aws_subnet" "database" {
  count             = length(var.database_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.database_subnets[count.index]
  availability_zone = var.azs[count.index]

  tags = merge(var.tags, {
    Name        = "${var.name}-database-subnet-${count.index + 1}"
    Environment = var.environment
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.tags, {
    Name        = "${var.name}-igw"
    Environment = var.environment
  })
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.public_subnets) : 0
  domain = "vpc"

  tags = merge(var.tags, {
    Name        = "${var.name}-nat-eip-${count.index + 1}"
    Environment = var.environment
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? length(var.public_subnets) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.tags, {
    Name        = "${var.name}-nat-gateway-${count.index + 1}"
    Environment = var.environment
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-public-route-table"
    Environment = var.environment
  })
}

resource "aws_route_table" "private" {
  count  = length(var.private_subnets)
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(var.tags, {
    Name        = "${var.name}-private-route-table-${count.index + 1}"
    Environment = var.environment
  })
}

resource "aws_route_table_association" "public" {
  count          = length(var.public_subnets)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = length(var.private_subnets)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_db_subnet_group" "database" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = aws_subnet.database[*].id

  tags = merge(var.tags, {
    Name        = "${var.name}-db-subnet-group"
    Environment = var.environment
  })
}

resource "aws_flow_log" "vpc" {
  count                = var.flow_log_destination_arn != "" ? 1 : 0
  vpc_id               = aws_vpc.main.id
  traffic_type         = "ALL"
  iam_role_arn         = aws_iam_role.flow_log[0].arn
  log_destination      = var.flow_log_destination_arn
  log_destination_type = "s3"

  tags = merge(var.tags, {
    Name = "${var.name}-vpc-flow-log"
  })
}

resource "aws_iam_role" "flow_log" {
  count = var.flow_log_destination_arn != "" ? 1 : 0
  name  = "${var.name}-vpc-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "vpc-flow-logs.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "flow_log" {
  count = var.flow_log_destination_arn != "" ? 1 : 0
  name  = "${var.name}-vpc-flow-log-policy"
  role  = aws_iam_role.flow_log[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ]
      Resource = "*"
    }]
  })
}

output "vpc_id"              { value = aws_vpc.main.id }
output "public_subnet_ids"  { value = aws_subnet.public[*].id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
output "database_subnet_ids" { value = aws_subnet.database[*].id }
output "database_subnet_group" { value = aws_db_subnet_group.database.name }
output "private_subnets"    { value = aws_subnet.private[*].id }
output "public_subnets"     { value = aws_subnet.public[*].id }
