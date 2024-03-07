import json
import tempfile
from pathlib import Path
import pytest

from asvbench import AsvBenchmarkAdapter
from benchadapt.result import BenchmarkResult



benchmarks_json = {
    "benchmarks.TimeSuite.time_insertion_sort": {
        "code": "class TimeSuite:\n    def time_insertion_sort(self):\n        sort(self.array)\n\n    def setup(self):\n        LENGTH = 10\n        self.array = [random.randint(0, 1000) for i in range(LENGTH)]",
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
    "strings.Repeat.time_repeat": {
        "code": "class Repeat:\n    def time_repeat(self, repeats):\n        self.s.str.repeat(self.values)\n\n    def setup(self, repeats):\n        N = 10**5\n        self.s = Series(Index([f\"i-{i}\" for i in range(N)], dtype=object))\n        repeat = {\"int\": 1, \"array\": np.random.randint(1, 3, N)}\n        self.values = repeat[repeats]",
        "min_run_count": 2,
        "name": "strings.Repeat.time_repeat",
        "number": 0,
        "param_names": [
            "repeats"
        ],
        "params": [
            [
                "'int'",
                "'array'"
            ]
        ],
        "repeat": 0,
        "rounds": 2,
        "sample_time": 0.01,
        "type": "time",
        "unit": "seconds",
        "version": "1020d0debc1446a71cfda9efe059407dc390e74d806d2783566fdba4e7d1de98",
        "warmup_time": -1
    },
    "boolean.TimeLogicalOps.time_or_scalar": {
        "code": "class TimeLogicalOps:\n    def time_or_scalar(self):\n        self.left | True\n        self.left | False\n\n    def setup(self):\n        N = 10_000\n        left, right, lmask, rmask = np.random.randint(0, 2, size=(4, N)).astype(\"bool\")\n        self.left = pd.arrays.BooleanArray(left, lmask)\n        self.right = pd.arrays.BooleanArray(right, rmask)",
        "min_run_count": 2,
        "name": "boolean.TimeLogicalOps.time_or_scalar",
        "number": 0,
        "param_names": [],
        "params": [],
        "repeat": 0,
        "rounds": 2,
        "sample_time": 0.01,
        "type": "time",
        "unit": "seconds",
        "version": "a9dcf90a110c0c703887ee44358e18a6930758987f7f1e9f921dd5ff4c84234e",
        "warmup_time": -1
    },
    "array.ArrowStringArray.time_setitem_slice": {
        "code": "class ArrowStringArray:\n    def time_setitem_slice(self, multiple_chunks):\n        self.array[::10] = \"foo\"\n\n    def setup(self, multiple_chunks):\n        try:\n            import pyarrow as pa\n        except ImportError as err:\n            raise NotImplementedError from err\n        strings = np.array([str(i) for i in range(10_000)], dtype=object)\n        if multiple_chunks:\n            chunks = [strings[i : i + 100] for i in range(0, len(strings), 100)]\n            self.array = pd.arrays.ArrowStringArray(pa.chunked_array(chunks))\n        else:\n            self.array = pd.arrays.ArrowStringArray(pa.array(strings))",
        "min_run_count": 2,
        "name": "array.ArrowStringArray.time_setitem_slice",
        "number": 0,
        "param_names": [
            "multiple_chunks"
        ],
        "params": [
            [
                "False",
                "True"
            ]
        ],
        "repeat": 0,
        "rounds": 2,
        "sample_time": 0.01,
        "type": "time",
        "unit": "seconds",
        "version": "6a0d09a5d23eb6dc7d6bb95140476cc1c1a896640e9d7bd005861c59072edc0d",
        "warmup_time": -1
    },
    "version": 2
}

asv_json = {
    "commit_hash": "0d24f201cc2506de45a2ed688d9f72f7123d58f7",
    "env_name": "conda-py3.10",
    "date": 1703062645000,
    "params": {
        "arch": "arm64",
        "cpu": "Apple M2",
        "machine": "MyMachine",
        "num_cpu": "8",
        "os": "macOS 13.5.1 (22G90)",
        "ram": "16GB",
        "python": "3.10"
    },
    "python": "3.10",
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

asv_json_with_param_andsamples = {
    "commit_hash": "89b286a699b2d023b7a1ebc468abf230d84ad547",
    "env_name": "conda-py3.10-Cython3.0-jinja2-matplotlib-meson-meson-python-numba-numexpr-odfpy-openpyxl-pyarrow-pytables-python-build-scipy-sqlalchemy-xlrd-xlsxwriter",
    "date": 1709607034000,
    "params": {
        "arch": "arm64",
        "cpu": "Apple M2",
        "machine": "MyMachine",
        "num_cpu": "8",
        "os": "macOS 13.5.1 (22G90)",
        "ram": "16GB",
        "python": "3.10",
        "Cython": "3.0",
        "matplotlib": "",
        "sqlalchemy": "",
        "scipy": "",
        "numba": "",
        "numexpr": "",
        "pytables": "",
        "pyarrow": "",
        "openpyxl": "",
        "xlsxwriter": "",
        "xlrd": "",
        "odfpy": "",
        "jinja2": "",
        "meson": "",
        "meson-python": "",
        "python-build": ""
    },
    "python": "3.10",
    "requirements": {
        "Cython": "3.0",
        "matplotlib": "",
        "sqlalchemy": "",
        "scipy": "",
        "numba": "",
        "numexpr": "",
        "pytables": "",
        "pyarrow": "",
        "openpyxl": "",
        "xlsxwriter": "",
        "xlrd": "",
        "odfpy": "",
        "jinja2": "",
        "meson": "",
        "meson-python": "",
        "python-build": ""
    },
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
        "strings.Repeat.time_repeat": [
            [
                0.03481033350544749,
                0.03935433350125095
            ],
            [
                [
                    "'int'",
                    "'array'"
                ]
            ],
            "1020d0debc1446a71cfda9efe059407dc390e74d806d2783566fdba4e7d1de98",
            1709658661060,
            2.571,
            [
                0.0344,
                0.039027
            ],
            [
                0.035398,
                0.039706
            ],
            [
                0.034686,
                0.039297
            ],
            [
                0.035208,
                0.039587
            ],
            [
                1,
                1
            ],
            [
                10,
                10
            ]
        ],
        "boolean.TimeLogicalOps.time_or_scalar": [
            [
                0.00001634304932968048
            ],
            [],
            "a9dcf90a110c0c703887ee44358e18a6930758987f7f1e9f921dd5ff4c84234e",
            1709659847382,
            0.91048,
            [
                0.000016278
            ],
            [
                0.000016475
            ],
            [
                0.000016302
            ],
            [
                0.000016374
            ],
            [
                669
            ],
            [
                10
            ],
            [
                [
                    0.000016370204791373757,
                    0.0000164747757895297,
                    0.000016352142014517064,
                    0.000016375186853806846,
                    0.000016442887910143355,
                    0.00001633370702185561,
                    0.000016333956644843892,
                    0.000016291790719454486,
                    0.000016286434983849937,
                    0.000016278026913333076
                ]
            ]
        ],
        "array.ArrowStringArray.time_setitem_slice": [
            [
                0.00006179990675063583,
                0.0001277931890998422
            ],
            [
                [
                    "False",
                    "True"
                ]
            ],
            "6a0d09a5d23eb6dc7d6bb95140476cc1c1a896640e9d7bd005861c59072edc0d",
            1709800865468,
            1.875,
            [
                0.000061653,
                0.00012664
            ],
            [
                0.00006225,
                0.000136
            ],
            [
                0.00006173,
                0.00012706
            ],
            [
                0.000061992,
                0.00012931
            ],
            [
                177,
                82
            ],
            [
                10,
                10
            ],
            [
                [
                    0.00006182156493334826,
                    0.00006185522589748356,
                    0.00006203789830912894,
                    0.00006174882492418848,
                    0.0000617782485679234,
                    0.00006172410722185284,
                    0.00006224953116964823,
                    0.00006212170615971173,
                    0.0000616723163800556,
                    0.00006165348587289326
                ],
                [
                    0.00012692784153708688,
                    0.00012744156105682345,
                    0.00012687448782721397,
                    0.00013600406094976678,
                    0.00012771798781880246,
                    0.00012936482948489579,
                    0.00013176371945386253,
                    0.00012914939050948839,
                    0.0001266422804314416,
                    0.00012786839038088192
                ]
            ]
        ]
    },
    
    "durations": {},
    "version": 2
}
class TestAsvAdapter:
    @pytest.fixture
    def asv_adapter(self, monkeypatch):
        monkeypatch.setenv(
            "REPOSITORY", "git@github.com:conchair/conchair"
        )
        
        result_file = tempfile.mktemp(suffix=".json")
        tempdir =  Path(tempfile.mkdtemp())

        asv_adapter = AsvBenchmarkAdapter(
            command=["echo", "'Hello, world!'"],
            result_file=Path(result_file),
            benchmarks_file_path=str(tempdir)+"/",
        )

        with open(asv_adapter.result_file, "w") as f:
            json.dump(asv_json, f)
        
        name = tempdir.joinpath("benchmarks.json")
        with open(name, "w") as f:
            json.dump(benchmarks_json, f)

        return asv_adapter
    
    def test_transform_results(self, asv_adapter) -> None:
        results = asv_adapter.transform_results()
       
        assert len(results) == 1
        assert len(set(res.tags["name"] for res in results)) == 1
        assert len(set(res.batch_id for res in results)) == 1
        for result in results:
        
            assert isinstance(result, BenchmarkResult)
            assert isinstance(result.run_name, str)
            assert result.tags["name"].endswith("time_insertion_sort")
            assert result.context == {'benchmark_language': 'Python',
                                      'env_name': 'conda-py3.10',
                                      'python': '3.10',
                                      'requirements': {}}
            
            assert result.machine_info is not None
            assert result.stats == {'data': [1.2035623905003376],
                                    'unit': 's',
                                    'iterations': 1}
            assert result.github['commit'] == '0d24f201cc2506de45a2ed688d9f72f7123d58f7'


class TestAsvAdapter_with_param_andsamples:
    @pytest.fixture
    def asv_adapter(self, monkeypatch):
        monkeypatch.setenv(
            "REPOSITORY", "git@github.com:conchair/conchair"
        )

        result_file = tempfile.mktemp(suffix=".json")
        tempdir = Path(tempfile.mkdtemp())

        asv_adapter = AsvBenchmarkAdapter(
            command=["echo", "'Hello, world!'"],
            result_file=Path(result_file),
            benchmarks_file_path=str(tempdir)+"/",
        )

        with open(asv_adapter.result_file, "w") as f:
            json.dump(asv_json_with_param_andsamples, f)
        
        name = tempdir.joinpath("benchmarks.json")
        with open(name, "w") as f:
            json.dump(benchmarks_json, f)

        return asv_adapter
    
    def test_transform_results(self, asv_adapter) -> None:
        results = asv_adapter.transform_results()

        assert len(results) == 5
        assert len([res.tags["name"] for res in results]) == 5
        
        for result in results:
           match result.tags:
               case {'name': 'strings.Repeat.time_repeat', 'repeats': "'int'"}:
                   assert result.stats == {'data': [0.03481033350544749],
                                          'unit': 's',
                                          'iterations': 1}
               case {'name': 'strings.Repeat.time_repeat', 'repeats': "'array'"}:
                   assert result.stats == {'data': [0.03935433350125095], 
                                            'unit': 's', 
                                            'iterations': 1}
               case {'name': 'boolean.TimeLogicalOps.time_or_scalar'}:
                   assert result.stats == {'data': [1.6370204791373757e-05, 
                                                      1.64747757895297e-05, 
                                                      1.6352142014517064e-05, 
                                                      1.6375186853806846e-05, 
                                                      1.6442887910143355e-05, 
                                                      1.633370702185561e-05, 
                                                      1.6333956644843892e-05, 
                                                      1.6291790719454486e-05, 
                                                      1.6286434983849937e-05, 
                                                      1.6278026913333076e-05], 
                                                      'unit': 's', 
                                                      'iterations': 10}
               case {'name': 'array.ArrowStringArray.time_setitem_slice'}:
                   assert len(result.stats["data"]) == 10
