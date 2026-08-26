# Youtube Extractor

These script will help you to retrieve information from youtube metadata and export your youtube playlists.

## 📋 Prerequisites

Before running this script, ensure you have the following installed:

* **[Python 3.x](https://www.python.org/)**
* **[pip](https://pypa.io)** (Python package installer)

You will also need perform the following in your Google account that you use for youtube:
1. Create a project in the Google Cloud Console
2. Enable the YouTube Data API v3
3. Download your OAuth 2.0 credentials as client_secret.json and place in the same directory as the script.

# Required Python Libraries
    google-api-python-client
    google-auth-oauthlib
    google-auth-httplib2
    
## 🔧 Installation

1. **Clone the repository** (or download the script directly):
   ```bash
   git clone https://github.com/w-perez/automated-backup-utilities.git
   cd automated-backup-utilities
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

For exporting youtube playlists, run the script from your terminal using the following command:

```bash
python script_name.py
```

## 🛠️ Built With

* [Python](https://www.python.org/)
