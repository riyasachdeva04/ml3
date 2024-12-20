import os
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash
from pytubefix import YouTube, Search
from pydub import AudioSegment
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
import zipfile
from email.mime.application import MIMEApplication

app = Flask(__name__)
app.secret_key = 'your_secret_key'
OUTPUT_PATH = os.path.join('/tmp', 'downloads')
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)


def download_audio(url, video_num):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        audio_file = os.path.join(OUTPUT_PATH, f"video_{video_num}_{yt.title}.mp3")
        audio_stream.download(output_path=OUTPUT_PATH, filename=f"video_{video_num}_{yt.title}.mp3")
        print("Successfully downloaded")
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
    except Exception as e:
        print(f"Error combining audio segments: {str(e)}")

def download_videos_and_combine_audio(artist_name, n_videos, y_seconds, output_file):
    try:
        if n_videos <= 10:
            return "Error: Number of videos should be greater than 10."
        if y_seconds <= 20:
            return "Error: Audio duration should be greater than 20 seconds."
        search = Search(artist_name)
        results = search.results[:n_videos]
        
        if len(results) < n_videos:
            return f"Error: Only found {len(results)} videos, but {n_videos} were requested."
        
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
            return None  
        else:
            return "No audio segments to combine."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def zip_audio_file(audio_file):
    zip_file_name = audio_file.replace('.mp3', '.zip')
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        zip_file.write(audio_file, os.path.basename(audio_file))
    return zip_file_name

def send_email(recipient, subject, body, audio_file):
    try:
        sender_email = "sachdevar919@gmail.com"  
        app_password = "tgpg jelk npas ovvr" 
        
        zip_file = zip_audio_file(audio_file)

        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject


        msg.attach(MIMEText(body, 'plain'))


        with open(zip_file, "rb") as f:
            zip_attachment = MIMEApplication(f.read(), _subtype='zip')
            zip_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file))
            msg.attach(zip_attachment)


        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient, msg.as_string())
            
        print("Email sent successfully with zip attachment!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        singer_name = request.form["singer_name"]
        n_videos = int(request.form["num_videos"])
        y_seconds = int(request.form["video_duration"])
        email = request.form["email"]
        
        output_file = os.path.join(OUTPUT_PATH, "mashup.mp3")
        error_message = download_videos_and_combine_audio(singer_name, n_videos, y_seconds, output_file)
        
        if error_message is None:
            subject = "Your Audio Mashup"
            body = "Here is your requested audio mashup."
            send_email(email, subject, body, output_file)
            flash("Mashup created and emailed successfully!", "success")
        else:
            flash(error_message, "error")
        
        return redirect(url_for("index"))
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
