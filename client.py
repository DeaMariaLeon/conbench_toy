from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os

os.environ["CONBENCH_URL"] = "http://127.0.0.1:5000"
os.environ["CONBENCH_EMAIL"] = "deamarialeon@gmail.com"
os.environ["CONBENCH_PASSWORD"] = "x"
os.environ["CONBENCH_PROJECT_REPOSITORY"] = "git@github.com:DeaMariaLeon/algos2"
os.environ["CONBENCH_RUN_REASON"] = "first"
#
os.environ["CONBENCH_PROJECT_PR_NUMBER"] = "1"
os.environ["CONBENCH_PROJECT_COMMIT"] = "cb63287e63db10ce3eb0f3b8c279fd995678d0ae"
#"github": "https://github.com/DeaMariaLeon/algos2.git"
adapter = AsvBenchmarkAdapter(
    command=["echo", "'Hello, world!'"],
    result_dir=Path(__name__).parent.absolute(),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON")
    },
    #result_fields_append={
    #    "info": {"build_version": os.getenv("MY_BUILD_VERSION")},
    #    "context": {"compiler_flags": os.getenv("MY_COMPILER_FLAGS")}
    #},
)

adapter.run()
#adapter()
print(adapter.results)
adapter.post_results()