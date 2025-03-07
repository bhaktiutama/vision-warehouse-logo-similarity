#!/usr/bin/env python3
"""Logo Similarity Analyzer using Google Cloud Vision Warehouse API."""

import os
import argparse
import logging
from datetime import datetime
from tqdm import tqdm

import requests
from google.cloud import storage

from config import (
    PROJECT_NUMBER,
    LOCATION,
    CORPUS_SETTINGS,
    INDEX_SETTINGS,
    BATCH_SIZE,
    MAX_RETRIES,
    TIMEOUT,
    SUPPORTED_FORMATS,
    SPREADSHEET_RANGE
)
from utils import get_access_token, upload_to_gcs, save_to_spreadsheet

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogoSimilarityAnalyzer:
    def __init__(self, project_number=PROJECT_NUMBER, location=LOCATION):
        self.project_number = project_number
        self.location = location
        self.base_url = "https://warehouse-visionai.googleapis.com/v1"
        self.token = get_access_token()
        
    def _make_request(self, method, endpoint, data=None, retry_count=0):
        """Make HTTP request to Vision Warehouse API with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=TIMEOUT)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if retry_count < MAX_RETRIES:
                logger.warning(f"Request failed, retrying... ({retry_count + 1}/{MAX_RETRIES})")
                return self._make_request(method, endpoint, data, retry_count + 1)
            raise Exception(f"Request failed after {MAX_RETRIES} retries: {e}")
    
    def create_corpus(self):
        """Create a corpus for image storage."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/corpora"
        return self._make_request("POST", endpoint, CORPUS_SETTINGS)
    
    def create_index(self, corpus_id):
        """Create an index for similarity search."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/corpora/{corpus_id}/indexes"
        return self._make_request("POST", endpoint, INDEX_SETTINGS)
    
    def create_index_endpoint(self, display_name, description):
        """Create an index endpoint."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/indexEndpoints"
        data = {
            "display_name": display_name,
            "description": description
        }
        return self._make_request("POST", endpoint, data)
    
    def deploy_index(self, index_endpoint_id, corpus_id, index_id):
        """Deploy index to endpoint."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/indexEndpoints/{index_endpoint_id}:deployIndex"
        data = {
            "deployedIndex": {
                "index": f"projects/{self.project_number}/locations/{self.location}/corpora/{corpus_id}/indexes/{index_id}"
            }
        }
        return self._make_request("POST", endpoint, data)
    
    def process_images(self, image_dir, corpus_id, bucket_name):
        """Process all images in directory and upload to Vision Warehouse."""
        logger.info("Starting image processing...")
        
        # Get list of image files
        image_files = []
        for root, _, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    image_files.append(os.path.join(root, file))
        
        # Process images in batches
        for i in tqdm(range(0, len(image_files), BATCH_SIZE)):
            batch = image_files[i:i + BATCH_SIZE]
            
            # Upload batch to GCS
            gcs_uris = []
            for image_path in batch:
                destination_blob = f"logos/{datetime.now().strftime('%Y%m%d')}/{os.path.basename(image_path)}"
                gcs_uri = upload_to_gcs(bucket_name, image_path, destination_blob)
                gcs_uris.append(gcs_uri)
            
            # Create assets in Vision Warehouse
            for gcs_uri in gcs_uris:
                self.create_asset(corpus_id, gcs_uri)
    
    def create_asset(self, corpus_id, gcs_uri):
        """Create an asset in the corpus."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/corpora/{corpus_id}/assets"
        data = {
            "asset": {
                "display_name": os.path.basename(gcs_uri),
                "gcs_uri": gcs_uri
            }
        }
        return self._make_request("POST", endpoint, data)
    
    def search_similar_images(self, index_endpoint_id, query_image_path, max_results=10):
        """Search for similar images."""
        endpoint = f"projects/{self.project_number}/locations/{self.location}/indexEndpoints/{index_endpoint_id}:findNeighbors"
        
        # Upload query image to GCS first
        bucket_name = f"{self.project_number}-query-images"
        destination_blob = f"query/{datetime.now().strftime('%Y%m%d')}/{os.path.basename(query_image_path)}"
        gcs_uri = upload_to_gcs(bucket_name, query_image_path, destination_blob)
        
        data = {
            "query_image": {
                "gcs_uri": gcs_uri
            },
            "max_results": max_results
        }
        
        return self._make_request("POST", endpoint, data)

def main():
    parser = argparse.ArgumentParser(description='Logo Similarity Analysis Tool')
    parser.add_argument('--image-dir', required=True, help='Directory containing logo images')
    parser.add_argument('--bucket', required=True, help='GCS bucket for image storage')
    parser.add_argument('--spreadsheet-id', help='Google Spreadsheet ID for results')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of similar images to find')
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = LogoSimilarityAnalyzer()
        
        # Create corpus
        logger.info("Creating corpus...")
        corpus_response = analyzer.create_corpus()
        corpus_id = corpus_response["response"]["name"].split("/")[-1]
        
        # Process images
        logger.info("Processing images...")
        analyzer.process_images(args.image_dir, corpus_id, args.bucket)
        
        # Create and deploy index
        logger.info("Creating index...")
        index_response = analyzer.create_index(corpus_id)
        index_id = index_response["response"]["name"].split("/")[-1]
        
        logger.info("Creating index endpoint...")
        endpoint_response = analyzer.create_index_endpoint(
            display_name=f"logo_similarity_endpoint_{datetime.now().strftime('%Y%m%d')}",
            description="Endpoint for logo similarity search"
        )
        endpoint_id = endpoint_response["response"]["name"].split("/")[-1]
        
        logger.info("Deploying index...")
        analyzer.deploy_index(endpoint_id, corpus_id, index_id)
        
        # If spreadsheet ID is provided, save results
        if args.spreadsheet_id:
            logger.info("Saving results to spreadsheet...")
            # Implement saving results to spreadsheet
            pass
        
        logger.info("Processing completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()