import json
from pathlib import Path
from typing import Any, Dict, List
import itertools
import numpy as np
from datetime import datetime

from benchadapt.adapters._adapter import BenchmarkAdapter
from benchadapt.result import BenchmarkResult

class AsvBenchmarkAdapter(BenchmarkAdapter):

    def __init__(
        self,
        command: List[str],
        result_file: Path,
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
        self.result_file = result_file
        super().__init__(
            command=command,
            result_fields_override=result_fields_override,
            result_fields_append=result_fields_append,
        )
    
    def _transform_results(self) -> List[BenchmarkResult]:
        """Transform asv results into a list of BenchmarkResults instances"""
        parsed_benchmarks = []
        
        with open(self.result_file, "r") as f:

            benchmarks_results = json.load(f)
        
        with open("benchmarks.json") as f:
            benchmarks_info = json.load(f)
        
        parsed_benchmarks, no_results, failing = self._parse_results(benchmarks_results, benchmarks_info)

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

    def _parse_results(self, benchmarks_results, benchmarks_info):
        # From asv documention "result_columns" is a list of column names for the results dictionary. 
        # ["result", "params", "version", "started_at", "duration", "stats_ci_99_a", "stats_ci_99_b", 
        # "stats_q_25", "stats_q_75", "stats_number", "stats_repeat", "samples", "profile"] 
        # In this first version of the adapter we are using only the "result" column. 
        # TODO: use the "samples" column instead.
        result_columns = benchmarks_results["result_columns"]
        parsed_benchmarks = []
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
                    params = benchmarks_results["params"]
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
                        context={"benchmark_language": "Python",
                                 "env_name": benchmarks_results["env_name"],
                                 "date": str(datetime.fromtimestamp(benchmarks_results["date"]/1e3)),
                                 "python": benchmarks_results["python"],
                                 "requirements": benchmarks_results["requirements"],
                                 },
                        github={"repository": "git@github.com:pandas-dev/pandas",
                                "commit":benchmarks_results["commit_hash"],
                                },
                        machine_info={
                             "name": params["machine"],
                             "os_name": params["os"],
                             "os_version":params["os"],
                             "architecture_name": params["arch"],
                             "kernel_name": "x",
                             "memory_bytes": 0,
                             "cpu_model_name": params["cpu"],
                             "cpu_core_count": params["num_cpu"],
                             "cpu_thread_count": 0,
                             "cpu_l1d_cache_bytes": 0,
                             "cpu_l1i_cache_bytes": 0,
                             "cpu_l2_cache_bytes": 0,
                             "cpu_l3_cache_bytes": 0,
                             "cpu_frequency_max_hz": 0,
                             "gpu_count": 0,
                             "gpu_product_names": [],      
                               }
                    )
                    parsed_benchmarks.append(parsed_benchmark)         
            except:
                    no_results.append(name)
                
        return parsed_benchmarks, no_results, failing

