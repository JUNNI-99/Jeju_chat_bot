import os
import google.generativeai as genai
import streamlit as st

GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')

if not GOOGLE_API_KEY:
    st.error("API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

    st.title("라봉이가 추천하는 제주 어디가?")
    
    @st.cache_resource
    def load_model():
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model

    model = load_model()

    if "chat_session" not in st.session_state:
        st.session_state["chat_session"] = model.start_chat(history=[])

    for content in st.session_state.chat_session.history:
        with st.chat_message("ai" if content.role == "model" else "user"):
            st.markdown(content.parts[0].text)

    if prompt := st.chat_input("메세지를 입력하세요."):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("ai"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("메세지 답변 처리 중 입니다."):
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response)
