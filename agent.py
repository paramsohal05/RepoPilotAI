from google.adk.agents.llm_agent import Agent

import os
import requests
import json
import sys


GITHUB_USERNAME=os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")


def create_git_repo(repo_name:str, description:str='', private:bool=True):
    """
    Create a github repository with the given name, description, and privacy setting.
    This function uses the GitGub API to create a new repository under the authenticated user's account.

    Args:
        repo_name(str): The name of the repository to create.
        description(str): A brief description of the repository if not provided, use deafult empty string.
        private(bool): Wheather the repository should be private. Default is True.

    """
    api_url=f"https://api.github.com/user/repos"

    headers={
        "Authorization":f"token {GITHUB_TOKEN}",
        "Accept":"application/vnd.github.v3+json"
    }

    data={
        "name":repo_name,
        "description":description,
        "private":private,
        "auto_init":False
    }

    print(f"Creating respository '{repo_name}'...")

    try:
        response=requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        repo_data=response.json()
        print(f"Repositoey '{repo_name}' created succesfully at '{repo_data['html_url']}")
        print("Use the following commands to link the local repository:")
        print(f"git remote add origin '{repo_data['clone_url']}'")
        print("git push -u origin main")
    
    except requests.exceptions.HTTPError as error :
        if error.response.status_code==422 :
            print(f"Repository '{repo_name}' already exists.", file=sys.stderr)
        else :
            print(f"HTTP error occurred: '{error}", file=sys.stderr)
    except requests.exceptions.RequestException as err:
        print(f"Error Occurred: '{err}'", file=sys.stderr)
    
    except Exception as e: 
        print(f"An unexpected error occurred: '{e}'", file=sys.stderr)

def del_git_repo(repo_name:str):
    """
     Delete a github repository with the given name. 
     Args:
        repo_name(str): The name of the repository to delete.
    """
    if not GITHUB_USERNAME :
        print(f"Error: Github username is not set in environment variables.", file=sys.stderr)
        return 
    
    if not GITHUB_TOKEN :
        print(f"Error: Github token is not set in environment variables.", file=sys.stderr)
        return 
    
    api_url=f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    headers={
        "Authorization":f"token {GITHUB_TOKEN}",
        "Accept":"application/vnd.github.v3+json"
    }
    
    print(f"Attempting to delete repository '{repo_name}")

    try:
        response=requests.delete(api_url, headers=headers)
        response.raise_for_status()

        if response.status_code==204 :
            print(f"Repository '{repo_name}' deleted successfully.")
    
    except requests.exceptions.HTTPError as error :
        if error.response.status_code==404 :
            print(f"Error: Repository '{repo_name}' not found.", file=sys.stderr)
        elif error.response.status_code==403 :
            print(f"Error: Forbidden. Verify your token permissions to delete the repository.", file=sys.stderr)
        else :
            print(f"HTTP Error: '{error}'", file=sys.stderr)
    except requests.exceptions.RequestException as err:
        print(f"Error Occurred: '{err}'", file=sys.stderr)
    
    except Exception as e:
        print(f"An unexpected error occurred: '{e}'", file=sys.stderr)
    
root_agent = Agent(
    model='gemini-2.5-flash',
    name='github_agent',
    description='An assistant that helps to create and delete github repos.',
    instruction="""
        You are a Github Repository Management specialist that can create and delete github repositories using the provided tools.
        If the user does not specify respository name, description, public/private status, ask them to provide these details. 
        once you receive the details, create repo using tool 'create_git_repo'.
        In case user wants to delete a repository, ask them the repository name and then delete using tool 'del_git_repo'.
        Before deleting repo, always confirm with the user to avoid accidental deletions.
    """,
    tools=[create_git_repo, del_git_repo]
)
