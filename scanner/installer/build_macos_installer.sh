#!/bin/bash
set -e

# Parse command-line arguments
SKIP_DMG=false
for arg in "$@"; do
  case $arg in
    --skip-dmg)
      SKIP_DMG=true
      shift
      ;;
  esac
done

# Change to the installer directory
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building BLE Kafka Scanner macOS Universal Installer${NC}"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if py2app is installed
if ! pip show py2app > /dev/null; then
    echo -e "${YELLOW}Installing py2app...${NC}"
    pip install py2app
fi

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null && [ "$SKIP_DMG" = false ]; then
    echo -e "${YELLOW}Installing create-dmg using Homebrew...${NC}"
    brew install create-dmg
fi

# Create a simple app icon if it doesn't exist
if [ ! -f "app_icon.icns" ]; then
    echo -e "${YELLOW}Creating a placeholder app icon...${NC}"
    
    # Create a temporary directory for the icon
    ICON_DIR=$(mktemp -d)
    
    # Try using our Python script first
    if [ -f "create_icon.py" ]; then
        echo -e "${YELLOW}Using create_icon.py to generate icon...${NC}"
        python create_icon.py "$ICON_DIR/icon.png"
    else
        # Generate a simple colored square as a PNG using ImageMagick
        echo -e "${YELLOW}Trying ImageMagick for icon creation...${NC}"
        convert -size 1024x1024 xc:blue -fill white -gravity center -pointsize 72 -annotate 0 "BLE\nKafka\nScanner" "$ICON_DIR/icon.png" 2>/dev/null
        
        # If ImageMagick is not available, try a simpler approach with Python
        if [ ! -f "$ICON_DIR/icon.png" ]; then
            echo -e "${YELLOW}ImageMagick not found, using Python PIL...${NC}"
            python -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (1024, 1024), color = (0, 0, 255))
d = ImageDraw.Draw(img)
d.rectangle([(10, 10), (1014, 1014)], outline=(255, 255, 255), width=10)
img.save('$ICON_DIR/icon.png')
            " 2>/dev/null
        fi
        
        # If all else fails, create a very basic icon
        if [ ! -f "$ICON_DIR/icon.png" ]; then
            echo -e "${YELLOW}Creating a very basic icon...${NC}"
            echo "BLE Kafka Scanner" > "$ICON_DIR/icon.png"
        fi
    fi
    
    # Create the iconset directory
    mkdir -p "$ICON_DIR/AppIcon.iconset"
    
    # Create different sizes for the iconset
    for size in 16 32 128 256 512; do
        # Regular size
        sips -z $size $size "$ICON_DIR/icon.png" --out "$ICON_DIR/AppIcon.iconset/icon_${size}x${size}.png" 2>/dev/null || echo "Error creating icon size $size"
        
        # Retina size (2x)
        if [ $size -lt 512 ]; then
            double=$((size * 2))
            sips -z $double $double "$ICON_DIR/icon.png" --out "$ICON_DIR/AppIcon.iconset/icon_${size}x${size}@2x.png" 2>/dev/null || echo "Error creating icon size $double"
        fi
    done
    
    # Create the icns file
    iconutil -c icns "$ICON_DIR/AppIcon.iconset" -o "app_icon.icns" 2>/dev/null
    
    # If iconutil fails, use a simple file as the icon
    if [ ! -f "app_icon.icns" ]; then
        echo -e "${YELLOW}iconutil failed, creating a simple icon file...${NC}"
        cp "$ICON_DIR/icon.png" "app_icon.icns"
    fi
    
    # Clean up
    rm -rf "$ICON_DIR"
    
    echo -e "${GREEN}App icon created.${NC}"
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build dist

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r ../requirements.txt

# Build the app using py2app with universal2 architecture
echo -e "${YELLOW}Building the universal app with py2app...${NC}"
python ble_kafka_setup.py py2app --arch=universal2

if [ "$SKIP_DMG" = false ]; then
    # Create DMG
    echo -e "${YELLOW}Creating DMG installer...${NC}"
    create-dmg \
      --volname "BLE Kafka Scanner" \
      --volicon "app_icon.icns" \
      --window-pos 200 120 \
      --window-size 800 400 \
      --icon-size 100 \
      --icon "BLE Kafka Scanner.app" 200 190 \
      --hide-extension "BLE Kafka Scanner.app" \
      --app-drop-link 600 185 \
      "../BLE Kafka Scanner.dmg" \
      "dist/BLE Kafka Scanner.app"
    
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}Universal Installer created: ../BLE Kafka Scanner.dmg${NC}"
else
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}App created at: dist/BLE Kafka Scanner.app${NC}"
    echo -e "${YELLOW}DMG creation was skipped as requested.${NC}"
fi

echo -e "${YELLOW}This installer works on both Intel and Apple Silicon Macs.${NC}"

# Move back to the original directory
cd - > /dev/null 