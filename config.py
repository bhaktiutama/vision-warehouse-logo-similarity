"""Configuration settings for the Logo Similarity Analyzer."""

# Google Cloud settings
PROJECT_NUMBER = "your-project-number"  # Replace with your project number
LOCATION = "us-central1"  # Replace with your preferred region

# Corpus settings
CORPUS_SETTINGS = {
    "display_name": "logo_similarity_corpus",
    "description": "Corpus for analyzing logo similarities",
    "type": "IMAGE",
    "search_capability_setting": {
        "search_capabilities": {
            "type": "EMBEDDING_SEARCH"
        }
    }
}

# Index settings
INDEX_SETTINGS = {
    "display_name": "logo_similarity_index",
    "index_type": "VISUAL_EMBEDDING"
}

# Processing settings
BATCH_SIZE = 100  # Number of images to process in each batch
MAX_RETRIES = 3   # Number of retries for API calls
TIMEOUT = 300     # Timeout for API calls in seconds

# Supported image formats
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png')

# Google Sheets settings
SPREADSHEET_RANGE = "Sheet1!A1"  # Default range for results
SPREADSHEET_COLUMNS = ['Query Image', 'Similar Image', 'Similarity Score']