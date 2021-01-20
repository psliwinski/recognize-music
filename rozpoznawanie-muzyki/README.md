required Python version: 3.6
install file 'install.txt'
"pip install -r install.txt"
go to windows powershell and install ffmpeg
"choco install ffmpeg"
send some mp3s to songs folder

program handling
create descriptors: run create_descriptors.py 
music recognition: "python recognize_songs.py -g -s [seconds]" or modify run configurations
-g flag is optional, it decides whether sound will be recorded from mic or from speakers (pc's screen)
database reset: run reset.py
statistics: run statistics.py
