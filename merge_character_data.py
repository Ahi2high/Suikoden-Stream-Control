#!/usr/bin/env python
"""
This script merges character data from characters.json and recruitment.json
into a properly formatted characters_processed.json file for the Suikoden Display app.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path("data")

def merge_character_data():
    """Merges character and recruitment data into a single, properly formatted file."""
    try:
        DEFAULT_RECRUITMENT_INFO = "Recruitment information not available."
        
        # Load the character data (image mappings)
        characters_path = DATA_DIR / "characters.json"
        with open(characters_path, 'r', encoding='utf-8') as f:
            characters_data = json.load(f)
        
        # Load the recruitment data
        recruitment_path = DATA_DIR / "recruitment.json"
        recruitment_data = {}
        try:
            with open(recruitment_path, 'r', encoding='utf-8') as f:
                recruitment_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load recruitment data: {e}")
        
        # Initialize the new character data structure
        processed_characters = []
        
        # Process each character (starting with characters.json as the base)
        for i, (name, image_path) in enumerate(characters_data.items(), 1):
            # Get recruitment info if available
            recruitment_info = DEFAULT_RECRUITMENT_INFO
            
            # Check if this character has recruitment data
            if name in recruitment_data:
                data = recruitment_data[name]
                
                if isinstance(data, str):
                    # Handle older format where recruitment data is just a string
                    recruitment_info = data
                    # Keep the image_path from characters.json
                else:
                    # Handle new format where data is a dict
                    recruitment_info = data.get("recruitment", DEFAULT_RECRUITMENT_INFO)
                    # Use image from recruitment data if specified, otherwise use from characters.json
                    if "image" in data:
                        image_path = data["image"]
            
            # Ensure image path is properly formatted
            if not isinstance(image_path, str):
                image_path = f"{name}.png"  # Default fallback
                
            # Create character entry
            character = {
                "id": i,
                "name": name,
                "image_url": f"/static/img/{image_path}",
                "recruitment_info": recruitment_info
            }
            
            processed_characters.append(character)
        
        # Save the processed data
        output_path = DATA_DIR / "characters_processed.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_characters, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully merged data for {len(processed_characters)} characters to {output_path}")
        print(f"- {len([c for c in processed_characters if c['recruitment_info'] != DEFAULT_RECRUITMENT_INFO])} characters with recruitment information")
        print(f"- {len([c for c in processed_characters if c['recruitment_info'] == DEFAULT_RECRUITMENT_INFO])} characters without recruitment information")
        return processed_characters
    
    except Exception as e:
        print(f"Error merging character data: {e}")
        return []

if __name__ == "__main__":
    # Ensure the data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    merged_data = merge_character_data()
    print(f"Processed {len(merged_data)} characters.")

