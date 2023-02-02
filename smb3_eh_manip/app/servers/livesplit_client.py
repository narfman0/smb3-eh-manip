import logging
from multiprocessing import Process, Value
import socket
import time
import win32file, win32pipe

from smb3_eh_manip.util import events, settings
from smb3_eh_manip.util.logging import initialize_logging

LIVESPLIT_REQUEST_FREQUENCY = settings.get_float(
    "livesplit_request_frequency", fallback=0.25
)


def client_process(split_index_value: Value):
    initialize_logging(
        console_log_level="DEBUG",
        file_log_level="DEBUG",
        filename="livesplit_client.log",
    )
    handle = win32file.CreateFile(
        r"\\.\pipe\LiveSplit",
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_ATTRIBUTE_NORMAL,
        None,
    )
    res = win32pipe.SetNamedPipeHandleState(
        handle, win32pipe.PIPE_READMODE_BYTE, None, None
    )
    if res == 0:
        print(f"SetNamedPipeHandleState return code: {res}")
    while True:
        win32file.WriteFile(handle, b"getsplitindex\r\n")
        result, data = win32file.ReadFile(handle, 65536)
        if result == 0:
            split_index_value.value = int(data.decode("utf-8").strip())
        time.sleep(LIVESPLIT_REQUEST_FREQUENCY)


class LivesplitClient:
    def __init__(self):
        self.last_split_index = -1
        self.split_index_value = Value("i", self.last_split_index)
        self.process = Process(
            target=client_process,
            args=(self.split_index_value,),
        )
        self.process.daemon = True
        self.process.start()

    def tick(self):
        split_index = self.split_index_value.value
        if split_index != self.last_split_index:
            logging.info(
                f"Livesplit client detected split change from {self.last_split_index} to {split_index}"
            )
            events.emit(
                self,
                events.LivesplitCurrentSplitIndexChanged(
                    split_index,
                    self.last_split_index,
                ),
            )
            self.last_split_index = split_index


if __name__ == "__main__":
    initialize_logging(
        console_log_level="DEBUG",
        file_log_level="DEBUG",
        filename="livesplit_client.log",
    )
    client = LivesplitClient()

    while True:
        client.tick()
        time.sleep(1)
