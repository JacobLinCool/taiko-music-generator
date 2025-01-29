from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Literal, Optional

import numpy as np
from pydub import AudioSegment
from tja import parse_tja, PyParsedTJA, PyChart

DON_WAV = "./assets/sound/Don.wav"
KA_WAV = "./assets/sound/Ka.wav"
BIGDON_WAV = "./assets/sound/BigDon.wav"
BALLOON_BANG_WAV = "./assets/sound/Balloon.wav"
PARTY_POPPER_SUCCESS_WAV = "./assets/sound/PartyPopperSuccess.wav"
PARTY_POPPER_FAILURE_WAV = "./assets/sound/PartyPopperFailure.wav"

DEFAULT_HIT_PER_SEC = 30 # drum hits in drumroll, balloon
DEFAULT_SOUND_VOLUME = 5 # for song, taiko notes volume settings

SHEET_BRANCH = {
    "普通譜面 / Normal": "N",
    "玄人譜面 / Expert": "E",
    "達人譜面 / Master": "M",
}

@dataclass
class CourseMusic:
    ura: AudioSegment | Tuple[int, np.ndarray] = field(default_factory=AudioSegment.empty)
    oni: AudioSegment | Tuple[int, np.ndarray] = field(default_factory=AudioSegment.empty)
    hard: AudioSegment | Tuple[int, np.ndarray] = field(default_factory=AudioSegment.empty)
    normal: AudioSegment | Tuple[int, np.ndarray] = field(default_factory=AudioSegment.empty)
    easy: AudioSegment | Tuple[int, np.ndarray] = field(default_factory=AudioSegment.empty)

class TaikoMusic:
    def __init__(self):
        # Input filepath
        self.tja_file : Optional[str] = None
        self.song_file : Optional[str] = None

        # Sheet branch for "普通譜面, 玄人譜面, 達人譜面"
        self.sheet_branch: Optional[str] = None
        
        # DrumRoll hits per seconds
        self.per_hits_second : int = DEFAULT_HIT_PER_SEC
        
        # Volume settings for each elements
        self.song_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.don_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.ka_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.big_don_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.big_ka_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.drum_roll_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.big_drum_roll_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.balloon_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.balloon_bang_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.balloon_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.balloon_bang_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.party_popper_sound_volume : int = DEFAULT_SOUND_VOLUME
        self.party_popper_success_volume : int = DEFAULT_SOUND_VOLUME
        self.party_popper_failure_volume : int = DEFAULT_SOUND_VOLUME

    def generate_taiko_music(self) -> CourseMusic:
        with open(self.tja_file, "r", encoding="utf-8") as f:
            tja_content = f.read()
        
        parsed_tja = parse_tja(tja_content)
        # import objprint
        # with open("parsed_tja.txt", "w") as f:
        #     f.write(objprint.objstr(parsed_tja))
        music = CourseMusic()
        for chart in parsed_tja.charts:
            course = chart.course
            if course in ("Easy", "Normal", "Hard", "Oni", "Ura"):
                setattr(music, course.lower(), self.__process(chart))
        
        return self.__post_process(music)
    
    def __process(self, chart: PyParsedTJA) -> AudioSegment:
        annotated_chart = self.__annotate_sound(chart)
        max_length = int(max([start_time + len(self.__adjust_audio(file_path, target_duration=1, target_amplitude=-20))
                            for file_path, start_time in annotated_chart]))
        mixed_audio = np.zeros(max_length)

        for file_path, start_time in annotated_chart:
            audio = self.__adjust_audio(file_path, target_duration=0.5, target_amplitude=-20)
            audio_array = np.array(audio.get_array_of_samples())
            start_index = int(start_time * audio.frame_rate)
            end_index = start_index + len(audio_array)

            if len(mixed_audio) < end_index:
                mixed_audio = np.pad(mixed_audio, (0, end_index - len(mixed_audio)))

            mixed_audio[start_index:end_index] += audio_array

        mixed_audio = np.clip(mixed_audio, -32768, 32767)
        mixed_audio_segment = AudioSegment(
            mixed_audio.astype(np.int16).tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=2,
            channels=1
        )

        if self.song_file is None: # Only taiko drum sound
            return mixed_audio_segment
        
        else:
            if self.song_file.endswith(".mp3"):
                background_music = AudioSegment.from_mp3(self.song_file)
            elif self.song_file.endswith(".ogg"):
                background_music = AudioSegment.from_ogg(self.song_file)
            else:
                raise ValueError("Unsupported file format. Please provide mp3 or ogg file.")
            
            mixed_audio_with_bg = background_music.overlay(mixed_audio_segment)
            return mixed_audio_with_bg

    def __annotate_sound(self, chart: PyChart) -> List[Tuple[str, float]]:
        annotated_chart = []
        balloon_list = chart.balloons

        for segment in chart.segments:
            if not (segment.branch != SHEET_BRANCH[self.sheet_branch] or segment.branch is not None):
                continue            
            for i, note in enumerate(segment.notes):
                note_type = note.note_type
                timestamp = note.timestamp
                
                if note_type in {"Don", "DonBig"}:
                    annotated_chart.append((DON_WAV, timestamp))
                
                elif note_type in {"Ka", "KaBig"}:
                    annotated_chart.append((KA_WAV, timestamp))
                
                elif note_type in {"Roll", "RollBig"}:
                    end_time = next((n.timestamp for n in segment.notes[i+1:] if n.note_type == "EndOf"), timestamp)
                    time_count = timestamp
                    while time_count < end_time:
                        annotated_chart.append((DON_WAV, time_count))
                        time_count += (1 / self.per_hits_second)
                
                elif note_type in {"Balloon", "BalloonAlt"}:
                    end_time = next((n.timestamp for n in segment.notes[i+1:] if n.note_type == "EndOf"), timestamp)
                    time_count = timestamp
                    balloon_count = 0
                    while time_count < end_time and balloon_count < balloon_list[0]:
                        annotated_chart.append((DON_WAV, time_count))
                        time_count += (1 / self.per_hits_second)
                        balloon_count += 1

                    if balloon_count >= balloon_list[0]:
                        if note_type == "Balloon":
                            annotated_chart.append((BALLOON_BANG_WAV, timestamp))
                        elif note_type == "BalloonAlt":
                            annotated_chart.append((PARTY_POPPER_SUCCESS_WAV, timestamp))
                    else:
                        annotated_chart.append((BALLOON_BANG_WAV, timestamp))
                    
                    balloon_list.pop(0)
                        
        return annotated_chart


    def __adjust_audio(self, file_path: str, target_duration: int, target_amplitude: int) -> AudioSegment:
        audio = AudioSegment.from_wav(file_path)
        audio = audio[:target_duration * 1000]

        if file_path == DON_WAV or file_path == BALLOON_BANG_WAV:
            return audio

        audio = audio - (audio.dBFS - target_amplitude)
        return audio

    def __post_process(self, music: CourseMusic) -> CourseMusic:
        def segment_to_tuple(seg: AudioSegment) -> Tuple[int, np.ndarray]:
            return (seg.frame_rate, np.array(seg.get_array_of_samples()))

        music.ura = segment_to_tuple(music.ura)
        music.oni = segment_to_tuple(music.oni)
        music.hard = segment_to_tuple(music.hard)
        music.normal = segment_to_tuple(music.normal)
        music.easy = segment_to_tuple(music.easy)

        return music