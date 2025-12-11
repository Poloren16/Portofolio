# processing/video_processing.py
import numpy as np
import cv2


# fungsi-fungsi filter dasar untuk dipanggil dari exporter


def grayscale(frame):
# frame: BGR numpy array
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def to_bgr_if_gray(frame):
    if len(frame.shape) == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    return frame


def brightness_contrast(frame, brightness=0, contrast=1.0):
    out = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
    return out


def rotate(frame, angle_deg):
    h, w = frame.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle_deg, 1)
    return cv2.warpAffine(frame, M, (w, h))


# wrapper untuk digunakan oleh moviepy: menerima frame RGB -> kembalikan RGB


def apply_effect(frame, effect_name=None, params=None):
    if params is None:
        params = {}
# convert RGB -> BGR
    bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if effect_name == 'grayscale':
        out = grayscale(bgr)
        out = to_bgr_if_gray(out)
    elif effect_name == 'brightness':
        b = params.get('brightness', 30)
        c = params.get('contrast', 1.0)
        out = brightness_contrast(bgr, brightness=b, contrast=c)
    elif effect_name == 'rotate':
        angle = params.get('angle', 90)
        out = rotate(bgr, angle)
    else:
        out = bgr
# convert back to RGB
        rgb = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    return rgb