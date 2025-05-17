#!/usr/bin/env python3
"""
Performance benchmarking for the formal verification service.
"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add the project root to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.policy_service.app.services.formal_verification_service import FormalVerificationService
from services.policy_service.app.core.config import settings

# Configuration
TEST_DATA_DIR = Path(__file__).parent.parent / "tests" / "test_data"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class BenchmarkResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.execution_times: List[float] = []
        self.memory_usage: List[float] = []  # In MB
        self.success_count = 0
        self.failure_count = 0
        self.error_messages: List[str] = []
    
    def add_result(self, execution_time: float, memory_usage: float, success: bool, error: str = None):
        self.execution_times.append(execution_time)
        self.memory_usage.append(memory_usage)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            if error:
                self.error_messages.append(error)
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.execution_times:
            return {}
            
        return {
            "test_name": self.test_name,
            "total_runs": len(self.execution_times),
            "success_rate": self.success_count / len(self.execution_times) * 100,
            "avg_time_ms": statistics.mean(self.execution_times) * 1000,
            "min_time_ms": min(self.execution_times) * 1000,
            "max_time_ms": max(self.execution_times) * 1000,
            "p50_ms": statistics.median(self.execution_times) * 1000,
            "p95_ms": statistics.quantiles(self.execution_times, n=20)[-1] * 1000,
            "p99_ms": statistics.quantiles(self.execution_times, n=100)[-1] * 1000,
            "avg_memory_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
            "error_count": self.failure_count,
            "error_messages": list(set(self.error_messages))  # Unique errors
        }

async def measure_memory() -> float:
    """Get current process memory usage in MB."""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

async def load_test_policies() -> Dict[str, Dict]:
    """Load test policies from the test data directory."""
    policies = {}
    for policy_file in TEST_DATA_DIR.glob("*.json"):
        with open(policy_file, 'r') as f:
            policy = json.load(f)
            test_name = policy_file.stem
            policies[test_name] = policy
    return policies

async def run_verification_benchmark(
    fv_service: FormalVerificationService,
    policy: Dict[str, Any],
    iterations: int = 10
) -> BenchmarkResult:
    """Run benchmark for a single policy."""
    test_name = policy.get("metadata", {}).get("test_case", "unknown")
    result = BenchmarkResult(test_name)
    
    for i in range(iterations):
        try:
            # Measure memory before
            mem_before = await measure_memory()
            
            # Run verification
            start_time = time.perf_counter()
            verification_result = await fv_service.verify_policy(policy)
            end_time = time.perf_counter()
            
            # Measure memory after
            mem_after = await measure_memory()
            
            # Calculate metrics
            execution_time = end_time - start_time
            memory_usage = mem_after - mem_before
            
            # Check if verification was successful
            success = verification_result.get("status") == "SATISFIABLE"
            error_msg = verification_result.get("error") if not success else None
            
            result.add_result(execution_time, memory_usage, success, error_msg)
            
        except Exception as e:
            result.add_result(0, 0, False, str(e))
    
    return result

async def run_benchmarks():
    """Run all benchmarks and generate reports."""
    print("Starting formal verification benchmarks...")
    
    # Initialize the formal verification service
    fv_service = FormalVerificationService()
    
    # Load test policies
    policies = await load_test_policies()
    if not policies:
        print("No test policies found. Please generate test policies first.")
        return
    
    # Run benchmarks for each policy
    all_results = {}
    for test_name, policy in policies.items():
        print(f"\nRunning benchmark for: {test_name}")
        result = await run_verification_benchmark(fv_service, policy, iterations=10)
        all_results[test_name] = result
    
    # Generate reports
    await generate_reports(all_results)

async def generate_reports(results: Dict[str, BenchmarkResult]):
    """Generate benchmark reports and visualizations."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = RESULTS_DIR / f"benchmark_{timestamp}"
    report_dir.mkdir(exist_ok=True)
    
    # Generate CSV report
    csv_data = []
    for test_name, result in results.items():
        stats = result.get_stats()
        if stats:
            csv_data.append(stats)
    
    if csv_data:
        df = pd.DataFrame(csv_data)
        csv_path = report_dir / "benchmark_results.csv"
        df.to_csv(csv_path, index=False)
        
        # Generate summary markdown
        markdown_path = report_dir / "README.md"
        with open(markdown_path, 'w') as f:
            f.write("# Formal Verification Benchmark Results\n\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
            
            # Summary table
            f.write("## Summary\n\n")
            f.write(df.to_markdown(index=False, floatfmt=".2f"))
            f.write("\n\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            for _, row in df.iterrows():
                f.write(f"### {row['test_name']}\n")
                f.write(f"- **Success Rate**: {row['success_rate']:.2f}%\n")
                f.write(f"- **Avg Time**: {row['avg_time_ms']:.2f} ms\n")
                f.write(f"- **P95 Time**: {row['p95_ms']:.2f} ms\n")
                f.write(f"- **Avg Memory**: {row['avg_memory_mb']:.2f} MB\n")
                
                if row['error_count'] > 0:
                    f.write(f"- **Errors**: {row['error_count']} failures\n")
                    for error in row['error_messages']:
                        f.write(f"  - `{error}`\n")
                f.write("\n")
        
        # Generate plots
        plt.figure(figsize=(12, 6))
        
        # Execution time plot
        plt.subplot(1, 2, 1)
        df_sorted = df.sort_values('avg_time_ms', ascending=False)
        plt.bar(df_sorted['test_name'], df_sorted['avg_time_ms'])
        plt.xticks(rotation=45, ha='right')
        plt.title('Average Verification Time (ms)')
        plt.tight_layout()
        
        # Memory usage plot
        plt.subplot(1, 2, 2)
        df_sorted = df.sort_values('avg_memory_mb', ascending=False)
        plt.bar(df_sorted['test_name'], df_sorted['avg_memory_mb'])
        plt.xticks(rotation=45, ha='right')
        plt.title('Average Memory Usage (MB)')
        plt.tight_layout()
        
        # Save plots
        plot_path = report_dir / "benchmark_plots.png"
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
        print(f"\nBenchmark results saved to: {report_dir}")
        print(f"- CSV Report: {csv_path}")
        print(f"- Markdown Report: {markdown_path}")
        print(f"- Plots: {plot_path}")
    else:
        print("No benchmark results to report.")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
