import json
from pathlib import Path
from typing import Any, Dict, List
import itertools
import numpy as np

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
        
        with open("c2cdeaf3-env-36436ace7d7eead1c76ef118fd27f1fa.json") as f:
            benchmarks_results = json.load(f)
        
        with open("benchmarks.json") as f:
            benchmarks_info = json.load(f)
        
        # From asv documention "result_columns" is a list of column names for the results dictionary. 
        # ["result", "params", "version", "started_at", "duration", "stats_ci_99_a", "stats_ci_99_b", 
        # "stats_q_25", "stats_q_75", "stats_number", "stats_repeat", "samples", "profile"] 
        # In this first version of the adapter we are using only the "result" column. 
        # TODO: use the "samples" column instead.
        result_columns = benchmarks_results["result_columns"]

        no_results = []
        failing = []     
        for name in benchmarks_results["results"]:
            #Bug with this benchmark: series_methods.ToFrame.time_to_frame
            if name == "series_methods.ToFrame.time_to_frame":
                continue
            print(name)
            try:     
                result_dict = dict(zip(result_columns, 
                                benchmarks_results["results"][name]))
                for param_values, data in zip(
                    itertools.product(*result_dict["params"]),
                    result_dict['result']
                    ):
                    if np.isnan(data):
                            failing.append(name)
                            print('failing ', name)
                            continue   
                    param_dic = dict(zip(benchmarks_info[name]["param_names"],
                                     param_values))      
                    tags = {}
                    tags["name"] = name
                    tags.update(param_dic)
                    parsed_benchmark = BenchmarkResult(
                        batch_id="A", #CORRECT THIS
                        stats={
                            "data": [data],
                            "unit": "s", #CORRECT THIS
                            "times": [data],
                            "time_unit": benchmarks_info[name]['unit'],
                            "iterations": 1,
                        },
                        tags=tags,
                        context={"benchmark_language": "Python"},
                        github={"repository": "git@github.com:pandas-dev/pandas",
                                "commit":benchmarks_results["commit_hash"],
                                },
                    )
                    parsed_benchmarks.append(parsed_benchmark)                        
            except:
                    no_results.append(name)
                
        #save benchmark names which did not work for debugging
        with open("noresults", "a") as no_f:
            no_f.write(benchmarks_results["commit_hash"])
            no_f.write("\n")
            no_f.write("\n".join(set(no_results)))  
                  
        with open("failing", "a") as failing_f:
            failing_f.write(benchmarks_results["commit_hash"])
            failing_f.write("\n")
            failing_f.write("\n".join(set(failing))) 

        return parsed_benchmarks

