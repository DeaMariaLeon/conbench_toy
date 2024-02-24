from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import CheckStatus
import benchalerts.pipeline_steps as steps
import benchmark_email
from datetime import datetime, timezone
from dateutil import tz
import json
import numpy as np
import pandas as pd
import re
from utilities import Environment, alerts_done_file

env = Environment()

repo = env.GITHUB_REPOSITORY
asv_processed_files = env.ASV_PROCESSED_FILES
alert_processed_files = env.ALERT_PROCESSED_FILES
RESULTS_DATA_FRAME = "./out.pkl"
REGRESSIONS_DATA_FRAME = "./reg.xlsx"


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

def find_regressions(df, threshold=4):
    df = df.fillna(0)
    df = df.sort_values(by="datetime")
    df = df.drop(columns='datetime')

    df2 = (df.rolling(threshold).sum() == threshold) & (df.rolling(threshold+1).sum() != threshold+1)
    df2 = df2.shift(1 - threshold)
    df2 = df2.where(df2)
    df2 = df2.dropna(axis='columns', how='all')
    df2 = df2.dropna(axis='index', how='all')
    return df2
    
    
def asv_commits_names():
    with open(asv_processed_files, "r") as f:
        processed_files = f.read().split('\n')
    return processed_files

def save_commit_name(new_commit):
    with open(alert_processed_files, "a") as f:
            f.write(new_commit)
            f.write("\n")

def alert() -> None:
    
    #df = pd.DataFrame()
    df = pd.read_pickle(RESULTS_DATA_FRAME)
    save_df = False
    processed_files = asv_commits_names()
    for new_commit in (set(processed_files) - set(alerts_done_file(env))):
        try:
            with open(new_commit, "r") as f:
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
              
        except:
            print(benchmarks_results['commit_hash'])
            
        save_commit_name(new_commit)


    df.to_pickle(RESULTS_DATA_FRAME)
    if len(df):
        df2 = find_regressions(df)
        df2.to_excel(REGRESSIONS_DATA_FRAME)
        # report(pipeline) email report
    # time.sleep(40)


if __name__ == "__main__":

    alert()
