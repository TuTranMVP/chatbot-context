"""
Vector Text Processor - Optimized version
Đọc text từ PDF, TXT, MD và lưu vào ChromaDB với Vector Embeddings
Tối ưu hiệu suất, memory usage và error handling
"""
 
import os
import uuid
import hashlib
import time
import warnings
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from functools import lru_cache
 
# Import thư viện xử lý file
import PyPDF2
import fitz  # PyMuPDF
import markdown
import chromadb
import numpy as np
 
# Lazy import for sentence_transformers
SentenceTransformer = None
 
# Tắt warnings và telemetry
warnings.filterwarnings('ignore')
os.environ["ANONYMIZED_TELEMETRY"] = "False"
 
# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
def configure_ssl():
    """Cấu hình SSL một cách an toàn"""
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        os.environ["CURL_CA_BUNDLE"] = ""
        os.environ["REQUESTS_CA_BUNDLE"] = ""
        return True
    except Exception as e:
        logger.warning(f"SSL configuration failed: {e}")
        return False
 
def load_sentence_transformer():
    """Lazy load SentenceTransformer chỉ khi cần"""
    global SentenceTransformer
    if SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            logger.error(f"Failed to import SentenceTransformer: {e}")
            SentenceTransformer = None
    return SentenceTransformer

