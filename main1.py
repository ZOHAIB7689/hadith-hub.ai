import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from typing import Optional
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

    def search_islamic_knowledge(self, query: str, language: str = "English") -> Optional[str]:
        """
        Search for Islamic knowledge based on the query in specified language.
        """
        if not query.strip():
            return "Please enter a valid search query." if language == "English" else "براہ کرم درست سوال درج کریں۔"

        # Check if query contains examples from Prophet or Sahabah
        has_prophetic_example = self._check_for_prophetic_example(query)
        
        # Construct language instruction - keep the rest of the prompt the same as original
        lang_instruction = ""
        if language == "Urdu":
            lang_instruction = "Please respond in Urdu."
        
        search_prompt = f"""
        Only search in Islamic texts (Quran, Hadith, and Islamic history).
        If the query is unrelated to Islam, return exactly this message: '🚫 This is not related to Islam.'.
        Provide specific references when possible (Surah and verse numbers for Quran, or Hadith collection names).
        {lang_instruction}
        
        Question: {query}
        """

        result = self._safe_api_call([{"role": "user", "content": search_prompt}])
        
        # If we found a prophetic example, add a note about it
        if result and has_prophetic_example and "🚫" not in result:
            prophetic_note = "\n\n**Note:** This query includes examples from the life of Prophet Muhammad (ﷺ) or his companions (رضي الله عنهم)." if language == "English" else "\n\n**نوٹ:** اس سوال میں حضور نبی کریم (ﷺ) یا صحابہ کرام (رضي الله عنهم) کی زندگی سے مثالیں شامل ہیں۔"
            result += prophetic_note
            
        return result

    def _check_for_prophetic_example(self, query: str) -> bool:
        """
        Check if the query potentially contains examples from Prophet or Sahabah.
        """
        prophetic_keywords = [
            "prophet", "muhammad", "pbuh", "sahaba", "companion", "abu bakr", "umar", "uthman", "ali",
            "aisha", "sunnah", "example of prophet", "prophetic tradition", "nabi", "rasool",
            "صحابہ", "حضرت محمد", "نبی کریم", "صلی اللہ علیہ وسلم", "رسول اللہ", "سنت", "ابوبکر", "عمر", "عثمان", "علی"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in prophetic_keywords)

    def get_references(self, search_result: str, language: str = "English") -> Optional[str]:
        """
        Get detailed references for the search result in specified language.
        """
        if "🚫" in search_result:
            return search_result

        # Construct language instruction - keep the rest of the prompt the same as original
        lang_instruction = ""
        if language == "Urdu":
            lang_instruction = "Please provide the response in Urdu."
            
        reference_prompt = f"""
        For the following Islamic knowledge:
        {search_result}
        
        Please provide:
        1. Exact Quranic verses with Surah name and number
        2. Hadith references with collection name and number
        3. Historical sources if applicable
        {lang_instruction}
        """

        return self._safe_api_call([{"role": "user", "content": reference_prompt}])

# Function to read and update search history
def initialize_session_state():
    """Initialize session state variables."""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'language' not in st.session_state:
        st.session_state.language = "English"

