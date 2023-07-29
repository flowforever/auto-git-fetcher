import os
import json
import git
import time


CONFIG_FILE = "config.json"


def read_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config
    except (IOError, KeyError, json.JSONDecodeError):
        print(f"Error loading {CONFIG_FILE} or invalid format.")
        return []


def clone_repository(url, download_path):
    try:
        print(f"Cloning repository from {url} to {download_path}")
        git.Repo.clone_from(url, download_path)
        print(f"Cloned repository from {url} to {download_path}")
    except git.exc.GitCommandError as e:
        if "already exists and is not an empty directory" in str(e):
            print(f"Repository already exists in {download_path}, skipping...")
        else:
            print(f"Failed to clone repository from {url}: {e}")


def main():
    while True:
        config = read_config()
        repositories = config["repositories"]
        default_folder = config["folders"][0]
        for repo in repositories:
            url = repo["url"]
            if url:
                download_path = repo["folder"] if repo["folder"] else default_folder
                clone_repository(url, download_path)

        time.sleep(30)


if __name__ == "__main__":
    main()
