# KommitterPy

KommitterPy is a Python script that (auto) commits to a GitHub repo.

## Usage

1. Create a config.json file with the following structure:
    
    ```
    {
        "github_token": "<your github token>",
        "github_username": "<your github username>",
        "github_repo_name": "<your github repo name>",
        "github_branch": "<your github branch>",
        "github_file_path": "<your github file path>"
        "github_commit_message": "<your github commit message>"
    }
    ```
2. Run KommitterPy.py
3. Setup with a scheduler (e.g. cron, Windows Task Scheduler)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Mozilla Public License 2.0](https://choosealicense.com/licenses/mpl-2.0/)
