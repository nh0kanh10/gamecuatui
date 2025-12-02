#!/usr/bin/env python3
"""
Automated benchmark sweep - test all recommended configurations
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict
import time

# Test configurations
CONFIGS = [
    # Phi-3-mini tests
    {
        "model": "models/phi-3-mini-4k-q4.gguf",
        "name": "Phi3_CPU",
        "n_gpu_layers": 0,
        "n_threads": 8,
        "n_ctx": 2048
    },
    {
        "model": "models/phi-3-mini-4k-q4.gguf",
        "name": "Phi3_4GPU",
        "n_gpu_layers": 4,
        "n_threads": 8,
        "n_ctx": 2048
    },
    {
        "model": "models/phi-3-mini-4k-q4.gguf",
        "name": "Phi3_8GPU",
        "n_gpu_layers": 8,
        "n_threads": 8,
        "n_ctx": 2048
    },
    
    # Llama-3.2-3B tests
    {
        "model": "models/llama-3.2-3b-q4.gguf",
        "name": "Llama32_CPU",
        "n_gpu_layers": 0,
        "n_threads": 8,
        "n_ctx": 2048
    },
    {
        "model": "models/llama-3.2-3b-q4.gguf",
        "name": "Llama32_8GPU",
        "n_gpu_layers": 8,
        "n_threads": 8,
        "n_ctx": 2048
    },
    
    # Mistral-7B tests
    {
        "model": "models/mistral-7b-q4.gguf",
        "name": "Mistral7B_CPU",
        "n_gpu_layers": 0,
        "n_threads": 8,
        "n_ctx": 2048
    },
    {
        "model": "models/mistral-7b-q4.gguf",
        "name": "Mistral7B_4GPU",
        "n_gpu_layers": 4,
        "n_threads": 8,
        "n_ctx": 2048
    }
]


def run_single_benchmark(config: Dict) -> bool:
    """Run a single benchmark configuration"""
    model_path = Path(config['model'])
    
    if not model_path.exists():
        print(f"⏭️  Skipping {config['name']} - model not found: {model_path}")
        return False
    
    cmd = [
        "python",
        "benchmarks/benchmark_inference.py",
        "--model", str(model_path),
        "--n_gpu_layers", str(config['n_gpu_layers']),
        "--n_threads", str(config['n_threads']),
        "--n_ctx", str(config['n_ctx']),
        "--test_name", config['name']
    ]
    
    print(f"\n{'='*70}")
    print(f"🚀 Running: {config['name']}")
    print(f"   Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Benchmark failed: {e}")
        return False


def generate_comparison_report(results_dir: Path):
    """Generate comparison table from all results"""
    results = []
    
    for json_file in results_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except:
            continue
    
    if not results:
        print("\n⚠️  No results found to compare")
        return
    
    # Sort by timestamp
    results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Generate markdown table
    report = []
    report.append("\n# Benchmark Comparison Report\n")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    report.append("## Summary Table\n")
    report.append("| Test Name | Model | GPU Layers | Avg t/s | Latency (ms) | VRAM (MB) | RAM (MB) | Verdict |\n")
    report.append("|-----------|-------|------------|---------|--------------|-----------|----------|----------|\n")
    
    for r in results:
        metrics = r.get('metrics', {})
        config = r.get('config', {})
        
        tps = metrics.get('avg_tokens_per_second', 0)
        latency = metrics.get('avg_latency_ms', 0)
        vram = metrics.get('max_vram_mb', 0)
        ram = metrics.get('max_ram_mb', 0)
        
        # Determine verdict
        if tps >= 4:
            verdict = "✅ Excellent"
        elif tps >= 3:
            verdict = "✅ Good"
        elif tps >= 2:
            verdict = "⚠️ Marginal"
        else:
            verdict = "❌ Poor"
        
        report.append(f"| {r['test_name']} | {r['model']} | {config.get('n_gpu_layers', 0)} | "
                     f"{tps:.2f} | {latency:.1f} | {vram:.0f} | {ram:.0f} | {verdict} |\n")
    
    # Add recommendations
    report.append("\n## Recommendations\n\n")
    
    # Find best config
    best = max(results, key=lambda x: x.get('metrics', {}).get('avg_tokens_per_second', 0))
    best_tps = best.get('metrics', {}).get('avg_tokens_per_second', 0)
    
    report.append(f"### 🏆 Best Configuration\n")
    report.append(f"- **Test**: {best['test_name']}\n")
    report.append(f"- **Model**: {best['model']}\n")
    report.append(f"- **Speed**: {best_tps:.2f} tokens/second\n")
    report.append(f"- **VRAM**: {best.get('metrics', {}).get('max_vram_mb', 0):.0f} MB\n\n")
    
    report.append(f"### 💡 Implementation Guidance\n\n")
    
    if best_tps >= 3:
        report.append(f"✅ **Recommended for production**: This configuration provides acceptable performance for real-time text adventure gameplay.\n\n")
    else:
        report.append(f"⚠️ **Consider alternatives**: Performance may be too slow for smooth gameplay. Consider:\n")
        report.append(f"- Using smaller model for parsing, larger for narrative generation\n")
        report.append(f"- Pre-generating content offline\n")
        report.append(f"- Showing typing animation to mask latency\n\n")
    
    # Save report
    report_path = results_dir / "COMPARISON_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"\n{'='*70}")
    print(f"📊 Comparison report generated: {report_path}")
    print(f"{'='*70}\n")
    
    # Print report to console
    print(''.join(report))


def main():
    print(f"""
{'='*70}
🔬 AUTOMATED BENCHMARK SWEEP
{'='*70}

This will test multiple model + configuration combinations.
Results will be saved to: benchmarks/results/

Estimated time: 5-10 minutes per configuration
Total configurations: {len(CONFIGS)}

""")
    
    input("Press Enter to start (or Ctrl+C to cancel)...")
    
    successful = 0
    failed = 0
    skipped = 0
    
    start_time = time.time()
    
    for i, config in enumerate(CONFIGS, 1):
        print(f"\n\n{'#'*70}")
        print(f"# TEST {i}/{len(CONFIGS)}")
        print(f"{'#'*70}")
        
        result = run_single_benchmark(config)
        
        if result is None:
            skipped += 1
        elif result:
            successful += 1
        else:
            failed += 1
        
        # Cool down between tests
        if i < len(CONFIGS):
            print("\n⏳ Cooling down for 5 seconds...")
            time.sleep(5)
    
    elapsed = time.time() - start_time
    
    print(f"\n\n{'='*70}")
    print(f"🎉 SWEEP COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"{'='*70}\n")
    
    # Generate comparison report
    results_dir = Path("benchmarks/results")
    if results_dir.exists():
        generate_comparison_report(results_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Sweep cancelled by user")
