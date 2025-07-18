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

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Excel file loaded successfully!")

    st.subheader("Data Preview")
    st.dataframe(df.head())

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
            "HTTP-Referer": "https://streamlit.io",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        
        try:
            data = res.json()
        except Exception:
            st.error("❌ OpenRouter returned a non-JSON response")
            st.code(res.text)
            return "❌ Error"
        
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            st.error("❌ OpenRouter API Error")
            st.code(data)
            return "❌ LLM failed to respond. Please try again."


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

    query = st.text_input("Ask a question about your Excel data:")

    if query:
        with st.spinner("Thinking..."):
            answer = ask_openrouter_llm(query, df)
        st.subheader("💬 Response")
        st.write(answer)

        # (Optional) Visualization suggestions (advanced users can parse LLM suggestion)
        if any(word in query.lower() for word in ["chart", "trend", "plot", "compare", "distribution", "graph"]):
            st.markdown("### 📈 Suggested Chart")
            chart_info = {
                "type": "bar",  # can be improved with NLP + LLM reasoning
                "x": df.columns[0],
                "y": df.select_dtypes(include='number').columns[0],
                "group_by": None
            }
            fig = generate_chart(df, chart_info)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
