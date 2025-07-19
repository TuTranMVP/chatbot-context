#!/usr/bin/env python3
"""
Cleanup script to remove old ChromaDB collections with incompatible dimensions
"""

import os
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_old_collections():
    """Remove old ChromaDB collections with incompatible dimensions"""
    
    directories_to_clean = [
        "./vector_chroma_db",
        "./chroma_db"
    ]
    
    for db_path in directories_to_clean:
        try:
            if os.path.exists(db_path):
                logger.info(f"🧹 Cleaning up old vector database: {db_path}")
                shutil.rmtree(db_path)
                logger.info(f"✅ Successfully cleaned up: {db_path}")
            else:
                logger.info(f"📁 Directory doesn't exist: {db_path}")
        except Exception as e:
            logger.error(f"❌ Failed to clean up {db_path}: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting ChromaDB cleanup for dimension compatibility...")
    cleanup_old_collections()
    logger.info("🎉 Cleanup completed! You can now run your application with Azure OpenAI 1536-dimensional embeddings.")
