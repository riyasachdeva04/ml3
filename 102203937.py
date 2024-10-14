import os
import sys
from pytubefix import YouTube, Search
from pydub import AudioSegment

OUTPUT_PATH = "downloads"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def download_audio(url, video_num):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        audio_file = os.path.join(OUTPUT_PATH, f"video_{video_num}_{yt.title}.mp3")
        audio_stream.download(output_path=OUTPUT_PATH, filename=f"video_{video_num}_{yt.title}.mp3")
        print(f"Downloaded audio from: {yt.title}")
        
        return audio_file
    except Exception as e:
        print(f"Download Error for {url}: {str(e)}")
        return None

def extract_audio_segment(audio_file, y_seconds):
    try:
        sound = AudioSegment.from_file(audio_file)
        
        extracted_segment = sound[:y_seconds * 1000]  
        
        return extracted_segment
    except Exception as e:
        print(f"Error extracting audio segment: {str(e)}")
        return None

def combine_audio_segments(audio_segments, output_file):
    try:
        combined = AudioSegment.silent(duration=0) 
        for segment in audio_segments:
            combined += segment
        
        combined.export(output_file, format="mp3")
        print(f"Combined audio saved as: {output_file}")
    except Exception as e:
        print(f"Error combining audio segments: {str(e)}")

def download_videos_and_combine_audio(artist_name, n_videos, y_seconds, output_file):
    try:
        if n_videos <= 10:
            print("Error: Number of videos should be greater than 10.")
            return
        if y_seconds <= 20:
            print("Error: Audio duration should be greater than 20 seconds.")
            return

        search = Search(artist_name)
        results = search.results[:n_videos]
        
        if len(results) < n_videos:
            print(f"Error: Only found {len(results)} videos, but {n_videos} were requested.")
            return
        
        audio_segments = []
        
        for i, video in enumerate(results):
            video_url = video.watch_url
            
            audio_file = download_audio(video_url, i+1)
            
            if audio_file:
                segment = extract_audio_segment(audio_file, y_seconds)
                
                if segment:
                    audio_segments.append(segment)
        
        if audio_segments:
            combine_audio_segments(audio_segments, output_file)
        else:
            print("No audio segments to combine.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python 102203937.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)
    
    singer_name = sys.argv[1]
    try:
        n_videos = int(sys.argv[2])
        y_seconds = int(sys.argv[3])
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)
    
    output_file = sys.argv[4]
    
    download_videos_and_combine_audio(singer_name, n_videos, y_seconds, output_file)
