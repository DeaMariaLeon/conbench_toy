import json
from pathlib import Path
from typing import Any, Dict, List
import itertools
import numpy as np
import os
from datetime import datetime



from benchadapt.adapters._adapter import BenchmarkAdapter
from benchadapt.result import BenchmarkResult

class AsvBenchmarkAdapter(BenchmarkAdapter):

    def __init__(
        self,
        command: List[str],
        result_file: Path,
        benchmarks_file_path: str,
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
        self.benchmarks_file_path=benchmarks_file_path
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

        benchmarks_file = self.benchmarks_file_path + "benchmarks.json"
        with open(benchmarks_file) as f:
            benchmarks_info = json.load(f)
        
        parsed_benchmarks = self._parse_results(benchmarks_results, benchmarks_info)
 
        return parsed_benchmarks

    def _parse_results(self, benchmarks_results, benchmarks_info):
        """
        From asv documention "result_columns" is a list of column names for the results dictionary. 
        ["result", "params", "version", "started_at", "duration", "stats_ci_99_a", "stats_ci_99_b", 
        "stats_q_25", "stats_q_75", "stats_number", "stats_repeat", "samples", "profile"] 
        In this first version of the adapter we are using only the "result" column. 
        TODO: use the "samples" column instead.
        """
        try:
           result_columns = benchmarks_results["result_columns"]
        except:
           raise Exception("Incorrect file format")
        parsed_benchmarks = []
          
        for name in benchmarks_results["results"]:
            
            try:
                # benchmarks_results["results"][name] bellow has either a list
                # with items corresponding to each result of a parameters combination,
                # or just one value if the benchmark has no parameters.
                # "name" is the name of the benchmark
                result_dict = dict(zip(result_columns,
                                benchmarks_results["results"][name]))
                if "samples" in result_dict:
                    data_key = "samples"
                    
                else:
                    data_key = "result"
                    iterations = 1

                for param_values, data in zip(
                    itertools.product(*result_dict["params"]),
                    result_dict[data_key]
                    ):
                    if not np.all(data):
                            # Nan is generated in the results by pandas benchmarks
                            # when a combination of parameters is not allowed.
                            # In this case, the result is not sent to  the conbench webapp
                            continue
                    param_dic = dict(zip(benchmarks_info[name]["param_names"],
                                     param_values))
                    tags = {}
                    tags["name"] = name
                    tags.update(param_dic)
                    #asv units are seconds or bytes, conbench uses "s" or "B"
                    units = {"seconds": "s",
                             "bytes": "B"} 
                    params = benchmarks_results["params"]

                    if data_key == "result":
                        data = [data]
                    else:
                        iterations = len(data)
                    parsed_benchmark = BenchmarkResult(
                        
                        stats={
                            #asv returns one value wich is the average of the iterations
                            #but it can be changed so it returns the value of each iteration
                            #if asv returns the value of each iteration, the variable "data"
                            #will be a list, so this needs to be addressed below
                            "data": data,
                            "unit": units[benchmarks_info[name]['unit']],
                            #iterations below is for conbench, 1 if we only provide a value
                            #if we run asv to return the value of each iteration (in data above)
                            #iterations should match the number of values
                            "iterations": iterations,
                        },
                        tags=tags,
                        context={"benchmark_language": "Python",
                                 "env_name": benchmarks_results["env_name"],
                                 "python": benchmarks_results["python"],
                                 "requirements": benchmarks_results["requirements"],
                                 },
                        github={"repository": os.environ["REPOSITORY"],
                                "commit":benchmarks_results["commit_hash"],
                                },
                        info={"date": str(datetime.fromtimestamp(benchmarks_results["date"]/1e3)),
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
                # This happens if the name of the benchmark is
                # not found in benchmarks.json
                
                continue

        return parsed_benchmarks
    
        

