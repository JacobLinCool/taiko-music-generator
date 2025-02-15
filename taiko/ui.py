from typing import List

import gradio as gr

from .taiko import (
    TaikoMusic,
    SHEET_BRANCH,
    DEFAULT_HIT_PER_SEC,
    DEFAULT_SOUND_VOLUME
)

SOURCE_CODE_GH_URL = "https://github.com/ryanlinjui/taiko-music-generator"
BADGE_URL = "https://img.shields.io/badge/GitHub_Code-Click_Here!!-default?logo=github"
TAIKO_OFFICIAL_URL = "https://taiko.namco-ch.net/taiko/howto/onpu.php#onpu"
EXAMPLE_SONG_LIST = ["Blue Rose Ruin", "千本桜", "さいたま2000", "百花繚乱", "第六天魔王"]

def UserInterface(event_handler: callable) -> gr.Interface:
    files = []
    settings = []
    taiko = TaikoMusic()

    with gr.Blocks(delete_cache=(86400, 86400)) as gradio_interface:
        gr.Markdown("> For Neokent NTNU CP2, click [here](https://huggingface.co/spaces/ryanlinjui/ntnucp2-taiko-music-generator) <br> Verify tja format by [TJA Tools](https://whmhammer.github.io/tja-tools/)")
        gr.Markdown("# 太鼓の達人音楽ジェネレーター (Taiko Music Generator)")

        # split the interface into two columns: input files and settings, and music player
        with gr.Row():

            # gradio column block: input files and settings
            with gr.Column():
                gr.HTML(f'<a target="_blank" href="{SOURCE_CODE_GH_URL}"> <img src="{BADGE_URL}" alt="GitHub"/> </a>')
                
                # gradio row block: upload TJA and Song
                with gr.Row(): 
                    with gr.Column():
                        gr.Markdown("## 🎼 太鼓の達人 TJA 譜面")
                        taiko.tja_file = gr.File(label="tja", file_types=[".tja"])
                    with gr.Column():
                        gr.Markdown("## 🎙️ 楽曲 Song (Optional)")
                        taiko.song_file = gr.File(label="ogg/mp3", file_types=[".ogg", ".mp3"])

                # gradio row block: advanced settings
                with gr.Row():
                    with gr.Accordion("詳細設定 / Advance Settings", open=False):
                        taiko.sheet_branch = gr.Dropdown(label="譜面分歧 / Sheet Branch", choices=list(SHEET_BRANCH.keys()), value=list(SHEET_BRANCH.keys())[-1], interactive=True)
                        taiko.per_hits_second = gr.Number(label="連打/秒 (DrumRoll hits per seconds)", minimum=0, maximum=100, value=DEFAULT_HIT_PER_SEC, interactive=True)
                        
                        # gradio column block: volume settings
                        with gr.Column():
                            gr.Markdown("音量設定 / Volume Settings")
                            
                            with gr.Column():
                                taiko.song_sound_volume = gr.Slider(label="楽曲 / Song", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                        
                            with gr.Column():
                                taiko.don_sound_volume = gr.Slider(label="ドン / Don", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.ka_sound_volume = gr.Slider(label="カツ / Ka", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                            
                            with gr.Column():    
                                taiko.big_don_sound_volume = gr.Slider(label="ドン(大) / Big Don", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.big_ka_sound_volume = gr.Slider(label="カツ(大) / Big Ka", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)

                            with gr.Column():
                                taiko.drum_roll_sound_volume = gr.Slider(label="連打音符 / Drum Roll", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.big_drum_roll_sound_volume = gr.Slider(label="連打音符(大) / Big Drum Roll", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)

                            with gr.Column():
                                taiko.balloon_sound_volume = gr.Slider(label="風船音符 / Balloon", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.balloon_bang_sound_volume = gr.Slider(label="破裂音 / Balloon Bang", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)

                            with gr.Column():
                                taiko.party_popper_sound_volume = gr.Slider(label="くすだま音符 / Party Popper", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.party_popper_success_volume = gr.Slider(label="成功音 / Party Popper Success", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                                taiko.party_popper_failure_volume = gr.Slider(label="失敗音 / Party Popper Failure", minimum=0, maximum=10, value=DEFAULT_SOUND_VOLUME, interactive=True, step=1)
                            
                            gr.Markdown(f"> [音符の種類 / Taiko Notes]({TAIKO_OFFICIAL_URL})")
                
                with gr.Column():
                    # gradio row block: generate music button
                    with gr.Row():
                        generate_music_button = gr.Button("🥁 音楽を生成する / Generate Music", variant="primary")
                    
                    # gradio row block: examples
                    with gr.Row():
                        gr.Examples(
                            examples=[[f"examples/{song}/{song}.tja", f"examples/{song}/{song}.ogg"] for song in EXAMPLE_SONG_LIST],
                            inputs=[taiko.tja_file, taiko.song_file],
                            label="例 / Examples (Click it!)"
                        )
                    
            # gradio column block: music player
            with gr.Column():
                music = [gr.Audio(label=course, format="mp3", interactive=False) for course in 
                    [
                        "裏 / Ura",
                        "おに / 魔王 / Oni",
                        "むずかしい / 樹(困難) / Hard",
                        "ふつう / 竹子(普通) / Normal",
                        "かんたん / 梅花(簡單) / Easy"
                    ]
                ]

        generate_music_button.click(
            fn=event_handler,
            inputs=[value for key, value in vars(taiko).items()],
            outputs=music
        )

    return gradio_interface