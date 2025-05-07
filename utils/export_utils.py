import os
import json
import zipfile
import time
import logging
import csv
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

from config import EXPORT_DIR, AUDIO_DIR

# Configure logging
logger = logging.getLogger(__name__)

def export_playlist(playlist: List[Dict], filename: Optional[str] = None) -> str:
    """
    Export playlist to JSON file
    
    Args:
        playlist (list): List of snippets
        filename (str, optional): Custom filename
        
    Returns:
        str: Path to exported file
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"playlist_{timestamp}.json"
    
    export_path = os.path.join(EXPORT_DIR, filename)
    
    try:
        # Prepare export data
        export_data = {
            "playlist": playlist,
            "exported_at": datetime.now().isoformat(),
            "version": "2.1.0"
        }
        
        # Save to file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Playlist exported to {export_path}")
        return export_path
    
    except Exception as e:
        logger.error(f"Error exporting playlist: {e}")
        return ""

def export_playlist_with_audio(playlist: List[Dict], filename: Optional[str] = None) -> str:
    """
    Export playlist with audio files as ZIP
    
    Args:
        playlist (list): List of snippets
        filename (str, optional): Custom filename
        
    Returns:
        str: Path to exported ZIP file
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"playlist_with_audio_{timestamp}.zip"
    
    export_path = os.path.join(EXPORT_DIR, filename)
    
    try:
        # Create temporary directory for export
        temp_dir = os.path.join(EXPORT_DIR, "temp_export")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save playlist JSON
        playlist_file = os.path.join(temp_dir, "playlist.json")
        with open(playlist_file, 'w', encoding='utf-8') as f:
            json.dump({
                "playlist": playlist,
                "exported_at": datetime.now().isoformat(),
                "version": "2.1.0"
            }, f, ensure_ascii=False, indent=2)
        
        # Create audio directory
        audio_dir = os.path.join(temp_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Copy audio files
        for i, snippet in enumerate(playlist):
            if 'audio_path' in snippet and os.path.exists(snippet['audio_path']):
                # Create a clean filename
                audio_filename = f"track_{i+1}_{os.path.basename(snippet['audio_path'])}"
                dest_path = os.path.join(audio_dir, audio_filename)
                
                # Copy audio file
                shutil.copy2(snippet['audio_path'], dest_path)
                
                # Update path in playlist
                playlist[i]['audio_path'] = os.path.join("audio", audio_filename)
        
        # Create info file with metadata
        info_file = os.path.join(temp_dir, "info.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("Mindsnacks Playlist Export\n")
            f.write("=========================\n\n")
            f.write(f"Exported: {datetime.now().isoformat()}\n")
            f.write(f"Tracks: {len(playlist)}\n\n")
            
            for i, snippet in enumerate(playlist):
                f.write(f"Track {i+1}: {snippet['title']}\n")
                f.write(f"Topic: {snippet['topic']}\n")
                f.write(f"Language: {snippet['language']}\n")
                f.write(f"Created: {snippet['created_date']}\n\n")
        
        # Create ZIP file
        with zipfile.ZipFile(export_path, 'w') as zipf:
            # Add files
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
        logger.info(f"Playlist with audio exported to {export_path}")
        return export_path
    
    except Exception as e:
        logger.error(f"Error exporting playlist with audio: {e}")
        return ""

def export_stats(stats: Dict[str, Any], format: str = 'json') -> str:
    """
    Export user stats
    
    Args:
        stats (dict): User statistics
        format (str): Export format ('json' or 'csv')
        
    Returns:
        str: Path to exported file
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == 'csv':
        filename = f"stats_{timestamp}.csv"
        export_path = os.path.join(EXPORT_DIR, filename)
        
        try:
            # Flatten stats for CSV export
            flat_stats = {}
            
            def flatten_dict(d, parent_key=''):
                for k, v in d.items():
                    key = f"{parent_key}_{k}" if parent_key else k
                    
                    if isinstance(v, dict):
                        flatten_dict(v, key)
                    else:
                        flat_stats[key] = v
            
            flatten_dict(stats)
            
            # Write to CSV
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Key', 'Value'])
                
                for key, value in flat_stats.items():
                    writer.writerow([key, value])
            
            logger.info(f"Stats exported to {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting stats to CSV: {e}")
            return ""
    else:
        # Default to JSON
        filename = f"stats_{timestamp}.json"
        export_path = os.path.join(EXPORT_DIR, filename)
        
        try:
            # Add timestamp
            export_data = {
                "stats": stats,
                "exported_at": datetime.now().isoformat()
            }
            
            # Save to file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Stats exported to {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting stats to JSON: {e}")
            return ""

def import_playlist(import_path: str) -> List[Dict]:
    """
    Import playlist from file
    
    Args:
        import_path (str): Path to import file
        
    Returns:
        list: Imported playlist
    """
    try:
        if import_path.endswith('.json'):
            # Import from JSON
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's a valid playlist
            if isinstance(data, dict) and 'playlist' in data:
                logger.info(f"Playlist imported from {import_path}")
                return data['playlist']
            elif isinstance(data, list):
                logger.info(f"Playlist imported from {import_path}")
                return data
            else:
                logger.error(f"Invalid playlist format in {import_path}")
                return []
        
        elif import_path.endswith('.zip'):
            # Import from ZIP
            temp_dir = os.path.join(EXPORT_DIR, "temp_import")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Extract ZIP
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Check for playlist.json
                playlist_file = os.path.join(temp_dir, "playlist.json")
                if os.path.exists(playlist_file):
                    with open(playlist_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict) and 'playlist' in data:
                        playlist = data['playlist']
                        
                        # Update audio paths
                        for i, snippet in enumerate(playlist):
                            if 'audio_path' in snippet:
                                # Get relative path
                                rel_path = snippet['audio_path']
                                
                                # Copy audio file to audio directory
                                src_path = os.path.join(temp_dir, rel_path)
                                if os.path.exists(src_path):
                                    # Create a unique filename
                                    filename = f"imported_{time.time()}_{os.path.basename(rel_path)}"
                                    dest_path = os.path.join(AUDIO_DIR, filename)
                                    
                                    # Copy audio file
                                    shutil.copy2(src_path, dest_path)
                                    
                                    # Update path in playlist
                                    playlist[i]['audio_path'] = dest_path
                        
                        logger.info(f"Playlist imported from {import_path}")
                        
                        # Clean up
                        shutil.rmtree(temp_dir)
                        
                        return playlist
                    else:
                        logger.error(f"Invalid playlist format in {import_path}")
                        return []
                else:
                    logger.error(f"No playlist.json found in {import_path}")
                    return []
            
            except Exception as e:
                logger.error(f"Error importing playlist from ZIP: {e}")
                
                # Clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                return []
        else:
            logger.error(f"Unsupported file format: {import_path}")
            return []
    
    except Exception as e:
        logger.error(f"Error importing playlist: {e}")
        return []