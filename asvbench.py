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
        
        #with open("a83f6aae-pandas2.json") as f:
        with open("pandas3-2benchmarks.json") as f:
        #with open("c2cdeaf3-env-36436ace7d7eead1c76ef118fd27f1fa.json") as f:
        #with open("6493d2a4-env-36436ace7d7eead1c76ef118fd27f1fa.json") as f:
        #with open("6493d2a4-modified.json") as f:
        #with open("/Users/dealeon/Documents/algos2/.asv/results/Deas-MacBook-Air.local/cb63287e-conda-py3.11.json") as f:
            raw_json = json.load(f)
        
        with open("benchmarks.json") as f:
        #with open("/Users/dealeon/Documents/algos2/.asv/results/benchmarks.json") as f:
            settings_file = json.load(f)
        names = raw_json["results"].keys()
        no_results = []
        failing = []
        none_in_param = []
        
        for name in names:
            #Bug with this benchmark: series_methods.ToFrame.time_to_frame
            if name == "series_methods.ToFrame.time_to_frame":
                continue
            print(name)
            result_list = raw_json["results"][name][0]
            param_names = settings_file[name]['param_names']
            param_values = raw_json["results"][name][1]
            combinations = [p for p in itertools.product(*param_values)]            
            nan = None
            if result_list and not np.isnan(result_list).any():
                for i, result in enumerate(result_list):       
                    data = [result]
                    param_dic = dict(zip(param_names,combinations[i]))
                    tags = {}
                    tags["name"] = name
                    tags.update(param_dic)
                    parsed_benchmark = BenchmarkResult(
                        batch_id="A",
                        stats={
                            "data": data,
                            "unit": "s", #CORRECT THIS
                            "times": data,
                            "time_unit": settings_file[name]['unit'],
                            "iterations": 1,
                        },
                        tags=tags,
                        context={"benchmark_language": "Python"},
                        github={"repository": "git@github.com:pandas-dev/pandas",
                                "commit":raw_json["commit_hash"],
                                },
                    )
                    parsed_benchmarks.append(parsed_benchmark)
                          
            else:
                no_results.append(name)
                
        print(f'{no_results=}')

        return parsed_benchmarks

