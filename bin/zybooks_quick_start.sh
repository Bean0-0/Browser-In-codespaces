#!/bin/bash
# Quick start script for Zybooks automation

echo "🤖 Zybooks Auto-Completion Tool"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Read docs/ZYBOOKS_AUTOMATION.md before use"
echo "⚠️  Use responsibly and ethically"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if traffic database exists
if [ ! -f "data/traffic.db" ]; then
    echo "❌ No traffic database found!"
    echo ""
    echo "You need to capture traffic first:"
    echo "  1. Run: ./bin/start_analyzer.sh"
    echo "  2. Configure browser proxy (localhost:8080)"
    echo "  3. Browse Zybooks and complete at least one activity"
    echo "  4. Then run this script again"
    exit 1
fi

# Check for zybooks traffic
echo "🔍 Checking for captured zybooks traffic..."
ZYBOOKS_COUNT=$(python3 bin/traffic_analyzer.py stats --zybooks 2>/dev/null | grep "Total Requests:" | awk '{print $3}')

if [ -z "$ZYBOOKS_COUNT" ] || [ "$ZYBOOKS_COUNT" = "0" ]; then
    echo "❌ No zybooks traffic found in database!"
    echo ""
    echo "Make sure you:"
    echo "  1. Started the proxy: ./bin/start_analyzer.sh"
    echo "  2. Configured browser to use proxy"
    echo "  3. Browsed to Zybooks and completed activities"
    exit 1
fi

echo "✅ Found $ZYBOOKS_COUNT zybooks requests"
echo ""

# Show summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Activity Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 bin/zybooks_autocomplete.py summary
echo ""

# Ask user what to do
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "What would you like to do?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1) Show authentication info"
echo "  2) Dry run (show what would be completed)"
echo "  3) Auto-complete ALL incomplete activities"
echo "  4) Auto-complete with custom delay"
echo "  5) Complete specific resource IDs"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        python3 bin/zybooks_autocomplete.py auth
        ;;
    2)
        echo ""
        echo "🔍 DRY RUN MODE - No changes will be made"
        echo ""
        python3 bin/zybooks_autocomplete.py auto --dry-run
        ;;
    3)
        echo ""
        echo "⚠️  This will complete ALL incomplete activities!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo ""
            python3 bin/zybooks_autocomplete.py auto
        else
            echo "Cancelled."
        fi
        ;;
    4)
        echo ""
        read -p "Enter delay in seconds (e.g., 2.5): " delay
        echo ""
        echo "⚠️  This will complete ALL incomplete activities with ${delay}s delay"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo ""
            python3 bin/zybooks_autocomplete.py auto --delay "$delay"
        else
            echo "Cancelled."
        fi
        ;;
    5)
        echo ""
        read -p "Enter resource IDs (space-separated): " resource_ids
        if [ -n "$resource_ids" ]; then
            echo ""
            python3 bin/zybooks_autocomplete.py complete $resource_ids
        else
            echo "No IDs provided."
        fi
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Done!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
