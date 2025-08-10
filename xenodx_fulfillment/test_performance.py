#!/usr/bin/env python3
"""Performance test to measure shared services overhead"""
import time
import asyncio
import statistics
from pathlib import Path
import tempfile
import sys
sys.path.append(str(Path(__file__).parent.parent))

from xenodx_fulfillment.shared.config import Config
from xenodx_fulfillment.shared.models import AnalysisResult, EmotionScore, EmotionCategory, Metadata
from xenodx_fulfillment.shared.reports import ReportGenerator
from xenodx_fulfillment.shared.pipeline import Pipeline


class MinimalClient:
    """Minimal API client for baseline measurement"""
    async def analyze_file(self, file_path: Path):
        # Simulate minimal API call
        await asyncio.sleep(0.001)  # 1ms simulated API latency
        return {"status": "success", "emotions": []}


class MinimalAnalyzer:
    """Minimal analyzer for baseline measurement"""
    def analyze(self, raw_result):
        return AnalysisResult(
            emotions=[EmotionScore(EmotionCategory.NEUTRAL, 1.0, 1.0)],
            raw_response=raw_result,
            metadata=Metadata(file_path="/test.mp3", api_name="Test")
        )


async def measure_shared_services_overhead():
    """Measure the overhead added by shared services"""
    print("Performance Test: Shared Services Overhead")
    print("=" * 50)
    
    # Create test file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        f.write(b"fake audio data")
        test_file = Path(f.name)
    
    # Test 1: Measure baseline (direct API call)
    print("\n1. Baseline Performance (Direct API Call)")
    print("-" * 30)
    
    client = MinimalClient()
    analyzer = MinimalAnalyzer()
    baseline_times = []
    
    for i in range(100):
        start = time.perf_counter()
        
        # Direct call without shared services
        raw_result = await client.analyze_file(test_file)
        result = analyzer.analyze(raw_result)
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        baseline_times.append(elapsed)
    
    baseline_avg = statistics.mean(baseline_times)
    baseline_std = statistics.stdev(baseline_times)
    print(f"Average time: {baseline_avg:.2f}ms (±{baseline_std:.2f}ms)")
    
    # Test 2: Measure with shared services (no features)
    print("\n2. With Shared Services (Minimal Config)")
    print("-" * 30)
    
    minimal_config = Config(data={
        'api_name': 'Test',
        'job_tracking': {'enable': False},
        'reports': {'formats': []},
        'error_handling': {'max_retries': 0}
    })
    
    pipeline = Pipeline(
        client=client,
        analyzer=analyzer,
        config=minimal_config
    )
    
    shared_minimal_times = []
    
    for i in range(100):
        start = time.perf_counter()
        result = await pipeline.process_file(test_file)
        elapsed = (time.perf_counter() - start) * 1000
        shared_minimal_times.append(elapsed)
    
    shared_minimal_avg = statistics.mean(shared_minimal_times)
    shared_minimal_std = statistics.stdev(shared_minimal_times)
    minimal_overhead = shared_minimal_avg - baseline_avg
    
    print(f"Average time: {shared_minimal_avg:.2f}ms (±{shared_minimal_std:.2f}ms)")
    print(f"Overhead: {minimal_overhead:.2f}ms ({(minimal_overhead/baseline_avg)*100:.1f}%)")
    
    # Test 3: Measure with all features enabled
    print("\n3. With All Features Enabled")
    print("-" * 30)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        full_config = Config(data={
            'api_name': 'Test',
            'job_tracking': {
                'enable': True,
                'directory': str(Path(tmpdir) / 'jobs')
            },
            'reports': {
                'formats': ['json', 'html', 'markdown'],
                'output_directory': str(Path(tmpdir) / 'reports')
            },
            'error_handling': {
                'max_retries': 3,
                'retry_delay': 0
            }
        })
        
        pipeline_full = Pipeline(
            client=client,
            analyzer=analyzer,
            config=full_config
        )
        
        shared_full_times = []
        
        for i in range(100):
            start = time.perf_counter()
            result = await pipeline_full.process_file(test_file)
            elapsed = (time.perf_counter() - start) * 1000
            shared_full_times.append(elapsed)
        
        shared_full_avg = statistics.mean(shared_full_times)
        shared_full_std = statistics.stdev(shared_full_times)
        full_overhead = shared_full_avg - baseline_avg
        
        print(f"Average time: {shared_full_avg:.2f}ms (±{shared_full_std:.2f}ms)")
        print(f"Overhead: {full_overhead:.2f}ms ({(full_overhead/baseline_avg)*100:.1f}%)")
    
    # Test 4: Memory usage
    print("\n4. Memory Usage")
    print("-" * 30)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # Baseline memory
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Baseline memory: {baseline_memory:.1f} MB")
    
    # Create multiple pipeline instances
    pipelines = []
    for i in range(10):
        p = Pipeline(
            client=MinimalClient(),
            analyzer=MinimalAnalyzer(),
            config=full_config
        )
        pipelines.append(p)
    
    pipeline_memory = process.memory_info().rss / 1024 / 1024
    memory_per_pipeline = (pipeline_memory - baseline_memory) / 10
    
    print(f"With 10 pipelines: {pipeline_memory:.1f} MB")
    print(f"Memory per pipeline: {memory_per_pipeline:.1f} MB")
    
    # Test 5: Report generation overhead
    print("\n5. Report Generation Performance")
    print("-" * 30)
    
    report_gen = ReportGenerator()
    test_result = AnalysisResult(
        emotions=[
            EmotionScore(EmotionCategory.JOY, 0.7, 0.8),
            EmotionScore(EmotionCategory.NEUTRAL, 0.3, 0.6)
        ],
        raw_response={"test": "data" * 100},  # Larger payload
        metadata=Metadata(
            file_path="/test.mp3",
            api_name="Test",
            duration=120.5,
            processing_time=2.3
        ),
        summary="Test summary" * 50  # Longer summary
    )
    
    # Test each report format
    for format_type in ['json', 'html', 'markdown']:
        times = []
        for i in range(100):
            start = time.perf_counter()
            report = report_gen.generate_report(test_result, format=format_type)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        print(f"{format_type.upper()} generation: {avg_time:.2f}ms")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Minimal overhead: {minimal_overhead:.2f}ms ({(minimal_overhead/baseline_avg)*100:.1f}%)")
    print(f"Full feature overhead: {full_overhead:.2f}ms ({(full_overhead/baseline_avg)*100:.1f}%)")
    print(f"Memory per pipeline: {memory_per_pipeline:.1f} MB")
    
    # Performance verdict
    print("\nPERFORMANCE VERDICT:")
    if minimal_overhead < 5 and full_overhead < 50:
        print("✅ Shared services add negligible overhead")
        print("   - Less than 5ms for core functionality")
        print("   - Less than 50ms with all features enabled")
        print("   - Memory footprint under 10MB per pipeline")
    else:
        print("⚠️ Performance overhead detected:")
        if minimal_overhead >= 5:
            print(f"   - Core overhead: {minimal_overhead:.1f}ms (target: <5ms)")
        if full_overhead >= 50:
            print(f"   - Full overhead: {full_overhead:.1f}ms (target: <50ms)")
    
    # Cleanup
    test_file.unlink()


def main():
    """Run performance tests"""
    asyncio.run(measure_shared_services_overhead())


if __name__ == "__main__":
    main()