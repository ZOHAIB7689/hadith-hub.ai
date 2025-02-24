# Islamic Knowledge Finder 📖

A Streamlit-based web application that leverages Google's Gemini AI to search and provide references from Islamic texts including the Quran, Hadith, and Islamic history.

## Features ✨

- **Smart Islamic Search**: Search through Islamic texts with specific queries
- **Detailed References**: Get precise references from the Quran and Hadith collections
- **Search History**: Keep track of previous searches in a convenient sidebar
- **User-Friendly Interface**: Clean and intuitive Streamlit-based UI
- **Error Handling**: Robust error handling and retry mechanisms
- **Input Validation**: Ensures proper query formatting and handling

## Prerequisites 🔧

Before running the application, make sure you have Python 3.8+ installed on your system. You'll also need the following:

- Google Gemini API key
- Python packages listed in requirements.txt

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/islamic-knowledge-finder.git
cd islamic-knowledge-finder
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory:
```bash
touch .env
```

5. Add your Gemini API key to the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage 💡

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

3. Enter your question about Islam in the text area

4. Click the "Search" button to get results

5. View your search history in the sidebar

## Dependencies 📚

- `streamlit`: Web application framework
- `crewai`: AI flow management
- `litellm`: LLM interface
- `python-dotenv`: Environment variable management
- `logging`: For application logging

## Project Structure 📁

```
islamic-knowledge-finder/
├── app.py                 # Main application file
├── .env                   # Environment variables
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Environment Variables 🔐

The following environment variables are required:

- `GEMINI_API_KEY`: Your Google Gemini API key

## Contributing 🤝

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## Error Handling 🐛

The application includes comprehensive error handling for:
- API failures
- Invalid inputs
- Missing API keys
- Connection issues

## Limitations ⚠️

- The application requires an active internet connection
- Responses are limited to Islamic knowledge only
- API rate limits may apply depending on your Gemini API plan

## Security 🔒

- API keys are stored securely in environment variables
- Input validation is implemented to prevent injection attacks
- Error messages are sanitized to prevent information leakage

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 🆘

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ for the Islamic community