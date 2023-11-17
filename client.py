from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./local_env.yml")

#benchmarks_path = Path("./asv_files")
#files = list(benchmarks_path.glob('*.json'))
#        with open("asv_files_read", "r+") as f:
#            x = f.read()
#            for file in files:
#                print(str(file))
#                if str(file) not in x:
#                    print(str(file))
#                    with open(str(file)) as read_this:
#                        benchmarks_results = json.load(read_this)
#                    f.write(str(file))
#                    f.write("\n")


adapter = AsvBenchmarkAdapter(
    command=["echo", "Reading asv benchmarks"],
    #result_dir=Path(__name__).parent.absolute(),
    result_dir=Path("/Users/dealeon/asv_files"),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON"),
    },
)

adapter.run()
adapter.post_results()

#innocent-registration-key