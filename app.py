from typing import List, Union, Tuple

import numpy as np
import gradio as gr

from taiko import (
    TaikoMusic,
    CourseMusic,
    UserInterface
)

def handle(*attributes: List[Union[str, int]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Must return TaikoMusic for each course in reverse order: 
        - Ura, Oni, Hard, Normal, Easy
    """

    # Set every attribute to TaikoMusic from gradio event handler inputs
    taiko = TaikoMusic()
    for attr_name, attr_value in zip(taiko.__dict__.keys(), attributes):
        setattr(taiko, attr_name, attr_value)
    
    # Generate Taiko Music
    try:
        music: CourseMusic = taiko.generate_taiko_music()
    except Exception as e:
        raise gr.Error(e)
    
    return music.ura, music.oni, music.hard, music.normal, music.easy

if __name__ == "__main__":
    app = UserInterface(event_handler=handle)
    app.launch()
