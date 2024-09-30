import google.generativeai as genai
import streamlit as st
import pandas as pd

# Streamlit app title
st.title("라봉이가 추천하는 제주 어디가?")

# API Key input
GOOGLE_API_KEY = st.text_input("API 키를 입력하세요:", type="password")

# Load 신한카드 소비 데이터 (제주도)
@st.cache_data
def load_data():
    # CSV 파일을 로딩 (여기에 파일 경로를 넣으세요)
    return pd.read_csv('제주도_소비데이터.csv')

if GOOGLE_API_KEY:
    # Configure the API with the provided key
    genai.configure(api_key=GOOGLE_API_KEY)

    @st.cache_resource
    def load_model():
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model

    # Load LLM model
    model = load_model()

    if "chat_session" not in st.session_state:
        st.session_state["chat_session"] = model.start_chat(history=[])

    # Load the 제주도 소비 데이터
    data = load_data()

    # 사용자 입력 - 지역과 음식 카테고리
    region = st.text_input("지역을 입력하세요 (예: 제주시, 서귀포시):")
    category = st.selectbox("음식 카테고리를 선택하세요:", data['MCT_TYPE'].unique())

    # 데이터 필터링 함수
    def filter_data(data, region, category):
        filtered = data[data['ADDR'].str.contains(region) & data['MCT_TYPE'].str.contains(category)]
        return filtered[['MCT_NM', 'ADDR', 'MCT_TYPE']]

    if st.button("맛집 추천 받기"):
        if region and category:
            # 데이터 필터링
            filtered_data = filter_data(data, region, category)
            
            if not filtered_data.empty:
                # LLM에 전달할 프롬프트 구성
                prompt = f"제주도 {region} 지역에서 {category} 유형의 맛집을 추천해줘. 다음은 필터링된 리스트야:\n"
                for idx, row in filtered_data.iterrows():
                    prompt += f"- {row['MCT_NM']} (주소: {row['ADDR']})\n"

                # LLM에게 대화 생성 요청
                with st.spinner("라봉이가 맛집을 추천 중입니다..."):
                    response = st.session_state.chat_session.send_message(prompt, stream=False)
                    full_response = response.text
                
                # 대화 출력
                with st.chat_message("ai"):
                    st.markdown(full_response)
            else:
                st.warning("해당 조건에 맞는 맛집이 없습니다.")
        else:
            st.warning("지역과 카테고리를 모두 입력해주세요.")
else:
    st.warning("API 키를 입력해주세요.")
