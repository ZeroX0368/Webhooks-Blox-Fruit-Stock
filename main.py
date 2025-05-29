
import requests
import json
import time
import hashlib
from datetime import datetime

# Global variable to store previous data hash
previous_data_hash = None

def get_bloxfruit_data():
    """Fetch data from the BloxFruit API"""
    try:
        response = requests.get("http://test-hub.kys.gay/api/stock/bloxfruit")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching BloxFruit data: {e}")
        return None

def get_data_hash(data):
    """Generate hash of data to detect changes"""
    if not data:
        return None
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_string.encode()).hexdigest()

def has_data_changed(data):
    """Check if data has changed since last check"""
    global previous_data_hash
    current_hash = get_data_hash(data)
    
    if previous_data_hash is None:
        previous_data_hash = current_hash
        return True  # First run, consider as changed
    
    if current_hash != previous_data_hash:
        previous_data_hash = current_hash
        return True
    
    return False

def send_discord_webhook(data):
    """Send data to Discord webhook with embed"""
    webhook_url = "YOU WEBHOOK URL"
    
    if not data:
        return False
    
    # Create embed with BloxFruit data
    embed = {
        "title": "🍎 BloxFruit Stock Update",
        "description": "🔄 Stock đã được cập nhật! Có thay đổi mới trong kho.",
        "color": 0x00ff00,  # Green color for updates
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "BloxFruit Monitor Bot • Cập nhật tự động",
            "icon_url": "https://cdn.discordapp.com/emojis/123456789.png"
        },
        "fields": []
    }
    
    # Handle Normal Stock specifically
    if "normal_stock" in data and "items" in data["normal_stock"]:
        normal_items = data["normal_stock"]["items"]
        
        embed["fields"].append({
            "name": "🔹 Normal Stock",
            "value": f"Có {len(normal_items)} mặt hàng trong kho thường",
            "inline": False
        })
        
        for item in normal_items:
            name = item.get("name", "Unknown")
            usd_price = item.get("usd_price", "N/A")
            robux_price = item.get("robux_price", "N/A")
            
            embed["fields"].append({
                "name": f"🍇 {name}",
                "value": f"💰 **Giá USD:** {usd_price}\n💎 **Giá Robux:** {robux_price}",
                "inline": True
            })
    
    # Handle Mirage Stock
    if "mirage_stock" in data and "items" in data["mirage_stock"]:
        mirage_items = data["mirage_stock"]["items"]
        
        embed["fields"].append({
            "name": "✨ Mirage Stock",
            "value": f"Có {len(mirage_items)} mặt hàng hiếm trong kho đặc biệt",
            "inline": False
        })
        
        for item in mirage_items:
            name = item.get("name", "Unknown")
            usd_price = item.get("usd_price", "N/A")
            robux_price = item.get("robux_price", "N/A")
            
            embed["fields"].append({
                "name": f"⭐ {name}",
                "value": f"💰 **Giá USD:** {usd_price}\n💎 **Giá Robux:** {robux_price}",
                "inline": True
            })
    
    # Prepare webhook payload
    payload = {
        "username": "BloxFruit Monitor",
        "avatar_url": "https://cdn.discordapp.com/emojis/123456789.png",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("✅ Đã gửi thông báo thay đổi đến Discord!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi gửi webhook: {e}")
        return False

def monitor_bloxfruit_stock():
    """Continuously monitor BloxFruit stock for changes"""
    print("🚀 Bắt đầu theo dõi BloxFruit stock...")
    print("⏱️  Bot sẽ kiểm tra thay đổi mỗi 30 giây")
    print("🔄 Chỉ gửi thông báo khi có thay đổi thực sự")
    print("🛑 Nhấn Ctrl+C để dừng bot\n")
    
    check_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"📡 [{current_time}] Kiểm tra lần #{check_count}...")
            
            # Fetch data from API
            data = get_bloxfruit_data()
            
            if data:
                # Check if data has changed
                if has_data_changed(data):
                    print("🔄 Phát hiện thay đổi trong stock!")
                    print(f"📊 Dữ liệu mới: {json.dumps(data, indent=2)}")
                    
                    # Send webhook notification
                    success = send_discord_webhook(data)
                    
                    if success:
                        print("🎉 Đã thông báo thay đổi thành công!")
                    else:
                        print("❌ Không thể gửi thông báo")
                else:
                    print("✅ Không có thay đổi, tiếp tục theo dõi...")
            else:
                print("❌ Không thể lấy dữ liệu từ API")
            
            print(f"⏳ Chờ 30 giây cho lần kiểm tra tiếp theo...\n")
            time.sleep(30)  # Wait 30 seconds before next check
            
    except KeyboardInterrupt:
        print("\n🛑 Bot đã được dừng bởi người dùng")
        print("👋 Tạm biệt!")

def main():
    """Main function"""
    print("🤖 BloxFruit Stock Monitor Bot")
    print("=" * 40)
    
    # Start continuous monitoring
    monitor_bloxfruit_stock()

if __name__ == "__main__":
    main()
