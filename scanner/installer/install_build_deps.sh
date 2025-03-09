#!/bin/bash
set -e

# Change to the installer directory
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing dependencies for building BLE Kafka Scanner${NC}"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo -e "${GREEN}Homebrew is already installed.${NC}"
fi

# Install blueutil for Bluetooth management
if ! command -v blueutil &> /dev/null; then
    echo -e "${YELLOW}Installing blueutil...${NC}"
    brew install blueutil
else
    echo -e "${GREEN}blueutil is already installed.${NC}"
fi

# Install create-dmg for creating the installer
if ! command -v create-dmg &> /dev/null; then
    echo -e "${YELLOW}Installing create-dmg...${NC}"
    brew install create-dmg
else
    echo -e "${GREEN}create-dmg is already installed.${NC}"
fi

# Try to install ImageMagick for icon creation
if ! command -v convert &> /dev/null; then
    echo -e "${YELLOW}Installing ImageMagick for icon creation...${NC}"
    brew install imagemagick || echo "ImageMagick installation failed, will use fallback methods"
else
    echo -e "${GREEN}ImageMagick is already installed.${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r ../requirements.txt

# Install py2app for building the macOS app
if ! pip show py2app &> /dev/null; then
    echo -e "${YELLOW}Installing py2app...${NC}"
    pip install py2app
else
    echo -e "${GREEN}py2app is already installed.${NC}"
fi

# Install Pillow for icon creation
if ! pip show Pillow &> /dev/null; then
    echo -e "${YELLOW}Installing Pillow for icon creation...${NC}"
    pip install Pillow
else
    echo -e "${GREEN}Pillow is already installed.${NC}"
fi

echo -e "${GREEN}All dependencies installed successfully!${NC}"
echo -e "${YELLOW}You can now run ./build_macos_installer.sh to build the installer.${NC}"

# Move back to the original directory
cd - > /dev/null 