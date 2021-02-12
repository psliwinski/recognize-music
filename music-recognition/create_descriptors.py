import os

from libs.descriptor import DescriptorCreator
from libs.database import SqliteDb
from libs.read_file import FileReader

if __name__ == '__main__':

    db = SqliteDb()
    dc = DescriptorCreator()

    path = "songs/"

    for audiofile_name in os.listdir(path):

        if audiofile_name.endswith(".mp3"):
            file_reader = FileReader(path + audiofile_name)
            audio_parser = file_reader.parse_audio()

            song_id = db.save_song(audiofile_name, audio_parser['file_hash'])
            print((' * %s %s: %s' % ('id=%s', 'kanały=%d', '%s')) %
                  (song_id, len(audio_parser['split_data']), audiofile_name))

            if db.find_song_by_file_hash(audio_parser['file_hash']):
                hash_amount = db.count_song_hashes(song_id)
                if hash_amount > 0:
                    print('   już istnieje (%d haszów)' % hash_amount)
                    continue

            hashes_set = set()

            for channel_number, channel_samples in enumerate(audio_parser['split_data']):
                print('   tworzenie deskryptorów kanału %d/%d' %
                      (channel_number + 1, len(audio_parser['split_data'])))
                channel_hashes_set = set(dc.descriptor(channel_samples))
                print('   ukończono kanał %d/%d,  %d haszów' %
                      (channel_number + 1, len(audio_parser['split_data']), len(channel_hashes_set)))
                hashes_set |= channel_hashes_set

            descriptors_set = []
            for hashx, offsetx in hashes_set:
                offset = int(offsetx)
                descriptors_set.append((song_id, hashx, offset))
            print('   zapisywanie %d haszów do bazy danych' % len(descriptors_set))
            db.save_descriptors(descriptors_set)

