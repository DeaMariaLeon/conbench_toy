from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os

os.environ["CONBENCH_URL"] = "http://127.0.0.1:5000"
os.environ["CONBENCH_EMAIL"] = "deamarialeon@gmail.com"
os.environ["CONBENCH_PASSWORD"] = "x"
os.environ["CONBENCH_PROJECT_REPOSITORY"] = "git@github.com:DeaMariaLeon/algos2.git"
os.environ["CONBENCH_RUN_REASON"] = "first"
#os.environ[""]
#"github": "https://github.com/DeaMariaLeon/algos2.git"
adapter = AsvBenchmarkAdapter(
    command=["echo", "'Hello, world!'"],
    result_dir=Path(__name__).parent.absolute(),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON")
    },
)

adapter.run()
#adapter()
print(adapter.results)
#adapter.results.post_results() # AttributeError: 'AsvBenchmarkAdapter' object has no attribute 'publish_results'. Did you mean: 'post_results'?
#adapter.publish_results()
#adapter()
adapter.post_results()