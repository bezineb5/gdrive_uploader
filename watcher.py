import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.utils import unicode_paths
from pathtools.patterns import match_any_paths
from uploader import MotionUploader


class UploaderEventHandler(FileSystemEventHandler):
    patterns = ["*.jpg", "*.mpo", "*.xmp"]

    def __init__(self, root_path, config_file_path):
        super(UploaderEventHandler, self).__init__()
        # Load config
        self.root_path = root_path
        self.config_path = config_file_path

    def on_created(self, event):
        try:
            if event.is_directory:
                # Create directory
                print "Created directory: ", event.src_path
                self._create_dir(event.src_path)
            else:
                paths = []
                if event.src_path:
                    paths.append(unicode_paths.decode(event.src_path))

                if match_any_paths(paths,
                                   included_patterns=self.patterns,
                                   case_sensitive=False):

                    print "Created file: ", event.src_path
                    self._create_file(event.src_path)
        except Exception as e:
            print "Unable to upload change: ", e

    def _create_dir(self, path):
        relative_path = os.path.relpath(path, self.root_path)
        print relative_path
        MotionUploader(self.config_path).create_folder(relative_path)

    def _create_file(self, path):
        relative_path = os.path.relpath(path, self.root_path)
        MotionUploader(self.config_path).upload_photo(relative_path, path)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    event_handler = UploaderEventHandler(path, './uploader.cfg')
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
