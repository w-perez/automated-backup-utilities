import os
import csv
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Date string used for file name
date_str = datetime.now().strftime("%Y%m%d")

# Read-only scope is sufficient for pulling playlist and item details
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_youtube_service():
    creds = None
    # Look for existing token file to bypass login screen if already authenticated
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Authenticate via browser if credentials do not exist or are invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def export_playlists_to_csv(youtube, output_file=f"youtube_playlists_export_{date_str}.csv"):
    print(f"Starting export to {output_file}...")
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Apply the layout header fields requested
        writer.writerow(["Playlist Name", "Playlist ID", "Video Name", "Video Link"])

        try:
            # 1. Fetch all playlists owned by the authenticated email
            playlists_request = youtube.playlists().list(
                part="snippet,id",
                mine=True,
                maxResults=50
            )
            
            playlist_count = 0
            video_count = 0

            while playlists_request:
                playlists_response = playlists_request.execute()

                for playlist in playlists_response.get("items", []):
                    playlist_id = playlist["id"]
                    playlist_name = playlist["snippet"]["title"]
                    playlist_count += 1
                    print(f"Processing playlist: {playlist_name}")
                    
                    # 2. Fetch all nested video items inside this individual playlist in batches of 50
                    items_request = youtube.playlistItems().list(
                        part="snippet",
                        playlistId=playlist_id,
                        maxResults=50
                    )
                    
                    while items_request:
                        items_response = items_request.execute()
                        
                        for item in items_response.get("items", []):
                            video_name = item["snippet"]["title"]
                            video_id = item["snippet"]["resourceId"]["videoId"]
                            video_link = f"https://youtube.com/watch?v={video_id}"
                            
                            # Log extracted metrics to the spreadsheet
                            writer.writerow([playlist_name, playlist_id, video_name, video_link])
                            video_count += 1
                        
                        # Fetch the next batch of videos inside this specific playlist
                        items_request = youtube.playlistItems().list_next(items_request, items_response)
                
                # Fetch the next batch of playlists owned by the account
                playlists_request = youtube.playlists().list_next(playlists_request, playlists_response)
                
            print(f"\nSuccess! Exported {playlist_count} playlists and {video_count} videos to {output_file}")
            
        except Exception as e:
            print(f"An error occurred during API execution: {e}")

def get_video_details(youtube, video_id):
    """
    Fetches detailed metadata, engagement metrics, and tags for a given YouTube Video ID.
    """
    print(f"\nFetching details for Video ID: {video_id}...")
    try:
        # Request metadata (snippet), stats (statistics), and duration (contentDetails)
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        response = request.execute()

        # Exit early if the video ID is invalid or cannot be found
        if not response.get("items"):
            print("No video found with that ID.")
            return None

        video_data = response["items"][0]
        snippet = video_data.get("snippet", {})
        stats = video_data.get("statistics", {})
        details = video_data.get("contentDetails", {})

        # Construct a dictionary containing all primary attributes
        info = {
            "Title": snippet.get("title"),
            "Channel": snippet.get("channelTitle"),
            "Published At": snippet.get("publishedAt"),
            "Duration": details.get("duration"),  # Format: ISO 8601 (e.g., PT14M32S)
            "View Count": stats.get("viewCount"),
            "Like Count": stats.get("likeCount"),
            "Comment Count": stats.get("commentCount"),
            "Description": snippet.get("description"),
            "Tags": snippet.get("tags", [])
        }

        # Print layout nicely formatted to console
        print("-" * 50)
        for key, value in info.items():
            if key == "Tags":
                print(f"{key}: {', '.join(value) if value else 'None'}")
            elif key == "Description":
                # Truncate descriptions so they don't flood your terminal screen
                short_desc = value.split('\n')[0][:80] + "..." if value else "None"
                print(f"{key}: {short_desc}")
            else:
                print(f"{key}: {value}")
        print("-" * 50)

        return info

    except Exception as e:
        print(f"An error occurred while fetching video details: {e}")
        return None

if __name__ == "__main__":
    # Authenticate and construct API service instance
    youtube_service = get_youtube_service()
    
    # Execute extraction logic
    export_playlists_to_csv(youtube_service)

