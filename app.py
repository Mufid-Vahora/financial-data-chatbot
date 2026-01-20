import re
import pandas as pd
import streamlit as st
import logging
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import ChatOllama

logging.basicConfig(level=logging.ERROR)

# -------------------------------
# Financial Chatbot (UNCHANGED LOGIC)
# -------------------------------
class FinancialChatbot:
    def __init__(self, trades_path, holdings_path):
        self.trades_path = trades_path
        self.holdings_path = holdings_path
        self.engine = self._init_database()
        self.agent = self._init_agent()

    def _init_database(self):
        df_trades = pd.read_csv(
            self.trades_path,
            na_values=["NULL", "null", ""],
            keep_default_na=True
        )

        if {"TradeDate", "SettleDate"}.issubset(df_trades.columns):
            date_cols = ["TradeDate", "SettleDate"]
        else:
            date_cols = [c for c in df_trades.columns if re.search("date", c, re.I)]

        for col in date_cols:
            df_trades[col] = pd.to_datetime(df_trades[col], errors="coerce")

        df_holdings = pd.read_csv(
            self.holdings_path,
            na_values=["NULL", "null", ""],
            keep_default_na=True
        )

        known_dates = [
            c for c in ["AsOfDate", "InceptionDate", "HoldingDate", "TradeDate"]
            if c in df_holdings.columns
        ]
        holdings_date_cols = known_dates if known_dates else [
            c for c in df_holdings.columns if re.search("date", c, re.I)
        ]

        for col in holdings_date_cols:
            df_holdings[col] = pd.to_datetime(
                df_holdings[col], dayfirst=True, errors="coerce"
            )

        engine = create_engine("sqlite:///financial.db")
        df_trades.to_sql("trades", engine, index=False, if_exists="replace")
        df_holdings.to_sql("holdings", engine, index=False, if_exists="replace")

        return engine

    def _init_agent(self):
        db = SQLDatabase(self.engine)

        llm = ChatOllama(
            model="gpt-oss:120b-cloud",
            temperature=0,
            num_ctx=8192
        )

        system_instruction = """
You are an expert Financial Data Analyst with access to two tables: 'trades' and 'holdings'.

RULES:
1. TradeDate is corrupted (NULL/NaT).
   - If user asks date/year-based trade questions → reply EXACTLY:
     "Sorry can not find the answer"

2. Performance / P&L:
   - Use holdings.PL_YTD
   - Rank funds by SUM(PL_YTD) DESC

3. Strict fallback:
   - If data is missing or unavailable → reply EXACTLY:
     "Sorry can not find the answer"

4. Use SQL aggregation only (COUNT, SUM, AVG).
"""

        return create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=True,
            prefix=system_instruction
        )

    def ask(self, question: str) -> str:
        try:
            result = self.agent.invoke(question)
            if isinstance(result, dict):
                return result.get("output") or result.get("result") or str(result)
            return str(result)
        except Exception:
            return "Sorry can not find the answer"


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Financial Chatbot", layout="wide")
st.title("📊 Financial Data Chatbot")
st.caption("Answers strictly from holdings.csv & trades.csv")

@st.cache_resource
def load_bot():
    return FinancialChatbot(
        trades_path="trades.csv",
        holdings_path="holdings.csv"
    )

bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(msg)

question = st.chat_input("Ask a question about funds, holdings, or trades")

if question:
    st.session_state.messages.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        answer = bot.ask(question)
        st.markdown(answer)

    st.session_state.messages.append(("assistant", answer))
