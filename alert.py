import os
import sys
from dotenv import load_dotenv
import socket
import benchalerts.pipeline_steps as steps
from benchalerts.integrations.github import CheckStatus
import benchmark_email
import re
#from benchalerts.pipeline_steps.slack import (
#    SlackErrorHandler,
#)
from benchalerts import AlertPipeline, Alerter
from benchalerts.integrations.github import GitHubRepoClient
import asvbench
from benchalerts.conbench_dataclasses import FullComparisonInfo
import pandas as pd

if socket.gethostname().startswith('Deas'):
      load_dotenv(dotenv_path="./local_env.yml")
else:
      load_dotenv(dotenv_path="./server_env.yml")

repo = os.getenv("GITHUB_REPOSITORY")

def alert(commit_hash):

    # Create a pipeline to update a GitHub Check
    pipeline = AlertPipeline(
        steps=[
            steps.GetConbenchZComparisonStep(
                commit_hash=commit_hash,
                #baseline_run_type=steps.BaselineRunCandidates.fork_point,
                #baseline_run_type=steps.BaselineRunCandidates.latest_default,
                baseline_run_type=steps.BaselineRunCandidates.parent,
                z_score_threshold=5.1, #If not set it defaults to 5
            ),
            #steps.GitHubCheckStep(
            #    commit_hash=commit_hash,
            #    comparison_step_name="GetConbenchZComparisonStep",
            #    github_client=GitHubRepoClient(repo=repo),
            #    #build_url=build_url,
            #),
            #steps.SlackMessageAboutBadCheckStep(
            #   channel_id="conbench-poc",
            #),

        ],
        #error_handlers=[
        #    steps.GitHubCheckErrorHandler(
        #        commit_hash=commit_hash, repo=repo, #build_url=build_url
        #    )
        #],
    )
    
    # Run the pipeline
    # data = pipeline.run_pipeline()['GetConbenchZComparisonStep'].results_with_z_regressions

    full_comparison_info = pipeline.run_pipeline()['GetConbenchZComparisonStep']
    alerter = Alerter()
    if alerter.github_check_status(full_comparison_info) == CheckStatus.FAILURE:
        
        message = """Subject: Benchmarks Alert \n\n """ \
                  + alerter.github_check_summary(full_comparison_info, "")
        #TODO add links to message
        #github_check_summary() returns links to comparison: very slow
        #cleaned_message = re.sub(r'\(http.*', '', message)
        #cleaned_message = re.sub(r'0\.0\.0\.0', '127.0.0.1', message) #local
        cleaned_message = re.sub(r'0\.0\.0\.0', '57.128.112.95', message) #new server
       
        #send message or cleaned_message
        benchmark_email.email(cleaned_message)

if __name__ == "__main__":
    #commit_hash = 'acf5d7d84187b5ba53e54b2a5d91a34725814bf9' #old server
    commit_hash = 'fce520d45a304ee2659bb4156acf484cee5aea07' #new server
    #commit_hash = "c8a9c2fd3bcf23a21acfa6f4cffbc4c9360b9ea6" #local
    alert(commit_hash)