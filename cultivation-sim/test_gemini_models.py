"""
Test script để kiểm tra các Gemini models có thể dùng được
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment")
    exit(1)

genai.configure(api_key=api_key)

# Danh sách models để test (từ free tier đến paid)
models_to_test = [
    "gemini-1.5-flash",           # Free tier, fast
    "gemini-1.5-pro",             # Free tier, better quality
    "gemini-1.5-flash-latest",    # Latest flash
    "gemini-1.5-pro-latest",      # Latest pro
    "gemini-2.0-flash-exp",       # Experimental (có thể hết quota)
    "gemini-pro",                 # Legacy
]

def test_model(model_name):
    """Test một model cụ thể"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")
    
    try:
        # Tạo model
        model = genai.GenerativeModel(model_name)
        
        # Test với prompt ngắn
        test_prompt = "Say 'Hello' in Vietnamese"
        
        print(f"📤 Sending test prompt...")
        start_time = time.time()
        
        response = model.generate_content(test_prompt)
        
        elapsed = time.time() - start_time
        
        text = response.text.strip()
        
        print(f"✅ SUCCESS!")
        print(f"   Response: {text[:100]}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Model available: ✅")
        
        # Get model info
        try:
            model_info = genai.get_model(model_name)
            print(f"   Display name: {model_info.display_name}")
            print(f"   Description: {model_info.description[:100] if model_info.description else 'N/A'}")
        except:
            pass
        
        return True, elapsed
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ FAILED!")
        print(f"   Error: {error_str[:200]}")
        
        if "429" in error_str or "quota" in error_str.lower():
            print(f"   Reason: Quota/Rate limit exceeded")
        elif "404" in error_str or "not found" in error_str.lower():
            print(f"   Reason: Model not found/not available")
        else:
            print(f"   Reason: {error_str[:100]}")
        
        return False, None

def main():
    print("🔍 Testing Gemini Models Availability")
    print("=" * 60)
    
    results = {}
    
    for model_name in models_to_test:
        success, elapsed = test_model(model_name)
        results[model_name] = {
            "available": success,
            "response_time": elapsed
        }
        time.sleep(1)  # Rate limit protection
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    available_models = [m for m, r in results.items() if r["available"]]
    unavailable_models = [m for m, r in results.items() if not r["available"]]
    
    print(f"\n✅ Available Models ({len(available_models)}):")
    for model in available_models:
        elapsed = results[model]["response_time"]
        print(f"   - {model} ({elapsed:.2f}s)")
    
    print(f"\n❌ Unavailable Models ({len(unavailable_models)}):")
    for model in unavailable_models:
        print(f"   - {model}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if available_models:
        fastest = min(available_models, key=lambda m: results[m]["response_time"] or float('inf'))
        print(f"   - Fastest: {fastest} ({results[fastest]['response_time']:.2f}s)")
        
        if "gemini-1.5-flash" in available_models:
            print(f"   - Recommended for free tier: gemini-1.5-flash (fast, free)")
        if "gemini-1.5-pro" in available_models:
            print(f"   - Recommended for quality: gemini-1.5-pro (better quality, free)")
        
        print(f"\n   Add to .env file:")
        print(f"   GEMINI_MODEL={fastest}")
    else:
        print(f"   ⚠️ No models available! Check your API key and quota.")

if __name__ == "__main__":
    main()

