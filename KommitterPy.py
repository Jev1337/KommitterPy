import json
from pathlib import Path
from typing import Dict, Any
import requests
from datetime import datetime


# Constants
CONFIG_FILE = 'config.json'
GITHUB_API_BASE = "https://api.github.com"


def load_config() -> Dict[str, str]:
    """Load configuration from JSON file."""
    config_path = Path(CONFIG_FILE)
    with config_path.open('r', encoding='utf-8') as file:
        return json.load(file)


def make_github_request(method: str, endpoint: str, config: Dict[str, str], 
                        json_data: Dict[str, Any] = None) -> requests.Response:
    """Make authenticated request to GitHub API with error handling."""
    url = f"{GITHUB_API_BASE}/repos/{config['github_username']}/{config['github_repo_name']}/{endpoint}"
    headers = {
        'Authorization': f"token {config['github_token']}",
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.request(method, url, headers=headers, json=json_data, timeout=30)
    response.raise_for_status()
    return response


def get_last_sha(config: Dict[str, str]) -> str:
    """Get the SHA of the last commit on the specified branch."""
    endpoint = f"branches/{config['github_branch']}"
    response = make_github_request('GET', endpoint, config)
    return response.json()["commit"]["sha"]


def create_blob(config: Dict[str, str]) -> str:
    """Create a blob with auto-generated content."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"This is an auto commit from KommitterPy at {timestamp}."
    
    blob_data = {
        "content": content,
        "encoding": "utf-8"
    }
    
    response = make_github_request('POST', 'git/blobs', config, blob_data)
    return response.json()["sha"]


def create_tree(config: Dict[str, str], blob_sha: str, base_tree_sha: str) -> str:
    """Create a tree object with the blob."""
    tree_data = {
        "base_tree": base_tree_sha,
        "tree": [{
            "path": config["github_file_path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }]
    }
    
    response = make_github_request('POST', 'git/trees', config, tree_data)
    return response.json()["sha"]


def create_commit(config: Dict[str, str], tree_sha: str, parent_sha: str) -> str:
    """Create a commit with the tree."""
    commit_data = {
        "message": config["github_commit_message"],
        "tree": tree_sha,
        "parents": [parent_sha]
    }
    
    response = make_github_request('POST', 'git/commits', config, commit_data)
    return response.json()["sha"]


def update_ref(config: Dict[str, str], commit_sha: str) -> None:
    """Update the branch reference to point to the new commit."""
    endpoint = f"git/refs/heads/{config['github_branch']}"
    ref_data = {"sha": commit_sha}
    make_github_request('PATCH', endpoint, config, ref_data)

def main() -> None:
    """Main function to orchestrate the commit process."""
    try:
        print("=== KommitterPy ===\n")
        
        # Load configuration
        config = load_config()
        print("Configuration loaded:")
        print(json.dumps(config, indent=4, sort_keys=True))
        
        # Get last commit SHA
        print("\nGetting last SHA...")
        last_sha = get_last_sha(config)
        print(f"Last SHA: {last_sha}")
        
        # Create blob
        print("\nCreating blob...")
        blob_sha = create_blob(config)
        print(f"Blob SHA: {blob_sha}")
        
        # Create tree
        print("\nCreating tree...")
        tree_sha = create_tree(config, blob_sha, last_sha)
        print(f"Tree SHA: {tree_sha}")
        
        # Create commit
        print("\nCreating commit...")
        commit_sha = create_commit(config, tree_sha, last_sha)
        print(f"Commit SHA: {commit_sha}")
        
        # Update reference
        print("\nUpdating branch reference...")
        update_ref(config, commit_sha)
        
        print("\n✓ Done! Commit successfully created and pushed.")
        
    except FileNotFoundError:
        print(f"Error: '{CONFIG_FILE}' not found.")
        print("\nPlease create a config.json file with the following structure:")
        example_config = {
            "github_token": "<your github token>",
            "github_username": "<your github username>",
            "github_repo_name": "<your github repo name>",
            "github_branch": "<your github branch>",
            "github_file_path": "<your github file path>",
            "github_commit_message": "<your github commit message>"
        }
        print(json.dumps(example_config, indent=4))
        
    except requests.exceptions.HTTPError as e:
        print(f"GitHub API Error: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        
    except KeyError as e:
        print(f"Configuration Error: Missing required field {e}")
        
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()

