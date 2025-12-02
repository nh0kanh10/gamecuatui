#!/usr/bin/env python3
"""
Benchmark script for LLM inference performance testing
Measures: tokens/s, latency, VRAM, RAM usage
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any

try:
    from llama_cpp import Llama
    import psutil
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install llama-cpp-python psutil")
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


def run_benchmark(
    model_path: str,
    n_gpu_layers: int = 0,
    n_ctx: int = 2048,
    n_threads: int = 8,
    test_name: str = "benchmark"
) -> Dict[str, Any]:
    """Run complete benchmark suite"""
    
    print(f"\n{'='*60}")
    print(f"🔬 Benchmark: {test_name}")
    print(f"{'='*60}")
    print(f"Model: {Path(model_path).name}")
    print(f"Config: n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx}, n_threads={n_threads}")
    print(f"{'='*60}\n")
    
    # Initialize model
    print("📦 Loading model...")
    ram_before = get_ram_usage()
    vram_before = get_vram_usage()
    
    load_start = time.time()
    try:
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return {"error": str(e)}
    
    load_time = time.time() - load_start
    ram_after = get_ram_usage()
    vram_after = get_vram_usage()
    
    print(f"✅ Model loaded in {load_time:.2f}s")
    print(f"   RAM used: {ram_after - ram_before:.0f} MB")
    print(f"   VRAM used: {vram_after - vram_before:.0f} MB\n")
    
    # Test prompts
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
    
    for test in test_prompts:
        print(f"🧪 Test: {test['name']}")
        print(f"   Prompt length: {len(test['prompt'])} chars")
        
        # Warm up
        if results == []:  # Only first time
            print("   Warming up...")
            llm(test['prompt'], max_tokens=10, echo=False)
        
        # Actual test
        start_time = time.time()
        vram_start = get_vram_usage()
        ram_start = get_ram_usage()
        
        output = llm(
            test['prompt'],
            max_tokens=test['max_tokens'],
            temperature=0.7,
            echo=False
        )
        
        elapsed = time.time() - start_time
        vram_peak = get_vram_usage()
        ram_peak = get_ram_usage()
        
        # Extract metrics
        tokens_generated = output['usage']['completion_tokens']
        tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0
        avg_latency = (elapsed * 1000) / tokens_generated if tokens_generated > 0 else 0
        
        result = {
            "test_name": test['name'],
            "prompt_length": len(test['prompt']),
            "tokens_generated": tokens_generated,
            "time_seconds": round(elapsed, 2),
            "tokens_per_second": round(tokens_per_sec, 2),
            "avg_latency_ms": round(avg_latency, 1),
            "vram_mb": round(vram_peak, 0),
            "ram_mb": round(ram_peak, 0),
            "output_preview": output['choices'][0]['text'][:100] + "..."
        }
        
        results.append(result)
        
        # Print results
        print(f"   ✅ Tokens: {tokens_generated} | Speed: {tokens_per_sec:.2f} t/s | Latency: {avg_latency:.0f}ms")
        print(f"   VRAM: {vram_peak:.0f}MB | RAM: {ram_peak:.0f}MB")
        print(f"   Output: {result['output_preview']}\n")
        
        time.sleep(1)  # Cool down
    
    # Calculate averages
    avg_tps = sum(r['tokens_per_second'] for r in results) / len(results)
    avg_latency = sum(r['avg_latency_ms'] for r in results) / len(results)
    max_vram = max(r['vram_mb'] for r in results)
    max_ram = max(r['ram_mb'] for r in results)
    
    summary = {
        "test_name": test_name,
        "model": Path(model_path).name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {
            "n_gpu_layers": n_gpu_layers,
            "n_ctx": n_ctx,
            "n_threads": n_threads
        },
        "load_time_seconds": round(load_time, 2),
        "model_ram_mb": round(ram_after - ram_before, 0),
        "model_vram_mb": round(vram_after - vram_before, 0),
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
    
    if max_vram > 3500:
        print(f"   ⚠️  VRAM WARNING - May cause OOM on 4GB GPU")
    
    if max_ram > 20000:
        print(f"   ⚠️  RAM WARNING - May impact system stability")
    
    print(f"{'='*60}\n")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Benchmark LLM inference performance")
    parser.add_argument("--model", required=True, help="Path to GGUF model file")
    parser.add_argument("--n_gpu_layers", type=int, default=0, help="Number of layers to offload to GPU")
    parser.add_argument("--n_ctx", type=int, default=2048, help="Context window size")
    parser.add_argument("--n_threads", type=int, default=8, help="Number of CPU threads")
    parser.add_argument("--test_name", default="benchmark", help="Name for this test run")
    parser.add_argument("--output", default="results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Validate model exists
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print(f"\nRun: python download_models.py")
        sys.exit(1)
    
    # Run benchmark
    results = run_benchmark(
        model_path=str(model_path),
        n_gpu_layers=args.n_gpu_layers,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        test_name=args.test_name
    )
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{args.test_name}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
