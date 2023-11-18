from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="./local_env.yml")

def adapter_instance(file_to_read):
    adapter = AsvBenchmarkAdapter(
    command=["echo", "Reading asv benchmarks"],
    result_file=Path(file_to_read),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON"),
    },
    )
    adapter.run()
    adapter.post_results()

benchmarks_path = Path("./asv_files")
asv_files = list(benchmarks_path.glob('*.json'))
with open("asv_files_read", "r+") as f:
    processed_files = f.read()
    for file in asv_files:
        file_to_read = str(file)
        if file_to_read not in processed_files:
            print(file_to_read)
            adapter_instance(file_to_read)
            f.write(file_to_read)
            f.write("\n")

#innocent-registration-key