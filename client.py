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
all_files = [str(file) for file in benchmarks_path.glob('*.json')]
try:
    with open("asv_processed_files", "r+") as f:
        processed_files = f.read().split('\n')
        for new_file in (set(all_files) - set(processed_files)):
            adapter_instance(new_file)
            f.write(new_file)
            f.write("\n")
except:
    print("The file you are trying to read is not correct")