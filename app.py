import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(page_title="Excel Chat Assistant", layout="wide")
st.title("📊 Excel Insight Chatbot")

# Show if API key is detected
st.write("🔐 API key present:", bool(api_key))
st.write("🔐 Key length:", len(api_key) if api_key else "None")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Excel file loaded successfully!")

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # LLM Query Function
    def ask_openrouter_llm(user_query, df):
        sample = df.head(5).to_dict(orient="records")
        columns = ", ".join(df.columns[:6])

        prompt = f"""You are a smart data assistant.

The dataset has columns like: {columns} (and more).
Here are some sample rows:
{sample}

User asked: "{user_query}"

Respond with a short, direct answer only. Do not include code or explanation.
Just give the final answer in one sentence.
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://chatbot-7ok8igz2ldmbtgskkgyxr2.streamlit.app/",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            data = res.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                st.error("❌ OpenRouter API Error")
                st.code(data)
                return "LLM failed to respond. Please try again."
        except Exception as e:
            st.error("❌ LLM request failed")
            st.code(str(e))
            return "LLM failed to respond. Please try again."

    # Chart helper
    def generate_chart(df, info):
        try:
            chart_type = info.get("type")
            x = info.get("x")
            y = info.get("y")
            group_by = info.get("group_by")

            if chart_type == "bar":
                return px.bar(df, x=x, y=y, color=group_by)
            elif chart_type == "line":
                return px.line(df, x=x, y=y, color=group_by)
            elif chart_type == "pie":
                return px.pie(df, names=x, values=y)
            elif chart_type == "histogram":
                return px.histogram(df, x=x)
        except Exception as e:
            st.error(f"Chart error: {e}")
        return None

    # Chart type inference
    def infer_chart_type(query):
        q = query.lower()
        if "pie" in q:
            return "pie"
        elif "line" in q or "trend" in q:
            return "line"
        elif "bar" in q or "compare" in q:
            return "bar"
        elif "histogram" in q or "distribution" in q:
            return "histogram"
        else:
            return "bar"

    # Text input for question
    query = st.text_input("Ask a question about your Excel data:")

    if query:
        with st.spinner("Thinking..."):
            answer = ask_openrouter_llm(query, df)

        st.subheader("💬 Response")
        st.write(answer)

        if any(word in query.lower() for word in ["chart", "plot", "compare", "distribution", "trend", "pie", "bar", "line", "histogram"]):
            st.markdown("### 📈 Chart Based on Query")

            chart_type = infer_chart_type(query)
            numeric_cols = df.select_dtypes(include='number').columns
            object_cols = df.select_dtypes(include='object').columns

            chart_info = {
                "type": chart_type,
                "x": numeric_cols[0] if chart_type == "histogram" else object_cols[0],
                "y": numeric_cols[0] if chart_type in ["bar", "line"] else None,
                "group_by": None
            }

            fig = generate_chart(df, chart_info)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
