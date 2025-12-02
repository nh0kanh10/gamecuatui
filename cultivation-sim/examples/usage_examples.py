"""
Ví dụ sử dụng Artifacts, Items, Regional Cultures
Chạy file này để xem cách các hệ thống hoạt động
"""

from world_database import WorldDatabase
from artifact_system import ArtifactSystem
from item_system import ItemSystem


def example_items():
    """Ví dụ sử dụng Items"""
    print("=" * 60)
    print("VÍ DỤ: ITEMS")
    print("=" * 60)
    
    world_db = WorldDatabase("data")
    
    # 1. Lấy thông tin item
    item = world_db.get_item("pill_breakthrough_foundation")
    if item:
        print(f"\n✨ Nhặt được: {item['name']}")
        print(f"   Công dụng: {item['lore']}")
        print(f"   Hiệu ứng: {item['effect']}")
        print(f"   Độc tính: {item.get('toxicity', 0)}")
    
    # 2. Lấy tất cả pills
    print("\n📦 Tất cả Pills:")
    pills = world_db.get_items_by_type("Pill")
    for pill in pills:
        print(f"   - {pill['name']}: {pill['effect']['target']} +{pill['effect']['value']}")
    
    # 3. Lấy materials tại location
    print("\n🗻 Materials tại loc_mountain_02:")
    materials = world_db.get_materials_by_location("loc_mountain_02")
    for mat in materials:
        print(f"   - {mat['name']}: Grade {mat.get('grade', 1)}")
    
    # 4. Sử dụng Item System
    print("\n💊 Sử dụng Item:")
    item_system = ItemSystem(world_db)
    player_state = {
        "cultivation": {
            "spiritual_power": 50,
            "max_spiritual_power": 100
        }
    }
    result = item_system.use_item("pill_qi_gathering", player_state)
    print(f"   {result['message']}")
    print(f"   Effect: {result['effect_applied']}")
    print(f"   Toxicity: +{result['toxicity_added']}")


def example_artifacts():
    """Ví dụ sử dụng Artifacts"""
    print("\n" + "=" * 60)
    print("VÍ DỤ: ARTIFACTS")
    print("=" * 60)
    
    world_db = WorldDatabase("data")
    artifact_system = ArtifactSystem(world_db)
    
    # 1. Lấy thông tin artifact
    artifact = world_db.get_artifact("spirit_tool_fire_blade")
    if artifact:
        print(f"\n⚔️  Pháp bảo: {artifact['name']}")
        print(f"   Cấp bậc: {artifact['tier']}")
        print(f"   Yêu cầu: {artifact['realm_requirement']}")
        print(f"   Tấn công: {artifact['stats']['attack']}")
        print(f"   Lịch sử: {artifact['lore']}")
    
    # 2. Lấy artifacts theo tier
    print("\n🔮 Tất cả Spirit Tools:")
    spirit_tools = world_db.get_artifacts_by_tier("Spirit_Tool")
    for tool in spirit_tools:
        print(f"   - {tool['name']}: {tool['stats']['attack']} ATK")
    
    # 3. Tính damage
    print("\n💥 Tính Sát Thương:")
    player_stats = {
        "element": "Fire",
        "current_qi": 80,
        "max_qi": 100,
        "target_type": "normal"
    }
    damage_result = artifact_system.calculate_artifact_damage(
        player_stats=player_stats,
        artifact_id="spirit_tool_fire_blade",
        target_defense=20
    )
    print(f"   Tổng sát thương: {damage_result['total_damage']}")
    print(f"   Chi tiết: {damage_result['damage_breakdown']}")
    
    # 4. Check requirements
    print("\n✅ Kiểm tra Requirements:")
    check = world_db.check_artifact_requirements(
        artifact_id="magic_treasure_phoenix_blade",
        current_realm="Foundation",
        attributes={"INT": 50, "CON": 40}
    )
    if check["can_use"]:
        print("   ✓ Có thể sử dụng!")
    else:
        print(f"   ✗ Thiếu: {check['missing_requirements']}")


