import streamlit as st
import os
from crewai.flow.flow import Flow
from litellm import completion

# Set API Key (Make sure to store it securely!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class CityFunFact(Flow):
    def function1(self, input_text):
        islamic_keywords = ["Islam", "Quran", "Hadith", "Sunnah", "Prophet", "Allah", "Muslim", "Fiqh", "Seerah", "Sharia", "Hadees"]
        if not any(keyword.lower() in input_text.lower() for keyword in islamic_keywords):
            return "🚫 This question is not related to Islam. Please ask something relevant."
        
        search_prompt = f"""
        Only search in Islamic texts (Quran, Hadith, and Islamic history). If the query is unrelated to Islam, return exactly this message: '🚫 This is not related to Islam.'.
        Question: {input_text}
        """
        response = completion(model="gemini/gemini-2.0-flash", messages=[{"role": "user", "content": search_prompt}], api_key=GEMINI_API_KEY)
        return response["choices"][0]["message"]["content"]

    def function2(self, search_result):
        if "🚫" in search_result:
            return search_result
        explain_prompt = f"find exact references for the: {search_result}"
        response = completion(model="gemini/gemini-2.0-flash", messages=[{"role": "user", "content": explain_prompt}], api_key=GEMINI_API_KEY)
        return response["choices"][0]["message"]["content"]

    def function3(self, elaboration):
        with open("README.md", "w", encoding="utf-8") as file:
            file.write("# Fun Fact Explanation\n\n")
            file.write(elaboration)
        return "✅ README.md has been updated!"

# Streamlit UI
st.title("📖 Islamic Knowledge Finder")
input_text = st.text_input("Enter a topic related to Islam, Quran, or Hadith:")

if st.button("Search"):
    flow = CityFunFact()
    search_result = flow.function1(input_text)
    st.write("### 🔎 Search Result:")
    st.write(search_result)
    
    if "🚫" not in search_result:
        explanation = flow.function2(search_result)
        st.write("### 📜 Elaborated Explanation:")
        st.write(explanation)
        
        flow.function3(explanation)
        st.success("✅ README.md has been updated!")
        
        with open("README.md", "r") as file:
            st.download_button(label="Download README.md", data=file, file_name="README.md", mime="text/markdown")
