# Lyric Syncer
A tool to manually timestamp lyrics to a song and export a karaoke video using the instrumental version

## Setup

### Depedencies:
```
python
tkinter
```

### Create a venv
```bash
python -m venv venv
```

### Activate it
```bash
source venv/bin/activate
```

### Install requirements
```bash
pip install -r requirements.txt
```
or
```bash
pip install numpy pygame moviepy pillow
```

### Start
```bash
python main.py
```

## How to use it

You need three files:
- **Lyrics** (.txt): Each lyric paragraph separated by blank lines
- **Vocal audio**: The original song to time against
- **Instrumental audio**: Instrumental for the final video

Example lyrics format:
```
First line of first paragraph
Second line of first paragraph
Third line of first paragraph

First line of second paragraph
Second line of second paragraph

More lyrics...
```

### Creating the video

1. Load all three files
2. Hit "Start Playback": The vocal track starts
3. Click "Mark Timestamp / Next" to timestamp the current paragraph and move to the next one
4. After timestamping all the lyrics you can export the video.

The final video shows the current lyric on the top and the next on the bottom.
It's synced to the manually set timestamps

The final video displays the current lyric at the top with a preview of the next line below, 
all timed to your manually marked timestamps.