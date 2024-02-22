from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import CheckStatus
import benchalerts.pipeline_steps as steps
import benchmark_email
from datetime import datetime
import json
import numpy as np
import pandas as pd
import re
from utilities import Environment, alerts_done_file

env = Environment()

repo = env.GITHUB_REPOSITORY
input_file = env.ASV_PROCESSED_FILES
output_file = env.ALERT_PROCESSED_FILES
results_data_frame = "./out.pkl"

def alert_instance(commit_hash):

    # Create a pipeline to update a GitHub Check
    pipeline = AlertPipeline(
        steps=[
            steps.GetConbenchZComparisonStep(
                commit_hash=commit_hash,
                baseline_run_type=steps.BaselineRunCandidates.parent,
            ),
            ],
        )
    return pipeline


def report(pipeline):
    full_comparison_info = \
        pipeline.run_pipeline()['GetConbenchZComparisonStep']
    alerter = Alerter()
    if alerter.github_check_status(full_comparison_info) == CheckStatus.FAILURE:
        message = """Subject: Benchmarks Alert \n\n """ \
                  + alerter.github_check_summary(full_comparison_info, "")
        correctserver = re.sub(r'0\.0\.0\.0', '57.128.112.95', message)  # new server
        cleaned_message = re.sub(r'- Commit Run.+\)|#| All benchmark runs analyzed:', '', correctserver)
        # send message or cleaned_message
        benchmark_email.email(cleaned_message)


def analyze_pipeline(pipeline, commit, date):
    analysis = pipeline.run_pipeline()['GetConbenchZComparisonStep']
    results_w_z_regressions = analysis.results_with_z_regressions
    columns = [(str(regression.display_name)) for regression in results_w_z_regressions]
    with open("columns", "a") as f:
        f.write(str(columns))
    commit_df = pd.DataFrame(data=np.ones((1, len(columns))), index=[commit], columns=columns)  # commit is a list
    commit_df.insert(0, "datetime",[datetime.fromtimestamp(int(date)/1e3)])

    return commit_df

#def find_regressions(df):
    
def open_file(input_file):
    with open(input_file, "r") as f:
        processed_files = f.read().split('\n')
    return processed_files

def save_file(output_file, new_file):
    with open(output_file, "a") as f:
            f.write(new_file)
            f.write("\n")

def alert(input_file, output_file) -> None:
    
    df = pd.read_pickle(results_data_frame)
    save_df = False
    processed_files = open_file(input_file)
    for new_file in (set(processed_files) - set(alerts_done_file(env))):
        try:
            with open(new_file, "r") as f:
                benchmarks_results = json.load(f)
        except:
            continue
        pipeline = alert_instance(benchmarks_results['commit_hash'])
        
        # report(pipeline) email report
        commit_df = analyze_pipeline(pipeline,
                                     benchmarks_results['commit_hash'],
                                     benchmarks_results['date'],
                                     )
        try:
            df = pd.concat([df, commit_df])
            #find_regressions(df)
            save_df = True
        except:
            print(benchmarks_results['commit_hash'])
            save_df = False
        save_file(output_file, new_file)
        
    if save_df:
        df.to_pickle(results_data_frame)
    # time.sleep(40)


if __name__ == "__main__":

    alert(input_file, output_file)