def example_regional_cultures():
    """Ví dụ sử dụng Regional Cultures"""
    print("\n" + "=" * 60)
    print("VÍ DỤ: REGIONAL CULTURES")
    print("=" * 60)
    
    world_db = WorldDatabase("data")
    
    # 1. Lấy văn hóa vùng
    culture = world_db.get_regional_culture("region_central_plains")
    if culture:
        print(f"\n🏛️  Vùng: {culture['name']}")
        print(f"   Không khí: {culture['vibe']}")
        print(f"   Quy tắc: {culture['social_rules']}")
        print(f"   Đặc điểm:")
        for trait in culture['cultural_traits']:
            print(f"      - {trait['effect']}")
    
    # 2. NPC behavior ở các vùng khác nhau
    print("\n👥 NPC Behavior:")
    
    regions = [
        ("region_central_plains", 100, "Foundation"),
        ("region_northern_tundra", 100, "Foundation"),
        ("region_northern_tundra", 1500, "Golden_Core"),
    ]
    
    for region_id, reputation, realm in regions:
        behavior = world_db.get_npc_behavior(
            region_id=region_id,
            player_reputation=reputation,
            player_realm=realm
        )
        region_name = world_db.get_regional_culture(region_id)['name']
        print(f"\n   {region_name} (Rep: {reputation}, Realm: {realm}):")
        print(f"      Thái độ: {behavior['attitude']}")
        print(f"      Cách chào: {behavior['greeting']}")
    
    # 3. Lấy văn hóa từ location
    print("\n📍 Văn hóa từ Location:")
    location_id = "loc_village_01"
    culture = world_db.get_culture_by_location(location_id)
    if culture:
        print(f"   Location: {location_id}")
        print(f"   Vùng: {culture['name']}")
        print(f"   Vibe: {culture['vibe']}")


def example_search():
    """Ví dụ tìm kiếm"""
    print("\n" + "=" * 60)
    print("VÍ DỤ: SEARCH")
    print("=" * 60)
    
    world_db = WorldDatabase("data")
    
    # Tìm kiếm theo tên
    results = world_db.search_by_name("rồng")
    
    print("\n🔍 Kết quả tìm kiếm 'rồng':")
    if results['artifacts']:
        print("   Artifacts:")
        for a in results['artifacts']:
            print(f"      - {a['name']}")
    if results['items']:
        print("   Items:")
        for i in results['items']:
            print(f"      - {i['name']}")


def example_integration():
    """Ví dụ tích hợp vào game logic"""
    print("\n" + "=" * 60)
    print("VÍ DỤ: INTEGRATION")
    print("=" * 60)
    
    world_db = WorldDatabase("data")
    artifact_system = ArtifactSystem(world_db)
    item_system = ItemSystem(world_db)
    
    # Scenario: Player ở Trung Châu, nhặt được Trúc Cơ Đan, dùng Hỏa Diễm Đao
    print("\n📖 Scenario: Player ở Trung Châu")
    
    # 1. Get location culture
    location_id = "loc_village_01"
    culture = world_db.get_culture_by_location(location_id)
    if culture:
        print(f"   Bạn đang ở: {culture['name']} - {culture['vibe']}")
    
    # 2. NPC behavior
    behavior = world_db.get_npc_behavior(
        region_id="region_central_plains",
        player_reputation=100,
        player_realm="Foundation"
    )
    print(f"   NPC sẽ: {behavior['attitude']} - {behavior['greeting']}")
    
    # 3. Player nhặt item
    item = world_db.get_item("pill_breakthrough_foundation")
    if item:
        print(f"\n   ✨ Nhặt được: {item['name']}")
        print(f"      {item['lore']}")
    
    # 4. Player dùng artifact
    player_stats = {
        "element": "Fire",
        "current_qi": 80,
        "max_qi": 100
    }
    damage = artifact_system.calculate_artifact_damage(
        player_stats=player_stats,
        artifact_id="spirit_tool_fire_blade",
        target_defense=20
    )
    print(f"\n   ⚔️  Tấn công với Hỏa Diễm Đao: {damage['total_damage']} dmg")
    print(f"      {damage['damage_breakdown']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("VÍ DỤ SỬ DỤNG: ARTIFACTS, ITEMS, REGIONAL CULTURES")
    print("=" * 60)
    
    try:
        example_items()
        example_artifacts()
        example_regional_cultures()
        example_search()
        example_integration()
        
        print("\n" + "=" * 60)
        print("✅ HOÀN THÀNH!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

