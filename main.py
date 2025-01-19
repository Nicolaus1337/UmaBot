import tweepy
import random
import os
import cv2
from pytube import YouTube
import yt_dlp
import requests

# Your Twitter Developer credentials
CLIENT_ID = " "
CLIENT_SECRET = ""
API_KEY = ""
API_SECRET_KEY = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""


CALLBACK_URL = "http://127.0.0.1/callback"


# Step 1: Authenticate with OAuth 2.0 for API v2 using the manual Bearer Token
def authenticate_v2():
    return tweepy.Client( 
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET)


# Step 2: Authenticate with OAuth 1.0 for v1.1 media upload
def authenticate_v1():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET,
    )
    return tweepy.API(auth)


# Step 3: Randomly select a video from a list
def pick_random_video(video_urls):
    return random.choice(video_urls)


# Step 4: Download the video from YouTube
def download_video(video_url, save_path="video.mp4"):
    ydl_opts = {
        'format': 'best',  # Automatically select the best combined video/audio stream
        'outtmpl': save_path,  # Save video with the specified filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    print(f"Downloaded video to {save_path}")
    return save_path


# Step 5: Extract a random frame from the downloaded video
def extract_random_frame(video_path, output_folder="frames"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame_number = random.randint(0, frame_count - 1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)
    success, frame = cap.read()
    if success:
        frame_path = os.path.join(output_folder, f"frame_{random_frame_number}.jpg")
        cv2.imwrite(frame_path, frame)
        print(f"Saved frame to {frame_path}")
        return frame_path
    else:
        print("Failed to extract frame")
        return None

    cap.release()


# Step 6: Post the extracted frame on Twitter using API v2 and OAuth 1.0 for media upload
def post_frame_on_twitter(client_v2, api_v1, frame_path):
    try:
        # Upload media using v1.1 API
        media = api_v1.media_upload(frame_path)
        
        # Post tweet with media using v2 API
        tweet = client_v2.create_tweet(
            text="Umapyoi!", 
            media_ids=[media.media_id]
        )
        print(f"Posted frame: {frame_path} with tweet ID: {tweet.data['id']}")
    except Exception as e:
        print("Error posting frame:", e)


# Step 7: The main function to combine all steps
def post_random_anime_frame(video_urls):
    # Pick a random video URL
    selected_video_url = pick_random_video(video_urls)
    print(f"Selected video: {selected_video_url}")
    
    # Authenticate with Twitter API v2 using manual Bearer Token
    client_v2 = authenticate_v2()
    
    # Authenticate with Twitter API v1.1 for media uploads
    api_v1 = authenticate_v1()
    
    # Step 2: Download the video
    video_path = download_video(selected_video_url)
    
    # Step 3: Extract a random frame from the video
    frame_path = extract_random_frame(video_path)
    
    # Step 4: Post the frame to Twitter
    if frame_path:
        post_frame_on_twitter(client_v2, api_v1, frame_path)
    
    # Cleanup: Delete the downloaded video and frame
    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(frame_path):
        os.remove(frame_path)
    print("Cleanup complete!")


# Run the bot
if __name__ == "__main__":
    # List of YouTube video URLs
    video_urls = [
        "https://www.youtube.com/watch?v=pjPXzJedwiA",
        "https://www.youtube.com/watch?v=0jev2Uv37F8",
        "https://www.youtube.com/watch?v=A42wNP1DJho",
        "https://www.youtube.com/watch?v=RIDl7x_gFGE",
    ]
    
    # Post a random anime frame
    post_random_anime_frame(video_urls)
