import numpy as np
import pyaudio


class StreamReader:
    sampling_rate = 44100
    init_channels = 2
    init_format = pyaudio.paInt16
    init_chunk = 4096

    def __init__(self):
        self.rate = StreamReader.sampling_rate
        self.chunk = StreamReader.init_chunk
        self.channels = StreamReader.init_channels
        self.split_data = []
        self.device_index = None
        self.stream = None
        self.port_audio = pyaudio.PyAudio()

    def start_streaming(self, arg):
        if arg == 1:
            for i in range(self.port_audio.get_device_count()):
                a = self.port_audio.get_device_info_by_index(i)['name'].lower()
                if any(x in a for x in ["stereo", "glosnik", "speakers"]):
                    self.device_index = self.port_audio.get_device_info_by_index(i)['index']
                    break
        self.stream = self.port_audio.open(
            frames_per_buffer=self.chunk,
            input=True,
            rate=self.rate,
            channels=self.channels,
            format=self.init_format,
            input_device_index=self.device_index
        )
        self.split_data = [[] for _ in range(self.channels)]

    def process_streaming(self):
        raw_byte_data = self.stream.read(self.chunk)
        int_data = np.fromstring(raw_byte_data, np.int16)
        for c in range(self.channels):
            self.split_data[c].extend(int_data[c::self.channels])
        return int_data

    def stop_streaming(self):
        self.stream.stop_stream()
        self.stream.close()

    def get_streamed_data(self):
        return self.split_data