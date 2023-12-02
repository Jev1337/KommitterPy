import json
import os
import requests
import datetime


def getConfig() -> dict:
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
        return data

def getLastSHA(config) -> str:
    r = requests.get("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/branches/" + config["github_branch"])
    return r.json()["commit"]["sha"]

def createBlob(config) -> str:
    content = "This is an auto commit from KommitterPy at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "."
    r = requests.post("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/git/blobs", json={"content": content, "encoding": "utf-8"}, headers={'Authorization': 'token ' + config["github_token"]})
    return r.json()["sha"]

def createTree(config, blobSHA, last_sha) -> str:
    r = requests.post("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/git/trees", json={"base_tree": last_sha, "tree": [{"path": config["github_file_path"], "mode": "100644", "type": "blob", "sha": blobSHA}]}, headers={'Authorization': 'token ' + config["github_token"]})
    return r.json()["sha"]

def createCommit(config, treeSHA, last_sha) -> str:
    r = requests.post("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/git/commits", json={"message": config["github_commit_message"], "tree": treeSHA, "parents": [last_sha]}, headers={'Authorization': 'token ' + config["github_token"]})
    return r.json()["sha"]

def updateRef(config, commitSHA):
    r = requests.patch("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/git/refs/heads/" + config["github_branch"], json={"sha": commitSHA}, headers={'Authorization': 'token ' + config["github_token"]})

def updateBranch(config, commitSHA):
    r = requests.patch("https://api.github.com/repos/" + config["github_username"] + "/" + config["github_repo_name"] + "/branches/" + config["github_branch"], json={"sha": commitSHA}, headers={'Authorization': 'token ' + config["github_token"]})

def main():
    try:
        config = getConfig()
        print("KommitterPy")
        print("Config: ")
        print(json.dumps(config, indent=4, sort_keys=True))
        print("Getting last SHA...")
        last_sha = getLastSHA(config)
        print("Last SHA: " + last_sha)
        print("Creating blob...")
        blobSHA = createBlob(config)
        print("Blob SHA: " + blobSHA)
        print("Creating tree...")
        treeSHA = createTree(config, blobSHA, last_sha)
        print("Tree SHA: " + treeSHA)
        print("Creating commit...")
        commitSHA = createCommit(config, treeSHA, last_sha)
        print("Commit SHA: " + commitSHA)
        print("Updating ref...")
        updateRef(config, commitSHA)
        print("Updating branch...")
        updateBranch(config, commitSHA)
        print("Done!")

    except FileNotFoundError as e:
        print("Error: " + str(e))
        print("Please create a config.json file with the following structure:")
        print("{")
        print("    \"github_token\": \"<your github token>\",")
        print("    \"github_username\": \"<your github username>\",")
        print("    \"github_repo_name\": \"<your github repo name>\",")
        print("    \"github_branch\": \"<your github branch>\",")
        print("    \"github_file_path\": \"<your github file path>\"")
        print("    \"github_commit_message\": \"<your github commit message>\"")
        print("}")
    except Exception as e:
        print("Error: " + str(e))

if __name__ == "__main__":
    main()

