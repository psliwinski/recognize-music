from pydub import AudioSegment
import numpy as np
from hashlib import sha1


class FileReader:

    def __init__(self, filename):
        self.audiofile_name = filename

    def parse_file_hash(self, byte_block=2 ** 20):
        sha1_object = sha1()
        with open(self.audiofile_name, "rb") as afile:
            while True:
                buffer = afile.read(byte_block)
                if not buffer:
                    break
                sha1_object.update(buffer)
        return sha1_object.hexdigest().upper()

    def parse_audio(self):
        audiofile = AudioSegment.from_file(self.audiofile_name)
        int_data = np.fromstring(audiofile.raw_data, np.int16)
        split_data = []
        for chn in range(audiofile.channels):
            split_data.append(int_data[chn::audiofile.channels])
        result = {
            "song_name": self.audiofile_name,
            "split_data": split_data,
            "Fs": audiofile.frame_rate,
            "file_hash": self.parse_file_hash()
        }
        return result
