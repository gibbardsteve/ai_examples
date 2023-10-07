import streamlit as st

# ----- SETTINGS -----
page_title = "AI Chat Interface"
page_icon = ":robot_face:"  # https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
layout = "centered"
# --------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# ----- DROPDOWN
options = ["Ask Question", "Calculate Tokens"]
ai_models = ["gpt-3.5-turbo"]

# ----- INPUT ---------
st.header("Ask me a question")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    col1.selectbox("Chat Option", options, key="option")
    col2.selectbox("AI Model", ai_models, key="ai_model")

    "---"
    with st.expander("Question", expanded=True):
        question = st.text_area(
            "",
            placeholder="Add your question here ...",
            help="Write your question here",
        )

    "---"
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Trigger question to AI
        option_selection = st.session_state["option"]
        model_selection = st.session_state["ai_model"]

        st.write(f"AI Option - {option_selection}")
        st.write(f"AI Model - {model_selection}")
        st.write(f"Question entered - {question}")
        st.success("Question Sent")

        "---"
        with st.expander("Answer", expanded=True):
            answer = st.text_area("", value="Ask whatever you like!", disabled=False)
