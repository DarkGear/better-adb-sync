from typing import Iterable, Tuple
import os
import subprocess
import sys

from ..SAOLogging import logging_fatal

from .Base import FileSystem

class LocalFileSystem(FileSystem):
    @property
    def sep(self) -> str:
        return os.path.sep

    def unlink(self, path: str) -> None:
        os.unlink(path)

    def rmdir(self, path: str) -> None:
        os.rmdir(path)

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok = True)

    def realpath(self, path: str) -> str:
        return os.path.realpath(path)

    def lstat(self, path: str) -> os.stat_result:
        return os.lstat(path)

    def lstat_in_dir(self, path: str) -> Iterable[Tuple[str, os.stat_result]]:
        for filename in os.listdir(path):
            yield filename, self.lstat(self.join(path, filename))

    def utime(self, path: str, times: Tuple[int, int]) -> None:
        os.utime(path, times)

    def join(self, base: str, leaf: str) -> str:
        return os.path.join(base, leaf)

    def split(self, path: str) -> Tuple[str, str]:
        return os.path.split(path)

    def normpath(self, path: str) -> str:
        return os.path.normpath(path)

    def push_file_here(self, source: str, destination: str, show_progress: bool = False) -> None:
        proc = subprocess.run(self.adb_arguments + ["pull", source, destination], stdout = sys.stdout if show_progress else subprocess.DEVNULL, stderr = subprocess.PIPE, encoding = "utf-8", text = True)

        try:
            proc.check_returncode()
        except subprocess.SubprocessError as e:
            final_err = e.stderr.strip()

            if self.RE_ADB_PERMISSION_ERROR.fullmatch(final_err):
                raise PermissionError
            
            logging_fatal("Non-zero exit code from adb pull")
