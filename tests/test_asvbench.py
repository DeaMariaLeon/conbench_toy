import json
import pytest

from asvbench import AsvBenchmarkAdapter
from benchadapt.result import BenchmarkResult

ASV_RESULT = {
    "commit_hash": "0d24f201cc2506de45a2ed688d9f72f7123d58f7",
    "env_name": "conda-py3.11",
    "date": 1703062645000,
    "params": {
        "arch": "arm64",
        "cpu": "Apple M2",
        "machine": "Deas-MacBook-Air.local",
        "num_cpu": "8",
        "os": "macOS 13.5.1 (22G90)",
        "ram": "16GB",
        "python": "3.11"
    },
    "python": "3.11",
    "requirements": {},
    "env_vars": {},
    "result_columns": [
        "result",
        "params",
        "version",
        "started_at",
        "duration",
        "stats_ci_99_a",
        "stats_ci_99_b",
        "stats_q_25",
        "stats_q_75",
        "stats_number",
        "stats_repeat",
        "samples",
        "profile"
    ],
    "results": {
        "benchmarks.TimeSuite.time_insertion_sort": [
            [
                1.2035623905003376
            ],
            [],
            "1198fba41755fd157a0c7f7bc588ee00d3c4b577d482adc3cf034d8476f03f50",
            1703063099923,
            38.656,
            [
                1.2016
            ],
            [
                1.2053
            ],
            [
                1.2025
            ],
            [
                1.2045
            ],
            [
                4
            ],
            [
                6
            ]
        ]
    },
    "durations": {},
    "version": 2
}

BENCHMARK_JSON = {
    "benchmarks.TimeSuite.time_insertion_sort": {
        "code": "class TimeSuite:\n    def time_insertion_sort(self):\n        sort(self.array)\n\n    def setup(self):\n        LENGTH = 10\n        #random.seed(10)\n        self.array = [random.randint(0, 1000) for i in range(LENGTH)]",
        "min_run_count": 2,
        "name": "benchmarks.TimeSuite.time_insertion_sort",
        "number": 4,
        "param_names": [],
        "params": [],
        "repeat": 3,
        "rounds": 2,
        "sample_time": 0.01,
        "type": "time",
        "unit": "seconds",
        "version": "1198fba41755fd157a0c7f7bc588ee00d3c4b577d482adc3cf034d8476f03f50",
        "warmup_time": -1
    },
    "version": 2
}