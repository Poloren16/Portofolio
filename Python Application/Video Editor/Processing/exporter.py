# processing/exporter.py
from moviepy.editor import VideoFileClip, AudioFileClip
from .video_processing import apply_effect
import os


def render_with_effects(input_video_path, effect_name=None, progress_cb=None, out_path=None):
    if out_path is None:
        base, ext = os.path.splitext(input_video_path)
        out_path = base + f'_edited{ext}'
        clip = VideoFileClip(input_video_path)
        if effect_name and effect_name != 'none':
            params = {}
                def frame_fx(frame):
        return apply_effect(frame, effect_name=effect_name, params=params)
            new_clip = clip.fl_image(frame_fx)
        else:
            new_clip = clip


new_clip.write_videofile(out_path, audio=True, verbose=False, logger=None)


if progress_cb:
progress_cb(1.0)


return out_path