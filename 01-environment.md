# 环境配置

## 硬件环境

| 项目 | 配置 |
|------|------|
| GPU | AMD Radeon gfx1100 (RDNA3), 48GB VRAM |
| 计算平台 | ROCm 7.2.1 |
| OS | Ubuntu 24.04 LTS |
| Python | 3.12.3 |
| PyTorch | 2.9.1+rocm（平台预装） |
| MinerU | 3.4.0 |

## 换源（阿里云镜像）

```bash
cat > /etc/apt/sources.list.d/ubuntu.sources << 'EOF'
Types: deb
URIs: http://mirrors.aliyun.com/ubuntu/
Suites: noble noble-updates noble-backports
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF
apt-get update
```

## 安装 LaTeX 工具链

```bash
apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-dejavu-extra \
  pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-lang-chinese
```

## ROCm 常用命令

```bash
rocm-smi                          # GPU 状态
rocm-smi --showproductname        # GPU 型号
cat /opt/rocm/.info/version       # ROCm 版本
```
