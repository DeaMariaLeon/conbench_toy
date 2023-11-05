import json
from pathlib import Path
from typing import Any, Dict, List


from benchadapt.adapters._adapter import BenchmarkAdapter
from benchadapt.result import BenchmarkResult

class AsvBenchmarkAdapter(BenchmarkAdapter):

    #result_dir: Path

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
            A list of strings defining a shell command to run benchmarks
        result_dir : Path
            Path to directory where results will be populated
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
        
        parsed_benchmarks = []
        
        #with open("benchmarks.json") as f:
        #with open("a83f6aae-pandas2.json") as f:
        with open("pandas3-2benchmarks.json") as f:
            benchmarks_results = json.load(f)
        
        with open("benchmarks.json") as f:
            benchmarks_info = json.load(f)
        

        names = benchmarks_results["results"].keys()
        #print(names)
        for n in names:
            bench = dict(zip(benchmarks_results["result_columns"], 
                         benchmarks_results["results"][n]))
            param_names = benchmarks_info[n]['param_names']
            param_values = benchmarks_info[n]['params']
            param_dic = dict(zip(param_names, param_values))

            tags = {}
            tags["name"] = n
            tags.update(param_dic)
            print("AQUI",tags)
            parsed_benchmark = BenchmarkResult(
                batch_id="A",
                stats={
                    "data": bench["result"],
                    "unit": "s",
                    "times": bench["result"],
                    "time_unit": "s",
                    "iterations": 1,
                },
                tags={"name": n},
                context={"benchmark_language": "Python"},
                github={"repository": "git@github.com:pandas-dev/pandas",
                        "commit":benchmarks_results["commit_hash"],
                        },
                
            )
            #print(parsed_benchmark.to_publishable_dict())
            parsed_benchmarks.append(parsed_benchmark)
            
        return parsed_benchmarks     

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