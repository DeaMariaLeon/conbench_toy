from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import CheckStatus
import benchalerts.pipeline_steps as steps
import benchmark_email
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from pathlib import Path
import re
from utilities import Environment, alerts_done_file

env = Environment()

repo = env.GITHUB_REPOSITORY
asv_processed_files = env.ASV_PROCESSED_FILES
alert_processed_files = env.ALERT_PROCESSED_FILES

threshold = 4

results_tail = Path.cwd().joinpath("output", "out.pkl")
output_all_rows = Path.cwd().joinpath("output", "out_all_rows.pkl")  #used for testing
all_links = Path.cwd().joinpath("output", "all_links.pkl") #used for testing
links_tail = Path.cwd().joinpath("output", "links_out.pkl")
cleaned_regression_file = Path.cwd().joinpath("output", "cleaned_regression_file.json")

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


def analyze_pipeline(results_w_z_regressions, commit, date):
    results = [(str(regression.display_name),
                str(regression.link),
                str(regression.run_link),
                ) for regression in results_w_z_regressions]
    links = [[(re.sub(r'0\.0\.0\.0', '57.128.112.95',result[1])) for result in results]]
    columns = [result[0] for result in results]
    links_df = pd.DataFrame(data=links, index=[commit], columns=columns)
    commit_df = pd.DataFrame(data=np.ones((1, len(columns))), index=[commit], columns=columns)  # commit is a list
    commit_df.insert(0, "datetime",[datetime.fromtimestamp(int(date)/1e3, tz=timezone.utc)])

    return commit_df, links_df

def find_regressions(df, threshold=4):
    df2 = df.copy()
    df2 = df2.fillna(0)
    df2 = df2.sort_values(by="datetime")
    df2 = df2.drop(columns='datetime')

    df2 = (df2.rolling(threshold).sum() == threshold) & (df2.rolling(threshold+1).sum() != threshold+1)
    df2 = df2.shift(1 - threshold)
    df2 = df2.where(df2)
    df2 = df2.dropna(axis='columns', how='all')
    df2 = df2.dropna(axis='index', how='all')
    return df2

def clean_dict(df):
    
    return { commit[0]: commit[1].dropna().to_dict() for  commit in df.iterrows()}

def add_regression_links(regressions_df, links_df):
    aligned_reg_df, aligned_links_df = regressions_df.align(links_df, join='left') # use update instead?
    reg_links_df = aligned_links_df.where(aligned_reg_df)
    
    return reg_links_df


def asv_commits_names():
    with open(asv_processed_files, "r") as f:
        processed_files = f.read().split('\n')
    return processed_files

def save_commit_name(new_commit):
    with open(alert_processed_files, "a") as f:
            f.write(new_commit)
            f.write("\n")

def alert(df, links_df) -> None:

    processed_files = asv_commits_names()
    for new_commit in (set(processed_files) - set(alerts_done_file(env))):
        try:
            with open(new_commit, "r") as f:
                benchmarks_results = json.load(f)
        except:
            continue
        pipeline = alert_instance(benchmarks_results['commit_hash'])
        analysis = pipeline.run_pipeline()['GetConbenchZComparisonStep']
        results_w_z_regressions = analysis.results_with_z_regressions
        # report(pipeline) email report
        commit_row, links_row = analyze_pipeline(results_w_z_regressions,
                                     benchmarks_results['commit_hash'],
                                     benchmarks_results['date'],
                                     )
        try:
            df = pd.concat([df, commit_row])
            links_df = pd.concat([links_df, links_row])
              
        except:
            print(benchmarks_results['commit_hash'])
            
        save_commit_name(new_commit)

    df.to_pickle(output_all_rows) #used for testing - remove
    links_df.to_pickle(all_links)
    df.tail(threshold + 1).to_pickle(results_tail)
    links_df.tail(threshold + 1).to_pickle(links_tail)
    if len(df):

        regressions_df = find_regressions(df, threshold)
        reg_links_df = add_regression_links(regressions_df, links_df)

        if len(reg_links_df):
            
            cleaned_reg_links_df = clean_dict(reg_links_df)
            with open(cleaned_regression_file, 'w') as file:
                json.dump(cleaned_reg_links_df, file, indent=4)
            message = """Subject: Benchmarks Alert \n\n """ \
            + json.dumps(cleaned_reg_links_df, indent=4)
            
            benchmark_email.email(message)


if __name__ == "__main__":

    try:
        df = pd.read_pickle(results_tail)
        links_df = pd.read_pickle(links_tail)
    except:
        df = pd.DataFrame()
        links_df = pd.DataFrame()

    alert(df, links_df)