# Add search result to history
def add_to_history(query: str, search_result: str, references: Optional[str], language: str):
    """Add search result to history."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.search_history.insert(0, {
        'timestamp': timestamp,
        'query': query,
        'search_result': search_result,
        'references': references,
        'language': language
    })

# Display sidebar history
def display_sidebar():
    """Display search history in sidebar."""
    st.sidebar.title("📜 " + ("Search History" if st.session_state.language == "English" else "تلاش کی تاریخ"))
    
    if not st.session_state.search_history:
        st.sidebar.info("No previous searches yet" if st.session_state.language == "English" else "ابھی تک کوئی پچھلی تلاش نہیں")
        return
    
    for item in st.session_state.search_history:
        with st.sidebar.expander(f"🔍 {item['query'][:50]}...", expanded=False):
            st.write(f"**{'Time' if st.session_state.language == 'English' else 'وقت'}:** {item['timestamp']}")
            st.write(f"**{'Language' if st.session_state.language == 'English' else 'زبان'}:** {item['language']}")
            st.write("**" + ("Search Result" if st.session_state.language == "English" else "تلاش کا نتیجہ") + ":**")
            st.write(item['search_result'])
            if item['references'] and "🚫" not in item['references']:
                st.write("**" + ("References" if st.session_state.language == "English" else "حوالہ جات") + ":**")
                st.write(item['references'])

# Main Streamlit app with improved UI
def main():
    st.set_page_config(
        page_title="Quranic Insights",
        page_icon="🕌",
        layout="wide"
    )
    
    initialize_session_state()
    
    # CSS for improved UI
    st.markdown("""
    <style>
    .main-header {
        font-family: 'Arial', sans-serif;
        text-align: center;
        color: #006400;
        margin-bottom: 2rem;
    }
    .subtitle {
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .result-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .reference-container {
        background-color: #eaf2f8;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border-left: 5px solid #3498db;
    }
    .stButton>button {
        background-color: #00ffcc;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .language-selector {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Language selector
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("<div class='language-selector'>", unsafe_allow_html=True)
        language_options = ["English", "Urdu"]
        selected_language = st.radio(
            "Select Language / زبان منتخب کریں",
            language_options,
            index=language_options.index(st.session_state.language)
        )
        st.session_state.language = selected_language
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content
    with col1:
        if st.session_state.language == "English":
            st.markdown("<h1 class='main-header'>🕋 Quranic Insights</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtitle'>Illuminating Islamic Wisdom</p>", unsafe_allow_html=True)
            st.markdown("""
            Search for knowledge from Islamic sources including:
            - The Holy Quran
            - Authentic Hadith Collections
            - Islamic Historical Records
            """)
        else:  # Urdu
            st.markdown("<h1 class='main-header'>🕋 قرآنی بصیرتیں</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtitle'>اسلامی حکمت کو روشن کرنا</p>", unsafe_allow_html=True)
            st.markdown("""
            اسلامی ذرائع سے علم تلاش کریں بشمول:
            - قرآن پاک
            - صحیح حدیث کے مجموعے
            - اسلامی تاریخی ریکارڈز
            """)

    try:
        finder = IslamicKnowledgeFinder()
    except ValueError as e:
        error_msg = "⚠️ Configuration Error: Please ensure the API key is properly set." if st.session_state.language == "English" else "⚠️ ترتیب کی غلطی: براہ کرم یقینی بنائیں کہ API کلید صحیح طریقے سے سیٹ ہے۔"
        st.error(error_msg)
        return

    placeholder_text = "Example: What does Islam say about kindness to parents?" if st.session_state.language == "English" else "مثال: اسلام والدین کے ساتھ مہربانی کے بارے میں کیا کہتا ہے؟"
    help_text = "Enter any topic related to Islamic teachings, history, or practices." if st.session_state.language == "English" else "اسلامی تعلیمات، تاریخ، یا طریقوں سے متعلق کوئی بھی موضوع درج کریں۔"
    
    input_text = st.text_area(
        "Enter your question about Islam:" if st.session_state.language == "English" else "اسلام کے بارے میں اپنا سوال درج کریں:",
        placeholder=placeholder_text,
        help=help_text
    )

    button_text = "🔍 Search" if st.session_state.language == "English" else "🔍 تلاش کریں"
    
    if st.button(button_text, type="primary"):
        spinner_text = "Searching Islamic sources..." if st.session_state.language == "English" else "اسلامی ذرائع تلاش کر رہا ہے..."
        
        with st.spinner(spinner_text):
            search_result = finder.search_islamic_knowledge(input_text, st.session_state.language)

            if not search_result:
                error_msg = "⚠️ Failed to get response. Please try again later." if st.session_state.language == "English" else "⚠️ جواب حاصل کرنے میں ناکام۔ براہ کرم بعد میں دوبارہ کوشش کریں۔"
                st.error(error_msg)
                return

            result_heading = "### 🔎 Search Result:" if st.session_state.language == "English" else "### 🔎 تلاش کا نتیجہ:"
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(result_heading)
            st.write(search_result)
            st.markdown("</div>", unsafe_allow_html=True)

            references = None
            if "🚫" not in search_result:
                spinner_text_ref = "Finding detailed references..." if st.session_state.language == "English" else "تفصیلی حوالہ جات تلاش کر رہا ہے..."
                
                with st.spinner(spinner_text_ref):
                    references = finder.get_references(search_result, st.session_state.language)

                    if references:
                        ref_heading = "### 📜 Detailed References:" if st.session_state.language == "English" else "### 📜 تفصیلی حوالہ جات:"
                        st.markdown("<div class='reference-container'>", unsafe_allow_html=True)
                        st.write(ref_heading)
                        st.write(references)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        error_msg = "⚠️ Failed to fetch references" if st.session_state.language == "English" else "⚠️ حوالہ جات حاصل کرنے میں ناکام"
                        st.error(error_msg)

            # Add to history
            add_to_history(input_text, search_result, references, st.session_state.language)

    # Display sidebar
    display_sidebar()

if __name__ == "__main__":
    main()