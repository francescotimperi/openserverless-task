SKIPDIR = ["virtualenv", "node_modules", "__pycache__"]

import os, time
from subprocess import Popen
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .deploy import deploy

class ChangeHandler(FileSystemEventHandler):
    """Logs all the events captured."""
    
    last_modified = {}

    def on_any_event(self, event):
        
        ## filter what is needed
        # only modified
        if event.event_type != "modified": return
        # no directories
        if event.is_directory: return
        src = event.src_path
        # no missing files
        if not os.path.exists(src): return
        # no generated directories
        for dir in src.split("/")[:-1]:
            if dir in SKIPDIR: return
        # no generated files
        if src.endswith(".zip"): return

        # cache last modified to do only once
        cur = os.path.getmtime(src)
        if self.last_modified.get(src, 0) == cur:
            return
        self.last_modified[src] = cur
        deploy(src)

def watch():
    observer = Observer()
    event_handler = ChangeHandler()
    observer.schedule(event_handler, "packages", recursive=True)
    #observer.schedule(event_handler, "web", recursive=True)
    observer.start()
    try:
        serve()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# serve web area
def serve():
    Popen("nuv ide serve", shell=True, env=os.environ)