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
import numpy as np

# LangChain imports
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
 
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

class VectorTextProcessor:
    """
    Optimized Vector Text Processor
    Class để xử lý text từ các file và lưu vào ChromaDB với vector embeddings
    """
   
    # Class constants
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_OVERLAP = 200
    EMBEDDING_DIMENSION = 1536  # Azure OpenAI text-embedding-3-small dimension
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md', '.markdown'}
    ENCODING_FALLBACKS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
   
    def __init__(self,
                 db_path: str = "./vector_chroma_db",
                 embedding_model: str = "text-embedding-3-small",
                 enable_caching: bool = True,
                 max_workers: int = 4):
        """
        Khởi tạo VectorTextProcessor với LangChain vector stores
        """
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        self._cache = {} if enable_caching else None
        
        # Configure SSL first
        configure_ssl()
        
        # Initialize Azure OpenAI embeddings
        self._initialize_azure_embeddings()
        
        # Initialize LangChain Chroma vector store
        self._initialize_langchain_vectorstore()
        
        logger.info(f"VectorTextProcessor initialized successfully with Azure OpenAI embeddings")
   
    def _initialize_azure_embeddings(self):
        """Initialize Azure OpenAI embeddings for LangChain"""
        try:
            self.embeddings = AzureOpenAIEmbeddings(
                api_key="sk-8YouTg_4fia-c-LA0yeEXQ",
                azure_endpoint="https://aiportalapi.stu-platform.live/jpe",
                api_version="2024-02-01",  # Updated to newer API version
                model="text-embedding-3-small",
                azure_deployment="text-embedding-3-small",
                chunk_size=1000,  # Optimize chunk size for embeddings
                max_retries=3,    # Add retry logic
                request_timeout=30  # Add timeout
            )
            logger.info("✅ Azure OpenAI embeddings initialized with text-embedding-3-small")
        except Exception as e:
            logger.error(f"Failed to initialize Azure embeddings: {e}")
            raise Exception(f"Azure OpenAI embeddings required but failed to initialize: {e}")
    
    def _initialize_langchain_vectorstore(self):
        """Initialize LangChain Chroma vector store with Azure OpenAI embeddings"""
        try:
            self.vectorstore = Chroma(
                collection_name="azure_openai_embeddings_collection",
                embedding_function=self.embeddings,
                persist_directory=self.db_path
            )
            logger.info("✅ LangChain Chroma vector store initialized with Azure OpenAI embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain vector store: {e}")
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
        """Create embedding using Azure OpenAI text-embedding-3-small"""
        if not text.strip():
            return None
           
        try:
            # Use Azure OpenAI embeddings with optimized text preprocessing
            cleaned_text = text.strip().replace('\n', ' ').replace('\r', ' ')
            embedding = self.embeddings.embed_query(cleaned_text)
            return embedding
           
        except Exception as e:
            logger.error(f"Azure OpenAI embedding creation failed: {e}")
            raise Exception(f"Azure OpenAI embeddings required but failed: {e}")
   
    def _create_hash_embedding(self, text: str) -> List[float]:
        """Tạo hash-based embedding tối ưu với Azure OpenAI dimension (1536)"""
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
       
        embedding = []
        # Create multiple hash rounds to reach 1536 dimensions
        for round_num in range(24):  # 24 rounds * 64 values = 1536
            round_hash = hashlib.sha256(f"{text}_{round_num}".encode('utf-8')).hexdigest()
            for i in range(0, min(len(round_hash), 128), 2):  # 64 hex pairs per round
                hex_pair = round_hash[i:i+2]
                embedding.append(int(hex_pair, 16) / 255.0)
                if len(embedding) >= self.EMBEDDING_DIMENSION:
                    break
            if len(embedding) >= self.EMBEDDING_DIMENSION:
                break
       
        # Ensure exact dimension
        embedding = embedding[:self.EMBEDDING_DIMENSION]
        
        # Pad if needed (shouldn't happen with above logic)
        while len(embedding) < self.EMBEDDING_DIMENSION:
            embedding.append(0.0)
       
        # Normalize vector
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
   
    def add_to_vectorstore(self,
                          content: str,
                          metadata: Dict[str, Any],
                          doc_id: Optional[str] = None,
                          use_chunking: bool = True) -> Optional[List[str]]:
        """Thêm text vào LangChain vector store với optimized chunking"""
        doc_id = doc_id or str(uuid.uuid4())
       
        try:
            chunk_ids = []
            documents = []
           
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
                   
                    doc = Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    )
                    documents.append(doc)
                    chunk_ids.append(chunk_id)
               
                logger.info(f"✅ Prepared {len(chunk_ids)} chunks for document: {doc_id}")
                   
            else:
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                documents.append(doc)
                chunk_ids = [doc_id]
                logger.info(f"✅ Prepared document: {doc_id}")
            
            # Add documents to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                logger.info(f"✅ Added {len(documents)} documents to vector store")
           
            return chunk_ids
           
        except Exception as e:
            logger.error(f"Failed to add to vector store: {e}")
            return None
   
    def process_and_store_file(self, file_path: str, use_chunking: bool = True) -> Optional[List[str]]:
        """Xử lý và lưu file với LangChain vector store"""
        start_time = time.time()
       
        result = self.process_file(file_path)
        if result is None:
            return None
       
        chunk_ids = self.add_to_vectorstore(
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
        """Tìm kiếm với LangChain vector store"""
        if not query.strip():
            logger.warning("Empty query provided")
            return None
           
        try:
            start_time = time.time()
           
            if score_threshold > 0.0:
                # Use similarity search with score threshold
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query,
                    k=n_results
                )
                
                # Filter by threshold (convert distance to similarity: similarity = 1 - distance)
                filtered_docs = [
                    (doc, score) for doc, score in docs_with_scores 
                    if (1 - score) >= score_threshold
                ]
                
                # Convert to expected format
                results = {
                    'documents': [[doc.page_content for doc, score in filtered_docs]],
                    'metadatas': [[doc.metadata for doc, score in filtered_docs]],
                    'ids': [[doc.metadata.get('chunk_id', f'doc_{i}') for i, (doc, score) in enumerate(filtered_docs)]],
                    'distances': [[score for doc, score in filtered_docs]]
                }
            else:
                # Regular similarity search
                docs = self.vectorstore.similarity_search(query, k=n_results)
                results = {
                    'documents': [[doc.page_content for doc in docs]],
                    'metadatas': [[doc.metadata for doc in docs]],
                    'ids': [[doc.metadata.get('chunk_id', f'doc_{i}') for i, doc in enumerate(docs)]],
                    'distances': [[0.0 for _ in docs]]  # No scores available
                }
           
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.3f}s")
           
            return results
           
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return None
   
    def get_collection_info(self) -> Dict[str, Any]:
        """Lấy thông tin vector store với additional metrics"""
        try:
            # Get document count from LangChain vector store
            try:
                # Try to get collection info if available
                collection_data = self.vectorstore._collection.get()
                count = len(collection_data.get('ids', []))
            except:
                count = 0
           
            return {
                "collection_name": "azure_openai_embeddings_collection",
                "document_count": count,
                "db_path": self.db_path,
                "embedding_method": "Azure OpenAI text-embedding-3-small",
                "vectorstore_type": "LangChain Chroma",
                "embedding_dimension": self.EMBEDDING_DIMENSION,
                "caching_enabled": self.enable_caching,
                "max_workers": self.max_workers
            }
           
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
   
    def get_performance_stats(self) -> Dict[str, Any]:
        """Lấy performance statistics"""
        return {
            "embedding_method": "Azure OpenAI text-embedding-3-small",
            "vectorstore_type": "LangChain Chroma",
            "supported_formats": list(self.SUPPORTED_EXTENSIONS),
            "chunk_size": self.DEFAULT_CHUNK_SIZE,
            "embedding_dimension": self.EMBEDDING_DIMENSION,
            "api_version": "2024-02-01"
        }
    
    def search_similar_documents(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Tuple[Document, float]]:
        """Search for similar documents using LangChain interface"""
        try:
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filter by similarity threshold
            filtered_docs = [
                (doc, score) for doc, score in docs_with_scores 
                if (1 - score) >= threshold
            ]
            
            return filtered_docs
        except Exception as e:
            logger.error(f"Similar document search failed: {e}")
            return []