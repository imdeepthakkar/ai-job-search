FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install essential system tools, LaTeX engine, fonts, poppler-utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    unzip \
    git \
    python3 \
    python3-pip \
    texlive-xetex \
    texlive-luatex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    fonts-lato \
    fonts-raleway \
    poppler-utils \
    ttyd \
    && rm -rf /var/lib/apt/lists/*

# If ttyd wasn't installed from apt, grab the official binary
RUN if ! command -v ttyd >/dev/null; then \
      curl -fsSL https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64 -o /usr/local/bin/ttyd && \
      chmod +x /usr/local/bin/ttyd; \
    fi

# Install Bun
ENV BUN_INSTALL=/root/.bun
ENV PATH="${BUN_INSTALL}/bin:/root/.local/bin:/usr/local/bin:${PATH}"
RUN curl -fsSL https://bun.sh/install | bash

# Install Antigravity CLI (agy)
RUN curl -fsSL https://antigravity.google/cli/install.sh | bash || true
RUN ln -sf /root/.local/bin/agy /usr/local/bin/agy || true

WORKDIR /app
COPY . /app

# Install python packages
RUN pip install --no-cache-dir --break-system-packages \
    google-api-python-client \
    google-auth \
    pypdf

# Install portal CLIs
RUN python3 tools/install_portal_clis.py || true

# Setup superpowers plugin
RUN mkdir -p /root/.gemini/config/plugins && \
    git clone https://github.com/obra/superpowers.git /root/.gemini/config/plugins/superpowers 2>/dev/null || true && \
    echo '{"plugins":{"superpowers":{"enabled":true}}}' > /root/.gemini/config/config.json

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 7681 8080

CMD ["/docker-entrypoint.sh"]
