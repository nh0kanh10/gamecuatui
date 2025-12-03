"""
Test Simple vs Complex Approach
So sánh:
1. Simple: Chỉ Gemini + basic prompt
2. Complex: Full stack với Memory, ECS, World Database, etc.

Mục đích: Xem những layer phức tạp có đáng giá không
"""

import asyncio
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
from typing import Dict, Any

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================
# 1. SIMPLE APPROACH - Chỉ Gemini + Basic Prompt
# ============================================

class SimpleGame:
    """
    Chỉ dùng Gemini API trực tiếp
    Không có Memory, ECS, Database gì cả
    """
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.conversation_history = []
        self.character_data = {
            "name": "Test Character",
            "age": 0,
            "gender": "Nam",
            "talent": "Bình thường"
        }
    
    def create_character(self) -> str:
        prompt = f"""
Bạn là storyteller cho game tu tiên.
Tạo background cho nhân vật:
- Tên: {self.character_data['name']}
- Tuổi: {self.character_data['age']}
- Giới tính: {self.character_data['gender']}
- Thiên phú: {self.character_data['talent']}

Viết câu chuyện ngắn về lúc sinh ra và cho 4 lựa chọn cho năm tiếp theo.

Format:
STORY: <câu chuyện>
CHOICES:
1. <lựa chọn 1>
2. <lựa chọn 2>
3. <lựa chọn 3>
4. <lựa chọn 4>
"""
        response = self.model.generate_content(prompt)
        result = response.text
        self.conversation_history.append({"role": "assistant", "content": result})
        return result
    
    def process_choice(self, choice_text: str) -> str:
        # Chỉ append vào lịch sử và gửi lại cho Gemini
        self.conversation_history.append({"role": "user", "content": choice_text})
        self.character_data["age"] += 1
        
        # Build context từ lịch sử
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-5:]])
        
        prompt = f"""
Nhân vật đã chọn: {choice_text}
Tuổi hiện tại: {self.character_data['age']}

Lịch sử gần đây:
{context}

Tiếp tục câu chuyện và cho 4 lựa chọn mới.

Format:
STORY: <câu chuyện>
CHOICES:
1. <lựa chọn 1>
2. <lựa chọn 2>
3. <lựa chọn 3>
4. <lựa chọn 4>
"""
        response = self.model.generate_content(prompt)
        result = response.text
        self.conversation_history.append({"role": "assistant", "content": result})
        return result


# ============================================
# 2. COMPLEX APPROACH - Full Stack
# ============================================

class ComplexGame:
    """
    Dùng toàn bộ stack:
    - CultivationAgent (với system prompt phức tạp)
    - Memory3Tier
    - ECS Systems
    - World Database
    - Advanced Systems
    """
    def __init__(self):
        from game import CultivationSimulator
        self.game = CultivationSimulator(save_id="test_complex")
    
    def create_character(self) -> Dict[str, Any]:
        result = self.game.character_creation(
            gender="Nam",
            talent="Bình thường",
            race="Người",
            background="Nông dân"
        )
        return result
    
    def process_choice(self, choice_index: int) -> Dict[str, Any]:
        result = self.game.process_year_turn(choice_index)
        return result


# ============================================
# 3. TEST & COMPARISON
# ============================================

async def test_simple_approach():
    """Test simple approach"""
    print("\n" + "="*60)
    print("🔵 TESTING SIMPLE APPROACH")
    print("="*60 + "\n")
    
    game = SimpleGame()
    
    # Character creation
    start = time.time()
    response = game.create_character()
    char_time = time.time() - start
    
    print("📝 Character Creation Response:")
    print(response[:300] + "..." if len(response) > 300 else response)
    print(f"\n⏱️  Time: {char_time:.2f}s")
    
    # Process 3 turns
    turn_times = []
    for i in range(3):
        start = time.time()
        response = game.process_choice(f"Lựa chọn {i+1}")
        turn_time = time.time() - start
        turn_times.append(turn_time)
        
        print(f"\n📖 Turn {i+1} Response:")
        print(response[:200] + "..." if len(response) > 200 else response)
        print(f"⏱️  Time: {turn_time:.2f}s")
    
    avg_turn_time = sum(turn_times) / len(turn_times)
    
    return {
        "char_creation_time": char_time,
        "avg_turn_time": avg_turn_time,
        "total_time": char_time + sum(turn_times),
        "conversation_length": len(game.conversation_history)
    }


