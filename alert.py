import os
import sys
from dotenv import load_dotenv
import socket
import benchalerts.pipeline_steps as steps
from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import GitHubRepoClient
import asvbench
from benchalerts.conbench_dataclasses import FullComparisonInfo
import pandas as pd

load_dotenv(dotenv_path="./local_env.yml")

#commit_hash = os.environ["GITHUB_SHA"]
#commit_hash = "c8a9c2fd3bcf23a21acfa6f4cffbc4c9360b9ea6"
#commit_hash = "007310665f8e2741ac5694f05d9412bbe6e326e8"

repo = os.getenv("GITHUB_REPOSITORY")

#build_url = (
#    "https://github.com" #os.environ["GITHUB_SERVER_URL"]
#    + f"/{repo}/actions/runs/"
#    #+ "7289196759" #os.environ["GITHUB_RUN_ID"]
#    + "7323312613"
#)
def alert(commit_hash):

    # Create a pipeline to update a GitHub Check
    pipeline = AlertPipeline(
        steps=[
            steps.GetConbenchZComparisonStep(
                commit_hash=commit_hash,
                #baseline_run_type=steps.BaselineRunCandidates.fork_point,
                #baseline_run_type=steps.BaselineRunCandidates.latest_default,
                baseline_run_type=steps.BaselineRunCandidates.parent,
                z_score_threshold=1, #If not set it defaults to 5
            ),
            #steps.GitHubCheckStep(
            #    commit_hash=commit_hash,
            #    comparison_step_name="GetConbenchZComparisonStep",
            #    github_client=GitHubRepoClient(repo=repo),
            #    #build_url=build_url,
            #),
        ],
        error_handlers=[
            steps.GitHubCheckErrorHandler(
                commit_hash=commit_hash, repo=repo, #build_url=build_url
            )
        ],
    )
    
    # Run the pipeline
    #print(pipeline.run_pipeline())
    data = pipeline.run_pipeline()['GetConbenchZComparisonStep'].results_with_z_regressions
    df = pd.DataFrame.from_dict(data=data)
    print(df.head())
    

if __name__ == "__main__":
    commit_hash = "c8a9c2fd3bcf23a21acfa6f4cffbc4c9360b9ea6"
    alert(commit_hash)