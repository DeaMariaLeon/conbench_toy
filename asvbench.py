import json
from pathlib import Path
from typing import Any, Dict, List


from benchadapt.adapters._adapter import BenchmarkAdapter
from benchadapt.result import BenchmarkResult

class AsvBenchmarkAdapter(BenchmarkAdapter):

    result_dir: Path

    def __init__(
        self,
        command: List[str],
        result_dir: Path,
        result_fields_override: Dict[str, Any] = None,
        result_fields_append: Dict[str, Any] = None,        
    ) -> None:
        """
        Parameters
        ----------
        command : List[str]
            A list of strings defining a shell command to run folly benchmarks
        result_dir : Path
            Path to directory where folly results will be populated
        result_fields_override : Dict[str, Any]
            A dict of values to override on each instance of `BenchmarkResult`. Useful
            for specifying metadata only available at runtime, e.g. build info. Applied
            before ``results_field_append``.
        results_fields_append : Dict[str, Any]
            A dict of default values to be appended to `BenchmarkResult` values after
            instantiation. Useful for appending extra tags or other metadata in addition
            to that gathered elsewhere. Only applicable for dict attributes. For each
            element, will override any keys that already exist, i.e. it does not append
            recursively.
        """
        self.result_dir = Path(result_dir)
        super().__init__(
            command=command,
            result_fields_override=result_fields_override,
            result_fields_append=result_fields_append,
        )
 
    def _transform_results(self) -> List[BenchmarkResult]:
        
        parsed_benchmark = BenchmarkResult(
            batch_id="A",
                    stats={
                        "data": [4.789694385535404e-07],
                        "unit": "ns",
                        "times": [4.789694385535404e-07],
                        "time_unit": "s",
                        "iterations": 1,
                    },
                    tags={"name": "benchmarks.TimeSuite.time_insertion_sort", 
                          "suite": "suite", 
                          "source": "cpp-micro"},
                    info={},
                    context={"benchmark_language": "Python"},
            
        )

        return [parsed_benchmark]       

# asv_result = {"commit_hash": "cb63287e63db10ce3eb0f3b8c279fd995678d0ae", 
#               "env_name": "conda-py3.11", 
#               "date": 1696315841000, 
#               "params": {"arch": "arm64", 
#                          "cpu": "Apple M2", 
#                          "machine": "Deas-MacBook-Air.local", 
#                          "num_cpu": "8", 
#                          "os": "macOS 13.5.1 (22G90)", 
#                          "ram": "16GB", 
#                          "python": "3.11"}, 
#               "python": "3.11", 
#               "requirements": {}, 
#               "env_vars": {}, 
#               "result_columns": ["result", "params", "version", "started_at", "duration", "stats_ci_99_a", "stats_ci_99_b", "stats_q_25", "stats_q_75", "stats_number", "stats_repeat", "samples", "profile"], 
#               "results": {"benchmarks.TimeSuite.time_insertion_sort": [[4.789694385535404e-07], [], "1198fba41755fd157a0c7f7bc588ee00d3c4b577d482adc3cf034d8476f03f50", 1697559305660, 0.40301, [4.7191e-07], [4.8881e-07], [4.7676e-07], [4.8181e-07], [22921], [10]]}, "durations": {}, "version": 2}