async def test_complex_approach():
    """Test complex approach"""
    print("\n" + "="*60)
    print("🔴 TESTING COMPLEX APPROACH")
    print("="*60 + "\n")
    
    game = ComplexGame()
    
    # Character creation
    start = time.time()
    response = game.create_character()
    char_time = time.time() - start
    
    print("📝 Character Creation Response:")
    print(f"Name: {response.get('character_name')}")
    print(f"Story: {response.get('narrative', '')[:300]}...")
    print(f"Choices: {len(response.get('choices', []))} choices")
    print(f"\n⏱️  Time: {char_time:.2f}s")
    
    # Check what systems are active
    print("\n🔧 Active Systems:")
    print(f"  - Agent: {'✅' if game.game.agent else '❌'}")
    print(f"  - Memory: {'✅' if game.game.memory else '❌'}")
    print(f"  - World DB: {'✅' if game.game.world_db else '❌'}")
    print(f"  - ECS Systems: {'✅' if game.game.cultivation_system else '❌'}")
    print(f"  - Attributes: {game.game.attributes.dict() if game.game.attributes else '❌'}")
    print(f"  - Resources: {game.game.resources.dict()}")
    
    # Process 3 turns
    turn_times = []
    for i in range(3):
        start = time.time()
        response = game.process_choice(0)  # Always choose first option
        turn_time = time.time() - start
        turn_times.append(turn_time)
        
        print(f"\n📖 Turn {i+1} Response:")
        print(f"Age: {response.get('age')}")
        print(f"Story: {response.get('narrative', '')[:200]}...")
        print(f"Choices: {len(response.get('choices', []))} choices")
        print(f"⏱️  Time: {turn_time:.2f}s")
    
    avg_turn_time = sum(turn_times) / len(turn_times)
    
    # Get memory stats
    memory_count = 0
    try:
        cursor = game.game.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_short_term")
        memory_count = cursor.fetchone()[0]
    except:
        pass
    
    return {
        "char_creation_time": char_time,
        "avg_turn_time": avg_turn_time,
        "total_time": char_time + sum(turn_times),
        "memory_entries": memory_count,
        "has_attributes": game.game.attributes is not None,
        "ecs_active": game.game.cultivation_system is not None
    }


async def compare_results(simple_results: Dict, complex_results: Dict):
    """So sánh kết quả"""
    print("\n" + "="*60)
    print("📊 COMPARISON RESULTS")
    print("="*60 + "\n")
    
    print("⏱️  PERFORMANCE:")
    print(f"  Simple  - Char Creation: {simple_results['char_creation_time']:.2f}s")
    print(f"  Complex - Char Creation: {complex_results['char_creation_time']:.2f}s")
    print(f"  Difference: {complex_results['char_creation_time'] - simple_results['char_creation_time']:.2f}s slower")
    
    print(f"\n  Simple  - Avg Turn: {simple_results['avg_turn_time']:.2f}s")
    print(f"  Complex - Avg Turn: {complex_results['avg_turn_time']:.2f}s")
    print(f"  Difference: {complex_results['avg_turn_time'] - simple_results['avg_turn_time']:.2f}s slower")
    
    print(f"\n  Simple  - Total: {simple_results['total_time']:.2f}s")
    print(f"  Complex - Total: {complex_results['total_time']:.2f}s")
    overhead = ((complex_results['total_time'] - simple_results['total_time']) / simple_results['total_time']) * 100
    print(f"  Overhead: {overhead:.1f}%")
    
    print("\n📦 FEATURES:")
    print(f"  Simple  - Conversation History: {simple_results['conversation_length']} entries")
    print(f"  Complex - Memory Entries: {complex_results['memory_entries']} entries")
    print(f"  Complex - Attributes System: {'✅' if complex_results['has_attributes'] else '❌'}")
    print(f"  Complex - ECS Systems: {'✅' if complex_results['ecs_active'] else '❌'}")
    
    print("\n💡 VERDICT:")
    if overhead < 20:
        print("  ✅ Complex approach chỉ chậm hơn <20% - WORTH IT nếu cần features")
    elif overhead < 50:
        print("  ⚠️  Complex approach chậm hơn 20-50% - CÂN NHẮC lại")
    else:
        print("  ❌ Complex approach quá chậm (>50%) - NÊN SIMPLIFY")
    
    print("\n🤔 QUESTIONS TO ASK:")
    print("  1. Bạn có thực sự cần Memory system không?")
    print("     → Nếu chỉ test ngắn (vài turn), simple approach đủ")
    print("     → Nếu chơi dài (100+ turns), memory giúp AI nhớ context")
    
    print("\n  2. Bạn có cần ECS Systems không?")
    print("     → Nếu chỉ cần story, không cần")
    print("     → Nếu cần cultivation progress, stats, relationships → cần")
    
    print("\n  3. Bạn có cần World Database không?")
    print("     → Nếu AI tự generate mọi thứ → không cần")
    print("     → Nếu cần consistency (locations, sects, NPCs) → cần")
    
    print("\n  4. Response quality có khác biệt không?")
    print("     → Xem output phía trên và tự đánh giá!")


async def main():
    """Main test runner"""
    print("\n🧪 TESTING: Simple vs Complex Approach")
    print("Goal: Xem complex stack có đáng công sức không\n")
    
    try:
        # Test simple
        simple_results = await test_simple_approach()
        
        # Test complex
        complex_results = await test_complex_approach()
        
        # Compare
        await compare_results(simple_results, complex_results)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
