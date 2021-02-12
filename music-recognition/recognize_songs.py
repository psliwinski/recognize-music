import argparse
import sys
import numpy as np

from itertools import zip_longest
from libs.descriptor import DescriptorCreator
from libs.database import SqliteDb
from libs.read_stream import StreamReader


def scale(int_datax):
    mean_peak = np.average(np.abs(int_datax)) * 2
    amp_scale = "#" * int(400 * mean_peak / 2 ** 16)
    return mean_peak, amp_scale


def group_matches(matchesx):
    offset_dict = {}
    max_offset = 0
    offset_confidence = 0
    song_id = -1

    for matches_tuple in matchesx:
        sid, offset = matches_tuple
        if offset not in offset_dict:
            offset_dict[offset] = {}
        if sid not in offset_dict[offset]:
            offset_dict[offset][sid] = 0
        offset_dict[offset][sid] += 1
        if offset_dict[offset][sid] > offset_confidence:
            max_offset = offset
            offset_confidence = offset_dict[offset][sid]
            song_id = sid
    song_name = db.find_song_by_id(song_id)
    max_offset_time = max_offset * dc.fft_window_size * dc.window_overlap_ratio / dc.sampling_frequency
    return {
        "SONG_ID": song_id,
        "SONG_NAME": song_name[1],
        "OFFSET": max_offset,
        "OFFSET_TIME": max_offset_time
    }


def key_grouper(iterable, n):
    argsx = [iter(iterable)] * n
    return (filter(None, values)
            for values in zip_longest(fillvalue=None, *argsx))


def search_for_matches(ch_samples):
    hashes_tuple = dc.descriptor(ch_samples)
    return fetch_matches(hashes_tuple)


def fetch_matches(hashes_tuple):
    hashes_dict = {}
    sum_keys = 0
    for hashx, offset in hashes_tuple:
        hashes_dict[hashx] = offset
    hashes_keys = hashes_dict.keys()
    for split_keys in map(list, key_grouper(hashes_keys, 999)):
        query = """
        SELECT hash, song_dk, offset
        FROM descriptors
        WHERE hash IN (%s)
        """
        query = query % ', '.join('?' * len(split_keys))
        fetched_matches = db.execute_all(query, split_keys)
        if len(fetched_matches) > 0:
            if len(hashes_keys) > 999:
                sum_keys += len(split_keys)
                print('   ** znaleziono %d dopasowań haszów (krok %d/%d)' %
                      (len(fetched_matches),
                       sum_keys,
                       len(hashes_keys))
                      )
            else:
                print('   ** znaleziono %d dopasowań haszów (krok %d/%d)' %
                      (len(fetched_matches),
                       len(split_keys),
                       len(hashes_keys))
                      )
        else:
            if len(hashes_keys) > 999:
                sum_keys += len(split_keys)
                print('   ** nie znaleziono dopasowań (krok %d/%d)' % (sum_keys, len(hashes_keys)))
            else:
                print('   ** nie znaleziono dopasowań (krok %d/%d)' % (len(split_keys), len(hashes_keys)))
        for hash_match, sid, offset in fetched_matches:
            if isinstance(offset, bytes):
                offset = np.frombuffer(offset, dtype=np.int)[0]
            yield sid, offset - hashes_dict[hash_match]


if __name__ == '__main__':

    db = SqliteDb()
    dc = DescriptorCreator()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-g', required=False, action="store_true")
    arg_parser.add_argument('-s', nargs='?')

    args = arg_parser.parse_args()
    if args.s is None or not args.s.isdigit():
        sys.exit(0)
    stream_time = int(args.s)

    stream_reader = StreamReader()
    if args.g:
        stream_reader.start_streaming(1)
    else:
        stream_reader.start_streaming(None)
    print(' * nagrywanie...')
    buffers_size = int(stream_reader.rate / stream_reader.chunk * stream_time)
    for i in range(0, buffers_size):
        int_data = stream_reader.process_streaming()
        print('   przetwarzanie %d z %d...' % (i + 1, buffers_size), end='')
        print(('   %05d' + ' %s') % scale(int_data))

    stream_reader.stop_streaming()
    print(' * nagrywanie zakończone')
    split_data = stream_reader.get_streamed_data()
    print(' * nagrano %d próbek' % len(split_data[0] + split_data[1]))

    channel_amount = len(split_data)
    hash_matches = []
    for channel_number, channel_samples in enumerate(split_data):
        print('   tworzenie deskryptorów kanału %d/%d' % (channel_number + 1, channel_amount))
        hash_matches.extend(search_for_matches(channel_samples))
        print('   ukończono kanał %d/%d, istnieje %d haszów' % (channel_number + 1,
                                                                channel_amount, len(hash_matches)))
    if len(hash_matches) > 0:
        print('\n ** razem znaleziono %d dopasowań haszów' % len(hash_matches))
        song = group_matches(hash_matches)
        print((' => utwór: %s (id=%d)\n' + '    zakres: 0-%d (0-%0.2f sekund)\n') %
              (song['SONG_NAME'], song['SONG_ID'],
               song['OFFSET'], song['OFFSET_TIME']))
    else:
        print('\n ** nie znaleziono dopasowań')
