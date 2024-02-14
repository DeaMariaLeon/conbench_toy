from utilities import Environment, alerts_done_file
import benchalerts.pipeline_steps as steps
from benchalerts.integrations.github import CheckStatus
import benchmark_email
import re
import json
# from benchalerts.pipeline_steps.slack import (
#    SlackErrorHandler,
# )
from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import GitHubRepoClient
from benchalerts.conbench_dataclasses import FullComparisonInfo
import pandas as pd
import numpy as np
import pathlib
from datetime import datetime

env = Environment()

repo = env.GITHUB_REPOSITORY


def alert_instance(commit_hash):

    # Create a pipeline to update a GitHub Check
    pipeline = AlertPipeline(
        steps=[
            steps.GetConbenchZComparisonStep(
                commit_hash=commit_hash,
                # baseline_run_type=steps.BaselineRunCandidates.fork_point,
                # baseline_run_type=steps.BaselineRunCandidates.latest_default,
                baseline_run_type=steps.BaselineRunCandidates.parent,
                # z_score_threshold=6.0, #If not set, defaults to 5
            ),
            #steps.GitHubCheckStep(
            #     commit_hash=commit_hash,
            #     comparison_step_name="GetConbenchZComparisonStep",
            #     github_client=GitHubRepoClient(repo=repo),
            # ),
            #steps.SlackMessageAboutBadCheckStep(
            #    channel_id="conbench-poc",
            #    #check_step_name="GetConbenchZComparisonStep",
            # ),

            ],
        # error_handlers=[
        #     steps.GitHubCheckErrorHandler(
        #         commit_hash=commit_hash, repo=repo, #build_url=build_url
        #     )
        # ],
        )
    return pipeline

    # To see the whole report, look at:
    # pipeline.run_pipeline()['GetConbenchZComparisonStep'].results_with_z_regressions


def report(pipeline):
    full_comparison_info = \
        pipeline.run_pipeline()['GetConbenchZComparisonStep']
    alerter = Alerter()
    if alerter.github_check_status(full_comparison_info) == CheckStatus.FAILURE:

        message = """Subject: Benchmarks Alert \n\n """ \
                  + alerter.github_check_summary(full_comparison_info, "")

        # cleaned_message = re.sub(r'0\.0\.0\.0', '127.0.0.1', message)  # local
        correctserver = re.sub(r'0\.0\.0\.0', '57.128.112.95', message)  # new server
        cleaned_message = re.sub(r'- Commit Run.+\)|#| All benchmark runs analyzed:', '', correctserver)
        # send message or cleaned_message
        benchmark_email.email(cleaned_message)


def analyze_pipeline(pipeline, commit, date):
    analysis = pipeline.run_pipeline()['GetConbenchZComparisonStep']
    results_w_z_regressions = analysis.results_with_z_regressions
    columns = [(str(regression.display_name)) for regression in results_w_z_regressions]
    commit_df = pd.DataFrame(data=np.ones((1, len(columns))), index=[commit], columns=columns)  # commit is a list
    commit_df.insert(0, "datetime",[datetime.fromtimestamp(int(date)/1e3)])
    
    return commit_df


def alert() -> None:
    df = pd.DataFrame()
    save_df = False
    #while True:
    with open(env.ASV_PROCESSED_FILES, "r") as f:
        processed_files = f.read().split('\n')
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
            save_df = True
        except:
            print(benchmarks_results['commit_hash'])
            save_df = False
        with open(env.ALERT_PROCESSED_FILES, "a") as f:
            f.write(new_file)
            f.write("\n")
    if save_df:
        df.to_pickle("./out.pkl")
        # time.sleep(40)


if __name__ == "__main__":
    # commit_hash = 'acf5d7d84187b5ba53e54b2a5d91a34725814bf9' #old server
    # commit_hash = 'fce520d45a304ee2659bb4156acf484cee5aea07' #new server
    # commit_hash = "c8a9c2fd3bcf23a21acfa6f4cffbc4c9360b9ea6" #local

    alert()
