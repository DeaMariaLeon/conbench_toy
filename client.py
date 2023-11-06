from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./local_env.yml")

adapter = AsvBenchmarkAdapter(
    command=["echo", "'Hello, world!'"],
    result_dir=Path(__name__).parent.absolute(),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON")
    },
)

adapter.run()

#print(adapter.results)
adapter.post_results()