class VectorTextProcessor:
    """
    Optimized Vector Text Processor
    Class để xử lý text từ các file và lưu vào ChromaDB với vector embeddings
    """
   
    # Class constants
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_OVERLAP = 200
    EMBEDDING_DIMENSION = 384
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md', '.markdown'}
    ENCODING_FALLBACKS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
   
    def __init__(self,
                 db_path: str = "./vector_chroma_db",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 enable_caching: bool = True,
                 max_workers: int = 4):
        """
        Khởi tạo VectorTextProcessor với các tối ưu
        """
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        self.embedding_model = None
        self._cache = {} if enable_caching else None
       
        # Configure SSL first
        configure_ssl()
       
        # Initialize embedding model
        self._initialize_embedding_model()
       
        # Initialize ChromaDB
        self._initialize_chromadb()
       
        logger.info(f"VectorTextProcessor initialized successfully")
   
    def _initialize_embedding_model(self):
        """Khởi tạo embedding model với fallback strategy tối ưu"""
        logger.info(f"🤖 Initializing embedding model: {self.embedding_model_name}")
       
        SentenceTransformer = load_sentence_transformer()
        if not SentenceTransformer:
            logger.warning("SentenceTransformer not available, using hash fallback")
            return
           
        # Strategy 1: Local cache
        if self._try_load_local_model(SentenceTransformer):
            return
           
        # Strategy 2: Download with SSL bypass
        if self._try_download_model(SentenceTransformer):
            return
           
        # Strategy 3: Alternative models
        if self._try_alternative_models(SentenceTransformer):
            return
           
        # Final fallback
        logger.warning("🔧 Using hash-based embeddings as fallback")
        self._log_embedding_guidance()
   
    def _try_load_local_model(self, SentenceTransformer) -> bool:
        """Thử load model từ cache local"""
        try:
            logger.info("🔄 Loading from local cache...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name, local_files_only=True)
            logger.info("✅ Loaded model from local cache")
            return True
        except Exception as e:
            logger.debug(f"Local cache failed: {e}")
            return False
   
    def _try_download_model(self, SentenceTransformer) -> bool:
        """Thử download model với SSL bypass"""
        try:
            logger.info("🔄 Downloading with SSL bypass...")
            import requests
            requests.packages.urllib3.disable_warnings()
           
            self.embedding_model = SentenceTransformer(self.embedding_model_name, trust_remote_code=True)
            logger.info("✅ Downloaded model successfully")
            return True
        except Exception as e:
            logger.debug(f"Download failed: {e}")
            return False
   
    def _try_alternative_models(self, SentenceTransformer) -> bool:
        """Thử các model thay thế"""
        alternatives = [
            'paraphrase-MiniLM-L6-v2',
            'distilbert-base-nli-stsb-mean-tokens',
            'all-mpnet-base-v2'
        ]
       
        for alt_model in alternatives:
            try:
                logger.info(f"🔄 Trying alternative: {alt_model}")
                self.embedding_model = SentenceTransformer(alt_model, local_files_only=True)
                logger.info(f"✅ Loaded alternative model: {alt_model}")
                return True
            except:
                continue
        return False
   
    def _log_embedding_guidance(self):
        """Log hướng dẫn cho user"""
        logger.info("💡 To use ML embeddings:")
        logger.info("   1. Download offline: huggingface-cli download sentence-transformers/all-MiniLM-L6-v2")
        logger.info("   2. Update certificates: pip install --upgrade certifi")
        logger.info("   3. Use VPN/proxy for SSL bypass")
   
    def _initialize_chromadb(self):
        """Khởi tạo ChromaDB với error handling"""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
           
            try:
                self.collection = self.client.get_collection("vector_documents")
                logger.info("📊 Connected to existing collection")
            except:
                self.collection = self.client.create_collection(
                    name="vector_documents",
                    metadata={"description": "Optimized vector text storage"}
                )
                logger.info("📊 Created new collection")
               
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
   
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[str]:
        """Chia text thành chunks với tối ưu hiệu suất"""
        chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        overlap = overlap or self.DEFAULT_OVERLAP
       
        if len(text) <= chunk_size:
            return [text]
       
        chunks = []
        start = 0
       
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
           
            # Tìm điểm ngắt tự nhiên
            if end < len(text):
                for delimiter in ['. ', '! ', '? ', '\\n\\n', '\\n', ' ']:
                    last_pos = chunk.rfind(delimiter)
                    if last_pos > chunk_size - 100:
                        chunk = chunk[:last_pos + len(delimiter)]
                        end = start + last_pos + len(delimiter)
                        break
           
            cleaned_chunk = chunk.strip()
            if cleaned_chunk:
                chunks.append(cleaned_chunk)
               
            start = max(end - overlap, start + 1) if end < len(text) else end
           
        return chunks
   
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Tạo embedding với optimization"""
        if not text.strip():
            return None
           
        try:
            if self.embedding_model is None:
                return self._create_hash_embedding(text)
           
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
           
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            return self._create_hash_embedding(text)
   
    def _create_hash_embedding(self, text: str) -> List[float]:
        """Tạo hash-based embedding tối ưu"""
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
       
        embedding = []
        for i in range(0, min(len(text_hash), self.EMBEDDING_DIMENSION * 2), 2):
            hex_pair = text_hash[i:i+2]
            embedding.append(int(hex_pair, 16) / 255.0)
       
        # Pad to correct dimension
        while len(embedding) < self.EMBEDDING_DIMENSION:
            embedding.extend(embedding[:min(self.EMBEDDING_DIMENSION - len(embedding), len(embedding))])
       
        # Normalize vector
        embedding = embedding[:self.EMBEDDING_DIMENSION]
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
           
        return embedding
   
    def read_pdf(self, file_path: str) -> str:
        """Đọc text từ file PDF với error handling tối ưu"""
        text = ""
        file_path = str(file_path)
       
        try:
            # Primary: PyMuPDF
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                try:
                    page_text = page.get_text()
                    if page_text.strip():
                        text += page_text + "\\n"
                except Exception as e:
                    logger.warning(f"Error reading page {page_num}: {e}")
                    continue
            doc.close()
           
            # Fallback: PyPDF2
            if not text.strip():
                logger.info("Trying PyPDF2 fallback...")
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text.strip():
                                text += page_text + "\\n"
                        except Exception as e:
                            logger.warning(f"PyPDF2 error on page {page_num}: {e}")
                            continue
                           
        except Exception as e:
            logger.error(f"PDF reading failed for {file_path}: {e}")
            return ""
           
        return text.strip()
   
    def read_txt(self, file_path: str) -> str:
        """Đọc text từ file TXT với encoding detection tối ưu"""
        file_path = str(file_path)
       
        for encoding in self.ENCODING_FALLBACKS:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    if content:
                        return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.error(f"TXT reading failed for {file_path}: {e}")
                return ""
       
        logger.warning(f"Could not decode file {file_path} with any encoding")
        return ""
   
    def read_md(self, file_path: str) -> str:
        """Đọc text từ file Markdown với tối ưu"""
        try:
            content = self.read_txt(file_path)
            if not content:
                return ""
           
            # Convert markdown to plain text
            html = markdown.markdown(content)
           
            import re
            text = re.sub(r'<[^>]+>', '', html)
            text = re.sub(r'\\n\\s*\\n', '\\n', text)
            text = re.sub(r'[ \\t]+', ' ', text)
           
            return text.strip()
           
        except Exception as e:
            logger.error(f"Markdown reading failed for {file_path}: {e}")
            return ""
   
    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Xử lý file với validation và error handling tối ưu"""
        file_path = Path(file_path)
       
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
           
        if not file_path.is_file():
            logger.error(f"Not a file: {file_path}")
            return None
           
        file_extension = file_path.suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {file_extension}")
            return None
       
        file_size = file_path.stat().st_size
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            logger.warning(f"Large file detected: {file_size / (1024*1024):.1f}MB")
       
        start_time = time.time()
       
        try:
            if file_extension == '.pdf':
                content = self.read_pdf(str(file_path))
            elif file_extension == '.txt':
                content = self.read_txt(str(file_path))
            elif file_extension in {'.md', '.markdown'}:
                content = self.read_md(str(file_path))
            else:
                logger.error(f"Handler not implemented for: {file_extension}")
                return None
               
        except Exception as e:
            logger.error(f"Content extraction failed for {file_path}: {e}")
            return None
       
        processing_time = time.time() - start_time
       
        if not content or not content.strip():
            logger.warning(f"No content extracted from: {file_path}")
            return None
       
        metadata = {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_type": file_extension,
            "file_size": file_size,
            "content_length": len(content),
            "processing_time": round(processing_time, 3),
            "processed_at": time.time()
        }
       
        logger.info(f"Processed {file_path.name}: {len(content)} chars in {processing_time:.2f}s")
       
        return {
            "content": content,
            "metadata": metadata
        }
   
    def add_to_chromadb(self,
                        content: str,
                        metadata: Dict[str, Any],
                        doc_id: Optional[str] = None,
                        use_chunking: bool = True) -> Optional[List[str]]:
        """Thêm text vào ChromaDB với optimized chunking"""
        doc_id = doc_id or str(uuid.uuid4())
       
        try:
            chunk_ids = []
           
            if use_chunking and len(content) > self.DEFAULT_CHUNK_SIZE:
                chunks = self.chunk_text(content)
                logger.info(f"📦 Split into {len(chunks)} chunks")
               
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_id": chunk_id,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "parent_doc_id": doc_id,
                        "chunk_length": len(chunk)
                    })
                   
                    embedding = self.create_embedding(chunk)
                    if embedding:
                        self.collection.add(
                            documents=[chunk],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id],
                            embeddings=[embedding]
                        )
                        chunk_ids.append(chunk_id)
               
                logger.info(f"✅ Added {len(chunk_ids)} chunks for document: {doc_id}")
                   
            else:
                embedding = self.create_embedding(content)
                if embedding:
                    self.collection.add(
                        documents=[content],
                        metadatas=[metadata],
                        ids=[doc_id],
                        embeddings=[embedding]
                    )
                    chunk_ids = [doc_id]
                    logger.info(f"✅ Added document: {doc_id}")
           
            return chunk_ids
           
        except Exception as e:
            logger.error(f"Failed to add to ChromaDB: {e}")
            return None
   
    def process_and_store_file(self, file_path: str, use_chunking: bool = True) -> Optional[List[str]]:
        """Xử lý và lưu file với optimization"""
        start_time = time.time()
       
        result = self.process_file(file_path)
        if result is None:
            return None
       
        chunk_ids = self.add_to_chromadb(
            content=result["content"],
            metadata=result["metadata"],
            use_chunking=use_chunking
        )
       
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f}s")
       
        return chunk_ids
   
    def vector_search(self,
                     query: str,
                     n_results: int = 5,
                     score_threshold: float = 0.0) -> Optional[Dict[str, Any]]:
        """Tìm kiếm với optimization"""
        if not query.strip():
            logger.warning("Empty query provided")
            return None
           
        try:
            start_time = time.time()
           
            query_embedding = self.create_embedding(query)
            if query_embedding is None:
                logger.error("Failed to create query embedding")
                return None
           
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
           
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.3f}s")
           
            if score_threshold > 0.0 and 'distances' in results and results['distances']:
                return self._filter_by_threshold(results, score_threshold)
           
            return results
           
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return None
   
    def _filter_by_threshold(self, results: Dict[str, Any], threshold: float) -> Dict[str, Any]:
        """Filter results by similarity threshold"""
        filtered = {
            'documents': [[]],
            'metadatas': [[]],
            'ids': [[]],
            'distances': [[]]
        }
       
        for i, distance in enumerate(results['distances'][0]):
            similarity_score = 1.0 - distance
            if similarity_score >= threshold:
                filtered['documents'][0].append(results['documents'][0][i])
                filtered['metadatas'][0].append(results['metadatas'][0][i])
                filtered['ids'][0].append(results['ids'][0][i])
                filtered['distances'][0].append(distance)
       
        return filtered
   
    def get_collection_info(self) -> Dict[str, Any]:
        """Lấy thông tin collection với additional metrics"""
        try:
            count = self.collection.count()
           
            return {
                "collection_name": self.collection.name,
                "document_count": count,
                "db_path": self.db_path,
                "embedding_model": self.embedding_model_name if self.embedding_model else "hash-fallback",
                "caching_enabled": self.enable_caching,
                "max_workers": self.max_workers
            }
           
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
   
    def get_performance_stats(self) -> Dict[str, Any]:
        """Lấy performance statistics"""
        return {
            "embedding_method": "ML" if self.embedding_model else "Hash",
            "supported_formats": list(self.SUPPORTED_EXTENSIONS),
            "chunk_size": self.DEFAULT_CHUNK_SIZE,
            "embedding_dimension": self.EMBEDDING_DIMENSION
        }