import os
import sys
from dotenv import load_dotenv
import socket
import benchalerts.pipeline_steps as steps
from benchalerts import AlertPipeline
from benchalerts.integrations.github import GitHubRepoClient
import asvbench

load_dotenv(dotenv_path="local_env.yml")


# Pretend we're running on GitHub Actions. Get some environment variables.
# (they may be different for different CI systems)
#commit_hash = os.environ["GITHUB_SHA"]
commit_hash = "9ca24902dd16e53d8586df9f828c27d24138478a"
#repo = os.environ["GITHUB_REPOSITORY"]
repo = "git@github.com:DeaMariaLeon/algos2"
#build_url = (
#    os.environ["GITHUB_SERVER_URL"]
#    + f"/{repo}/actions/runs/"
#    + os.environ["GITHUB_RUN_ID"]
#)

# Create a pipeline to update a GitHub Check
pipeline = AlertPipeline(
    steps=[
        steps.GetConbenchZComparisonStep(
            commit_hash=commit_hash,
            #baseline_run_type=steps.BaselineRunCandidates.fork_point,
            baseline_run_type=steps.BaselineRunCandidates.parent,
        ),
        steps.GitHubCheckStep(
            commit_hash=commit_hash,
            comparison_step_name="GetConbenchZComparisonStep",
            github_client=GitHubRepoClient(repo=repo),
        ),
    ],
    #error_handlers=[
    #    steps.GitHubCheckErrorHandler(
    #        commit_hash=commit_hash, repo=repo, build_url=build_url
    #    )
    #],
)

# Run the pipeline
print(pipeline.run_pipeline())