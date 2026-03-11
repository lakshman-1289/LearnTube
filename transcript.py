from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):

    transcript = YouTubeTranscriptApi().fetch(video_id)

    transcript_list = transcript.to_raw_data()

    transcript_text = ""
    timestamps = []

    for entry in transcript_list:

        transcript_text += entry["text"] + " "

        timestamps.append((entry["start"], entry["text"]))

    return transcript_text, timestamps