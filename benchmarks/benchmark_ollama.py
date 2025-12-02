#!/usr/bin/env python3
"""
Benchmark for Ollama - simpler and faster than llama.cpp
Uses Ollama's Python SDK to test local models
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import ollama
    import psutil
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install ollama psutil")
    sys.exit(1)

# Optional GPU monitoring
try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    print("⚠️  GPUtil not found, VRAM monitoring disabled")


def get_vram_usage() -> float:
    """Get current VRAM usage in MB"""
    if not HAS_GPU:
        return 0.0
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].memoryUsed
    except:
        pass
    return 0.0


def get_ram_usage() -> float:
    """Get current process RAM usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def list_available_models() -> List[str]:
    """List all Ollama models"""
    try:
        models = ollama.list()
        return [m['name'] for m in models['models']]
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        print("Make sure Ollama is running: ollama serve")
        return []


def run_benchmark(
    model_name: str,
    test_name: str = "ollama_benchmark"
) -> Dict[str, Any]:
    """Run complete benchmark suite with Ollama"""
    
    print(f"\n{'='*60}")
    print(f"🔬 Benchmark: {test_name}")
    print(f"{'='*60}")
    print(f"Model: {model_name}")
    print(f"Backend: Ollama")
    print(f"{'='*60}\n")
    
    # Test prompts - same as llama.cpp version for comparison
    test_prompts = [
        {
            "name": "Short Context",
            "prompt": "Describe a mysterious dungeon entrance in vivid detail.",
            "max_tokens": 100
        },
        {
            "name": "Medium Context",
            "prompt": """You are a game master. A player enters a dark forest at night.
They see: old oak trees, mist, distant howling.
They carry: rusty sword, torch, leather armor.
Describe what happens next in 2-3 paragraphs.""",
            "max_tokens": 150
        },
        {
            "name": "Long Context",
            "prompt": """You are running a text adventure game.

PLAYER STATE:
- Name: Aria
- HP: 45/100
- Items: Health Potion, Ancient Map, Silver Dagger
- Location: Abandoned Temple Entrance
- Quest: Find the Crystal of Eternal Light

WORLD STATE:
- Weather: Heavy rain
- Time: Midnight
- Nearby: Crumbling stone pillars, overgrown vines, locked iron gate
- Sounds: Thunder, dripping water, faint chanting from below

The player says: "I examine the iron gate carefully."

Respond with a detailed description and possible actions.""",
            "max_tokens": 200
        }
    ]
    
    results = []
    
    # Warm up
    print("🔥 Warming up model...")
    try:
        ollama.generate(model=model_name, prompt="Hello", options={"num_predict": 10})
        print("   ✅ Model loaded\n")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return {"error": str(e)}
    
    # Run tests
    for test in test_prompts:
        print(f"🧪 Test: {test['name']}")
        print(f"   Prompt length: {len(test['prompt'])} chars")
        
        vram_start = get_vram_usage()
        ram_start = get_ram_usage()
        
        start_time = time.time()
        
        try:
            response = ollama.generate(
                model=model_name,
                prompt=test['prompt'],
                options={
                    "num_predict": test['max_tokens'],
                    "temperature": 0.7
                }
            )
            
            elapsed = time.time() - start_time
            vram_peak = get_vram_usage()
            ram_peak = get_ram_usage()
            
            # Extract metrics from response
            output_text = response['response']
            
            # Estimate tokens (rough: ~4 chars per token)
            tokens_generated = len(output_text) // 4
            if tokens_generated == 0:
                tokens_generated = 1  # Avoid division by zero
            
            tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0
            avg_latency = (elapsed * 1000) / tokens_generated
            
            result = {
                "test_name": test['name'],
                "prompt_length": len(test['prompt']),
                "tokens_generated": tokens_generated,
                "time_seconds": round(elapsed, 2),
                "tokens_per_second": round(tokens_per_sec, 2),
                "avg_latency_ms": round(avg_latency, 1),
                "vram_mb": round(vram_peak, 0),
                "ram_mb": round(ram_peak, 0),
                "output_preview": output_text[:100] + "..."
            }
            
            results.append(result)
            
            # Print results
            print(f"   ✅ Tokens: ~{tokens_generated} | Speed: {tokens_per_sec:.2f} t/s | Latency: {avg_latency:.0f}ms")
            print(f"   VRAM: {vram_peak:.0f}MB | RAM: {ram_peak:.0f}MB")
            print(f"   Output: {result['output_preview']}\n")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}\n")
            continue
        
        time.sleep(1)  # Cool down
    
    if not results:
        return {"error": "All tests failed"}
    
    # Calculate averages
    avg_tps = sum(r['tokens_per_second'] for r in results) / len(results)
    avg_latency = sum(r['avg_latency_ms'] for r in results) / len(results)
    max_vram = max(r['vram_mb'] for r in results)
    max_ram = max(r['ram_mb'] for r in results)
    
    summary = {
        "test_name": test_name,
        "model": model_name,
        "backend": "ollama",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "avg_tokens_per_second": round(avg_tps, 2),
            "avg_latency_ms": round(avg_latency, 1),
            "max_vram_mb": max_vram,
            "max_ram_mb": max_ram
        },
        "detailed_results": results
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {test_name}")
    print(f"{'='*60}")
    print(f"Average Speed:    {avg_tps:.2f} tokens/second")
    print(f"Average Latency:  {avg_latency:.0f} ms/token")
    print(f"Peak VRAM:        {max_vram:.0f} MB")
    print(f"Peak RAM:         {max_ram:.0f} MB")
    
    # Verdict
    print(f"\n🎯 VERDICT:")
    if avg_tps >= 4:
        print(f"   ✅ EXCELLENT - Suitable for real-time text adventure")
    elif avg_tps >= 3:
        print(f"   ✅ GOOD - Acceptable for text adventure")
    elif avg_tps >= 2:
        print(f"   ⚠️  MARGINAL - Usable but noticeable delay")
    else:
        print(f"   ❌ POOR - Too slow for interactive gameplay")
    
    print(f"{'='*60}\n")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Benchmark Ollama models")
    parser.add_argument("--model", help="Ollama model name (e.g., phi3:3.8b)")
    parser.add_argument("--test_name", help="Name for this test run")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available models and exit")
    
    args = parser.parse_args()
    
    # List models if requested
    if args.list:
        print("\n📦 Available Ollama models:\n")
        models = list_available_models()
        if models:
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
            print(f"\nTo benchmark: python benchmark_ollama.py --model {models[0]}")
        else:
            print("  No models found. Install with: ollama pull phi3:3.8b")
        return
    
    if not args.model:
        print("❌ --model required. Use --list to see available models")
        sys.exit(1)
    
    test_name = args.test_name or f"{args.model.replace(':', '_')}"
    
    # Run benchmark
    results = run_benchmark(
        model_name=args.model,
        test_name=test_name
    )
    
    if "error" in results:
        print(f"❌ Benchmark failed: {results['error']}")
        sys.exit(1)
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{test_name}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
