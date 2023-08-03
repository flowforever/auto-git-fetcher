import os
import json
import time
from datetime import datetime
from uu import Error
import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = "config.json"

def get_now():
    return datetime.now().strftime("%H:%M:%S - %Y/%m/%d")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config["folders"]
    except (IOError, KeyError, json.JSONDecodeError):
        print(f"{get_now()} Error loading {CONFIG_FILE} or invalid format.")
        return []


def fetch_updates(folder_path):
    try:
        repo = git.Repo(folder_path)
        for remote in repo.remotes:
            print(f'{{"url": "{remote.url}", "folder": "{os.path.basename(folder_path)}" }}')
        if repo.is_dirty():
            print(f"{get_now()} Fetching updates for {folder_path}")
            repo.remotes.origin.fetch()
            print(f'----> Successfully fetched updates for {folder_path}')
        else:
            # pull updates
            print(f"{get_now()} Pulling updates for {folder_path}")
            repo.remotes.origin.pull()
            print(f'----> Successfully pulled updates for {folder_path}')
    except Exception as e:
        print(f"----> Failed to fetch updates for {folder_path}")
        print(e)
        pass

def list_subfolders(folder_path):
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    return subfolders

def list_git_projects(folder_path):
    git_projects = []

    dirs = list_subfolders(folder_path)

    for directory in dirs:
        git_dir = os.path.join(folder_path, directory, ".git")
        if os.path.exists(git_dir):
            git_projects.append(os.path.abspath(os.path.join(folder_path, directory)))

    return git_projects

def auto_fetch():
    folders = load_config()
    for folder_path in folders:
        try:
            git_projects = list_git_projects(folder_path)
            for project in git_projects:
                fetch_updates(folder_path=project)
        except Exception as e:
            print(f'Failed to fetch updates for {folder_path}')
            print(e)


def main():
    while True:
        print(f'{get_now()} Starting Auto fetcher...')
        auto_fetch()
        time.sleep(60 * 10)

if __name__ == "__main__":
    main()
