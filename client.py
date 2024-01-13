from asvbench import AsvBenchmarkAdapter
from pathlib import Path
import os
from dotenv import load_dotenv
import time
import socket
import alert

if socket.gethostname().startswith('Deas'):
      load_dotenv(dotenv_path="./local_env.yml")
else:
      load_dotenv(dotenv_path="./server_env.yml")

PANDAS_ASV_RESULTS_PATH = os.getenv("PANDAS_ASV_RESULTS_PATH")
BENCHMARKS_FILE_PATH = os.getenv("BENCHMARKS_FILE_PATH")

def adapter_instance(file_to_read) -> None:
    adapter = AsvBenchmarkAdapter(
    command=["echo", str(file_to_read)],
    result_file=Path(file_to_read),
    result_fields_override={
        "run_reason": os.getenv("CONBENCH_RUN_REASON"),
    },
    benchmarks_file_path=BENCHMARKS_FILE_PATH,
    )
    adapter.run()
    alert.alert(adapter.results[0].github['commit'])
    adapter.post_results()
    
         
def main() -> None:
   
   while True:
       benchmarks_path = Path(PANDAS_ASV_RESULTS_PATH)
       all_files = [str(file) for file in benchmarks_path.glob('*.json')]
       with open("asv_processed_files", "r+") as f:
           processed_files = f.read().split('\n')
       for new_file in (set(all_files) - set(processed_files)):
           adapter_instance(new_file)
           with open("asv_processed_files", "a") as f:
               f.write(new_file)
               f.write("\n") 
       time.sleep(30) #adjust this on server

if __name__=="__main__":
   main()
        
