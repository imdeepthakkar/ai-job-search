#!/usr/bin/env bash
set -e

echo "=== 1. Installing System Packages (TeX Live, Fonts, Poppler) ==="
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  texlive-xetex \
  texlive-luatex \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  fonts-lato \
  fonts-raleway \
  poppler-utils \
  curl \
  unzip \
  git

echo "=== 2. Installing Python Packages (Google Drive, Salary & Automation) ==="
pip install --no-cache-dir google-api-python-client google-auth pypdf || true

echo "=== 3. Installing Bun ==="
if ! command -v bun &> /dev/null; then
  curl -fsSL https://bun.sh/install | bash
fi
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Persist environment variables in ~/.bashrc and ~/.zshrc
echo 'export BUN_INSTALL="$HOME/.bun"' >> "$HOME/.bashrc"
echo 'export PATH="$BUN_INSTALL/bin:$HOME/.local/bin:$HOME/.gemini/antigravity-cli/bin:$PATH"' >> "$HOME/.bashrc"

if [ -f "$HOME/.zshrc" ]; then
  echo 'export BUN_INSTALL="$HOME/.bun"' >> "$HOME/.zshrc"
  echo 'export PATH="$BUN_INSTALL/bin:$HOME/.local/bin:$HOME/.gemini/antigravity-cli/bin:$PATH"' >> "$HOME/.zshrc"
fi

echo "=== 4. Installing Antigravity CLI (agy) ==="
if ! command -v agy &> /dev/null; then
  curl -fsSL https://antigravity.google/cli/install.sh | bash || true
fi
export PATH="$HOME/.local/bin:$HOME/.gemini/antigravity-cli/bin:$PATH"

echo "=== 5. Setting up Global AGY Config & Superpowers Plugin ==="
mkdir -p "$HOME/.gemini/config/plugins"

if [ ! -d "$HOME/.gemini/config/plugins/superpowers" ]; then
  git clone https://github.com/obra/superpowers.git "$HOME/.gemini/config/plugins/superpowers"
fi

cat > "$HOME/.gemini/config/config.json" << 'EOF'
{
  "plugins": {
    "superpowers": {
      "enabled": true
    }
  }
}
EOF

# Setup Notion MCP server configuration if NOTION_TOKEN is present
cat > "$HOME/.gemini/config/mcp_config.json" << EOF
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "disabled": false,
      "env": {
        "NOTION_TOKEN": "${NOTION_TOKEN:-}"
      }
    }
  }
}
EOF

echo "=== 6. Installing Portal Search CLIs ==="
python3 tools/install_portal_clis.py || python tools/install_portal_clis.py

echo "=== 7. Git Safe Directory ==="
git config --global --add safe.directory /workspaces/ai-job-search || true

echo "=== Setup complete! Type 'agy' to launch Antigravity. ==="
