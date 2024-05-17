import subprocess
import tempfile
import os
import argparse

def findSilences(filename, noise_tolerance, duration):
    command = ["ffmpeg",
               "-i", filename,
               "-af", "silencedetect=n=" + str(noise_tolerance) +
                      ":d=" + str(duration),
               "-f", "null", "-"]
    output = str(subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE))
    lines = output.replace("\\r", "").split("\\n")

    time_list = []
    for line in lines:
        if ("silencedetect" in line):
            words = line.split(" ")
            for i in range(len(words)):
                if "silence_start" in words[i]:
                    time_list.append(float(words[i + 1]))
                if "silence_end" in words[i]:
                    time_list.append(float(words[i + 1]))

    return time_list

def getVideoDuration(filename: str) -> float:
    command = ["ffprobe", "-i", filename, "-v", "quiet",
               "-show_entries", "format=duration", "-hide_banner",
               "-of", "default=noprint_wrappers=1:nokey=1"]

    output = subprocess.run(command, stdout=subprocess.PIPE)
    s = str(output.stdout, "UTF-8")
    return float(s)

def getSectionsOfNewVideo(silences, duration):
    return [0.0] + silences + [duration]

def ffmpeg_filter_getSegmentFilter(videoSectionTimings, margin):
    ret = ""
    for i in range(int(len(videoSectionTimings) / 2)):
        start = max(videoSectionTimings[2 * i] - margin, videoSectionTimings[0])
        end = min(videoSectionTimings[2 * i + 1] + margin, videoSectionTimings[-1])
        ret += "between(t," + str(start) + "," + str(end) + ")+"
    ret = ret[:-1]
    return ret

def getFileContent_videoFilter(videoSectionTimings, margin):
    ret = "select='"
    ret += ffmpeg_filter_getSegmentFilter(videoSectionTimings, margin)
    ret += "', setpts=N/FRAME_RATE/TB"
    return ret

def getFileContent_audioFilter⬤