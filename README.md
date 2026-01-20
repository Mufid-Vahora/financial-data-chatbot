# financial-data-chatbot
Interactive Financial Chatbot built with Python, Streamlit, and LLMs to analyze trades and holdings data from CSV files

A demo chatbot that allows users to interactively query financial data from trades and holdings CSV files. 
It uses Python, Streamlit, and an LLM (Ollama GPT-OSS) to answer questions strictly based on available data.

- Provides fund performance insights
- Summarizes trades and holdings
- Handles missing/corrupt data gracefully

  ## Features
- Ask questions about trades, holdings, or funds
- Summarizes P&L using PL_YTD
- Returns top-performing funds
- Handles missing data with strict fallback: "Sorry can not find the answer"
- Built with Streamlit for interactive demos

## Demo

Try it locally or deploy to Streamlit Cloud for live interaction.

## Installation

1. Clone the repository
```
git clone https://github.com/mufid-vahora>/financial-data-chatbot.git
cd financial-data-chatbot
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Run the app
```
streamlit run app.py
```

---

## Usage
```
- Upload your `trades.csv` and `holdings.csv` to the project folder
- Ask questions like:
  - "Top 3 funds by PL_YTD"
  - "Total trades for a specific fund"
  - "Holdings as of a certain date"
- Strict fallback for missing data: "Sorry can not find the answer"
```
## Tech Stack
- Python
- Streamlit
- Pandas & SQLAlchemy
- Ollama GPT-OSS (LLM)

## Future Improvements
- Support multiple data formats (Excel, Parquet)
- Add more sophisticated analytics (risk metrics, CAGR)
- Deployment on cloud for multi-user access




