import os
import json
import time
from uu import Error
import git
import schedule
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = "config.json"


class ConfigHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        print("config.json changes!")
        if event.src_path.endswith(CONFIG_FILE):
            self.callback()


def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config["folders"]
    except (IOError, KeyError, json.JSONDecodeError):
        print(f"Error loading {CONFIG_FILE} or invalid format.")
        return []


def fetch_updates(folder_path):
    try:
        repo = git.Repo(folder_path)
        print(f"Fetching updates for {folder_path}")
        repo.remotes.origin.fetch()
        print(f'----> Successfully fetched updates for {folder_path}')
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
    print('Starting Auto fetcher...')
    auto_fetch()

    event_handler = ConfigHandler(auto_fetch)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    schedule.every(5).minutes.do(auto_fetch)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
