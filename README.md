# Vision Warehouse Logo Similarity Analyzer

A Python tool to analyze similarities between business logos using Google Cloud Vision Warehouse API. This tool can process large sets of logo images (70k+) and identify similar logos based on visual features.

## Features

- Create and manage Vision Warehouse corpus for logo images
- Upload and index large sets of logo images
- Perform similarity search using Vision Warehouse API
- Export similarity results to Google Spreadsheet
- Support for batch processing of large image sets

## Prerequisites

1. Python 3.8+
2. Google Cloud Project with Vision Warehouse API enabled
3. Google Cloud SDK installed and configured
4. Service account with necessary permissions:
   - Vision Warehouse Admin
   - Storage Admin (if using GCS for image upload)
   - Sheets API access (for results export)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/bhaktiutama/vision-warehouse-logo-similarity.git
cd vision-warehouse-logo-similarity
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## Configuration

1. Update `config.py` with your settings:
   - Project number
   - Location (region)
   - Corpus settings
   - Index settings

2. Prepare your logo images in a directory
3. Create a Google Spreadsheet for results (optional)

## Usage

1. Basic usage:
```bash
python logo_similarity.py --image-dir /path/to/images --output spreadsheet_id
```

2. With custom configuration:
```bash
python logo_similarity.py --image-dir /path/to/images --output spreadsheet_id --max-results 20 --batch-size 100
```

## Project Structure

```
vision-warehouse-logo-similarity/
├── logo_similarity.py     # Main implementation
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── gcs.py           # Google Cloud Storage utilities
│   ├── auth.py          # Authentication utilities
│   └── spreadsheet.py   # Google Sheets utilities
├── tests/               # Unit tests
└── examples/            # Usage examples
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vision Warehouse API
- Google Cloud Platform