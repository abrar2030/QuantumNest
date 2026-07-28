# QuantumNest Infrastructure Tools - Multi-stage Dockerfile
# Provides a containerized environment for running infrastructure operations

FROM ubuntu:24.04 AS base

ARG TERRAFORM_VERSION=1.9.5
ARG KUBECTL_VERSION=1.29.9
ARG HELM_VERSION=3.16.1
ARG ANSIBLE_VERSION=10.4.0
ARG AWSCLI_VERSION=2.17.50

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    unzip \
    git \
    jq \
    yq \
    python3 \
    python3-pip \
    python3-venv \
    openssh-client \
    gnupg \
    ca-certificates \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    bash-completion \
    gettext-base \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ──────────────────────────────────────────────
# Stage: terraform
# ──────────────────────────────────────────────
FROM base AS terraform-installer
ARG TERRAFORM_VERSION
RUN curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o /tmp/terraform.zip \
    && unzip /tmp/terraform.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm /tmp/terraform.zip \
    && terraform version

# ──────────────────────────────────────────────
# Stage: kubectl
# ──────────────────────────────────────────────
FROM base AS kubectl-installer
ARG KUBECTL_VERSION
RUN curl -fsSL "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && kubectl version --client

# ──────────────────────────────────────────────
# Stage: helm
# ──────────────────────────────────────────────
FROM base AS helm-installer
ARG HELM_VERSION
RUN curl -fsSL "https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz" | tar -xz -C /tmp/ \
    && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf /tmp/linux-amd64 \
    && helm version

# ──────────────────────────────────────────────
# Stage: awscli
# ──────────────────────────────────────────────
FROM base AS awscli-installer
ARG AWSCLI_VERSION
RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWSCLI_VERSION}.zip" -o /tmp/awscliv2.zip \
    && unzip /tmp/awscliv2.zip -d /tmp/ \
    && /tmp/aws/install \
    && rm -rf /tmp/aws /tmp/awscliv2.zip \
    && aws --version

# ──────────────────────────────────────────────
# Final stage: runtime image
# ──────────────────────────────────────────────
FROM base AS final

# Copy tools from installer stages
COPY --from=terraform-installer /usr/local/bin/terraform /usr/local/bin/terraform
COPY --from=kubectl-installer   /usr/local/bin/kubectl   /usr/local/bin/kubectl
COPY --from=helm-installer      /usr/local/bin/helm      /usr/local/bin/helm
COPY --from=awscli-installer    /usr/local/aws-cli       /usr/local/aws-cli
COPY --from=awscli-installer    /usr/local/bin/aws       /usr/local/bin/aws
COPY --from=awscli-installer    /usr/local/bin/aws_completer /usr/local/bin/aws_completer

# Install Ansible and Python dependencies
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    "ansible==${ANSIBLE_VERSION}" \
    ansible-lint \
    boto3 \
    botocore \
    jmespath \
    netaddr \
    kubernetes \
    openshift \
    && ansible --version

# Create non-root user for running operations
RUN groupadd -r infraops && useradd -r -g infraops -m -s /bin/bash infraops \
    && mkdir -p /workspace /home/infraops/.aws /home/infraops/.kube /home/infraops/.terraform.d \
    && chown -R infraops:infraops /workspace /home/infraops/.aws /home/infraops/.kube /home/infraops/.terraform.d

# Copy infrastructure files
COPY --chown=infraops:infraops . /workspace/

# Make scripts executable
RUN chmod +x /workspace/deploy.sh /workspace/validate_infrastructure.sh \
    && find /workspace -name "*.sh" -exec chmod +x {} \;

WORKDIR /workspace

# Healthcheck: verify critical tools are available
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD terraform version && kubectl version --client && helm version && aws --version && ansible --version || exit 1

USER infraops

# Default entrypoint shows help
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "echo 'QuantumNest Infrastructure Tools'; echo 'Available: terraform, kubectl, helm, aws, ansible'; echo 'Run: ./deploy.sh'"]
