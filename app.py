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

#st.write("🔐 API key exists:", bool(api_key))

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
            "HTTP-Referer": "https://chatbot-7ok8igz2ldmbtgskkgyxr2.streamlit.app/",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

        data = res.json()



        if "choices" in data:

            return data["choices"][0]["message"]["content"]

        else:

            return "LLM failed to respond. Please try again."


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
        # Infer chart type from user query
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

        if any(word in query.lower() for word in ["chart", "trend", "plot", "compare", "distribution", "graph", "pie", "bar", "line", "histogram"]):
            st.markdown("### 📈 Suggested Chart")

            chart_type = infer_chart_type(query)
            numeric_cols = df.select_dtypes(include='number').columns
            categorical_cols = df.select_dtypes(include='object').columns

            if chart_type == "pie":
                chart_info = {
                    "type": "pie",
                    "x": categorical_cols[0] if len(categorical_cols) > 0 else df.columns[0],
                    "y": None,
                    "group_by": None
                }
            else:
                chart_info = {
                    "type": chart_type,
                    "x": numeric_cols[0] if chart_type == "histogram" else df.columns[0],
                    "y": numeric_cols[0] if chart_type in ["bar", "line"] else None,
                    "group_by": None
                }

            fig = generate_chart(df, chart_info)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
