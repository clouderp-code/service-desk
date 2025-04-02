import pdfplumber
import logging
from typing import List

logger = logging.getLogger(__name__)

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[str]:
        """
        Extract text from PDF using pdfplumber
        """
        try:
            logger.info(f"Opening PDF file: {file_path}")
            pages_text = []
            
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"PDF opened successfully. Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            pages_text.append(text)
                        logger.info(f"Processed page {page_num + 1}")
                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                
            logger.info(f"Successfully extracted text from {len(pages_text)} pages")
            return pages_text
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}") 