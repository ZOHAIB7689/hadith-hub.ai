import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
from typing import Optional, Dict, List
from crewai.flow.flow import Flow
from litellm import completion
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IslamicKnowledgeFinder(Flow):
    def __init__(self):
        """Initialize the IslamicKnowledgeFinder with API key validation."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
    def _safe_api_call(self, messages: list, retries: int = 3) -> Optional[str]:
        """
        Make API calls with error handling and retries.
        
        Args:
            messages (list): List of message objects for the API
            retries (int): Number of retry attempts
            
        Returns:
            Optional[str]: API response content or None if failed
        """
        for attempt in range(retries):
            try:
                response = completion(
                    model="gemini/gemini-2.0-flash",
                    messages=messages,
                    api_key=self.api_key,
                    max_tokens=1000
                )
                return response["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"API call failed (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    return None
                
    def search_islamic_knowledge(self, query: str) -> Optional[str]:
        """
        Search for Islamic knowledge based on the query.
        """
        if not query.strip():
            return "Please enter a valid search query."
            
        search_prompt = f"""
        Only search in Islamic texts (Quran, Hadith, and Islamic history).
        If the query is unrelated to Islam, return exactly this message: '🚫 This is not related to Islam.'.
        Provide specific references when possible (Surah and verse numbers for Quran, or Hadith collection names).
        
        Question: {query}
        """
        
        return self._safe_api_call([{"role": "user", "content": search_prompt}])

    def get_references(self, search_result: str) -> Optional[str]:
        """
        Get detailed references for the search result.
        """
        if "🚫" in search_result:
            return search_result
            
        reference_prompt = f"""
        For the following Islamic knowledge:
        {search_result}
        
        Please provide:
        1. Exact Quranic verses with Surah name and number
        2. Hadith references with collection name and number
        3. Historical sources if applicable
        """
        
        return self._safe_api_call([{"role": "user", "content": reference_prompt}])

def initialize_session_state():
    """Initialize session state variables."""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

def add_to_history(query: str, search_result: str, references: Optional[str]):
    """Add search result to history."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.search_history.insert(0, {
        'timestamp': timestamp,
        'query': query,
        'search_result': search_result,
        'references': references
    })

def display_sidebar_history():
    """Display search history in sidebar."""
    st.sidebar.title("Search History")
    
    if not st.session_state.search_history:
        st.sidebar.info("No previous searches yet")
        return
        
    for idx, item in enumerate(st.session_state.search_history):
        with st.sidebar.expander(f"🔍 {item['query'][:50]}...", expanded=False):
            st.write(f"**Time:** {item['timestamp']}")
            st.write("**Search Result:**")
            st.write(item['search_result'])
            if item['references'] and "🚫" not in item['references']:
                st.write("**References:**")
                st.write(item['references'])

def main():
    st.set_page_config(
        page_title="Islamic Knowledge Finder",
        page_icon="📖",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Main content
    st.title("📖 Islamic Knowledge Finder")
    st.markdown("""
    Search for knowledge from Islamic sources including:
    - The Holy Quran
    - Authentic Hadith Collections
    - Islamic Historical Records
    """)
    
    try:
        finder = IslamicKnowledgeFinder()
    except ValueError as e:
        st.error("⚠️ Configuration Error: Please ensure the API key is properly set.")
        return
        
    input_text = st.text_area(
        "Enter your question about Islam:",
        placeholder="Example: What does Islam say about kindness to parents?",
        help="Enter any topic related to Islamic teachings, history, or practices."
    )
    
    if st.button("🔍 Search", type="primary"):
        with st.spinner("Searching Islamic sources..."):
            search_result = finder.search_islamic_knowledge(input_text)
            
            if not search_result:
                st.error("⚠️ Failed to get response. Please try again later.")
                return
                
            st.write("### 🔎 Search Result:")
            st.write(search_result)
            
            references = None
            if "🚫" not in search_result:
                with st.spinner("Finding detailed references..."):
                    references = finder.get_references(search_result)
                    
                    if references:
                        st.write("### 📜 Detailed References:")
                        st.write(references)
                    else:
                        st.error("⚠️ Failed to fetch references")
            
            # Add to history
            add_to_history(input_text, search_result, references)
    
    # Display sidebar
    display_sidebar_history()

if __name__ == "__main__":
    main()