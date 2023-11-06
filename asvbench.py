import json
from pathlib import Path
from typing import Any, Dict, List
import itertools


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
        #with open("pandas3-2benchmarks.json") as f:
        with open("c2cdeaf3-env-36436ace7d7eead1c76ef118fd27f1fa.json") as f:
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
            combinations = [p for p in itertools.product(*param_values)]
        
            for i in range(len(combinations)):
                param_dic = dict(zip(param_names,combinations[i]))
                print(i, param_dic, bench["result"][i])

                tags = {}
                tags["name"] = n
                tags.update(param_dic)
                parsed_benchmark = BenchmarkResult(
                    batch_id="A",
                    stats={
                        "data": data,
                        "unit": "s", #CORRECT THIS
                        "times": data,
                        "time_unit": benchmarks_info[n]['unit'],
                        "iterations": 1,
                    },
                    tags=tags,
                    context={"benchmark_language": "Python"},
                    github={"repository": "git@github.com:pandas-dev/pandas",
                            "commit":benchmarks_results["commit_hash"],
                            },
                    
                )
                
                parsed_benchmarks.append(parsed_benchmark)
        
        #with open("parsed_benchmarks.json", "w") as f:
        #    json.dump(parsed_benchmarks, f)

        return parsed_benchmarks     

