import matplotlib.mlab as mlab
import numpy as np

from hashlib import sha1
from operator import itemgetter

from matplotlib import pyplot
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from scipy.ndimage.filters import maximum_filter


class DescriptorCreator:
    descriptor_length = 40
    max_time_distance = 200
    min_time_distance = 0
    neighbourhood_size = 20
    amplitude_minimum = 10
    pairing_descriptors_difference = 15
    window_overlap_ratio = 0.5
    fft_window_size = 4096
    sampling_frequency = 44100

    def __init__(self):
        self.d_length = DescriptorCreator.descriptor_length
        self.max_time = DescriptorCreator.max_time_distance
        self.min_time = DescriptorCreator.min_time_distance
        self.nbh_size = DescriptorCreator.neighbourhood_size
        self.amp_min = DescriptorCreator.amplitude_minimum
        self.difference = DescriptorCreator.pairing_descriptors_difference
        self.overlap = DescriptorCreator.window_overlap_ratio
        self.window = DescriptorCreator.fft_window_size
        self.fs = DescriptorCreator.sampling_frequency

    def create_hashes(self, local_maxima, difference):
        local_maxima.sort(key=itemgetter(1))
        #print(len(local_maxima))
        for i in range(len(local_maxima)):
            for j in range(1, difference):
                if (i + j) < len(local_maxima):

                    frequency1 = local_maxima[i][0]
                    frequency2 = local_maxima[i + j][0]
                    time1 = local_maxima[i][1]
                    time2 = local_maxima[i + j][1]

                    time_delta = time2 - time1
                    if self.min_time <= time_delta <= self.max_time:
                        hash_code = "%s|%s|%s" % (str(frequency1), str(frequency2), str(time_delta))
                        encoded_hash = sha1(hash_code.encode('utf-8'))
                        yield encoded_hash.hexdigest()[0:self.d_length], time1

    def fetch_peaks(self, array_2d, amp_min):
        structure = generate_binary_structure(2, 2)
        neighbourhood = iterate_structure(structure, self.nbh_size)
        local_max_mask = maximum_filter(array_2d,
                                        footprint=neighbourhood) == array_2d
        # y = range(10)
        # a = np.array([np.array(list) for _ in y])
        # print(a)
        background = (array_2d == 0)
        eroded_background = binary_erosion(background, structure=neighbourhood,
                                           border_value=1)
        identified_peaks = local_max_mask ^ eroded_background
        amplitudes = array_2d[identified_peaks]
        j, i = np.where(identified_peaks)
        peaks_tuple = zip(i, j, amplitudes)

        filtered_peaks = [x for x in peaks_tuple if x[2] > amp_min]
        time_index = [x[0] for x in filtered_peaks]
        frequency_index = [x[1] for x in filtered_peaks]

        #fig, ax = pyplot.subplots()
        #ax.imshow(array_2d)
        #ax.scatter(time_index, frequency_index, s=3)
        #ax.set_xlabel('czas(t)')
        #ax.set_ylabel('częstotliwość(Hz)')
        #ax.set_title("Spektrogram")
        #pyplot.gca().invert_yaxis()
        #pyplot.show()

        return zip(frequency_index, time_index)

    def descriptor(self, channel_samples):

        #pyplot.plot(channel_samples)
        #pyplot.title('%d próbek' % len(channel_samples))
        #pyplot.xlabel('czas (t)')
        #pyplot.ylabel('amplituda (A)')
        #pyplot.show()
        #pyplot.gca().invert_yaxis()

        array_2d = mlab.specgram(
            channel_samples,
            noverlap=int(self.window * self.overlap),
            window=mlab.window_hanning,
            Fs=self.fs,
            NFFT=self.window
        )[0]
       # print(array_2d.shape)
        #pyplot.plot(array_2d)
        #pyplot.title('Szybka transformacja Fouriera (FFT)')
        #pyplot.xlabel('częstotliwość (Hz)')
        #pyplot.ylabel('amplituda (A)')
        #pyplot.show()

        np.seterr(divide='ignore')
        array_2d = 10 * np.log10(array_2d)

        array_2d[array_2d == -np.inf] = 0
        local_maxima = list(self.fetch_peaks(array_2d, amp_min=self.amp_min))
        print('   maksima lokalne: %d par (częstotliwość, czas)' % len(local_maxima))

        return self.create_hashes(local_maxima, difference=self.difference)



    #def return_arg(self):
     #   print(self.d_length)
     #   #return self.d_length
