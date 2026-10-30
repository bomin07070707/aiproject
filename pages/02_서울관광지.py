
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="MBTI 진로 추천 & 서울 관광 지도",
    page_icon="🧭",
    layout="wide",
)

# =========================================================
# 1. MBTI 진로 추천 데이터
# =========================================================

CAREERS = {
    "ISTJ": {
        "nickname": "꼼꼼한 현실주의자",
        "vibe": "체계와 책임감을 바탕으로 차근차근 목표를 이루는 유형",
        "jobs": [
            {"job": "회계·세무 전문가", "major": "회계학과, 세무학과, 경영학과",
             "fit": "정확성, 책임감, 숫자와 규칙을 꼼꼼하게 다루는 태도",
             "salary": "약 3,000만~4,500만 원"},
            {"job": "데이터 분석가", "major": "통계학과, 데이터사이언스학과, 산업공학과",
             "fit": "논리적 사고, 세부 사항 확인, 꾸준한 문제 해결",
             "salary": "약 3,500만~5,000만 원"},
        ],
    },
    "ISFJ": {
        "nickname": "따뜻한 수호자",
        "vibe": "세심하게 살피고 다른 사람에게 실질적인 도움을 주는 유형",
        "jobs": [
            {"job": "간호사", "major": "간호학과",
             "fit": "배려심, 꼼꼼함, 협력과 책임감",
             "salary": "약 3,000만~4,200만 원"},
            {"job": "초등교사", "major": "초등교육과",
             "fit": "인내심, 공감 능력, 꾸준한 소통",
             "salary": "약 3,000만~4,500만 원"},
        ],
    },
    "INFJ": {
        "nickname": "통찰력 있는 조언자",
        "vibe": "사람과 사회의 의미를 고민하고 더 나은 방향을 찾는 유형",
        "jobs": [
            {"job": "상담 전문가", "major": "심리학과, 상담심리학과, 교육학과",
             "fit": "경청, 공감, 깊이 있는 관찰과 윤리 의식",
             "salary": "약 2,800만~4,000만 원"},
            {"job": "콘텐츠 기획자", "major": "국어국문학과, 미디어학과, 문예창작학과",
             "fit": "통찰력, 글쓰기, 사람들의 관심과 맥락을 이해하는 능력",
             "salary": "약 3,000만~4,500만 원"},
        ],
    },
    "INTJ": {
        "nickname": "전략적인 설계자",
        "vibe": "큰 그림을 그리고 복잡한 문제를 구조적으로 해결하는 유형",
        "jobs": [
            {"job": "소프트웨어 개발자", "major": "컴퓨터공학과, 소프트웨어학과",
             "fit": "논리력, 독립적인 탐구, 지속적인 학습",
             "salary": "약 3,500만~5,500만 원"},
            {"job": "전략기획 전문가", "major": "경영학과, 경제학과, 산업공학과",
             "fit": "분석력, 장기적인 관점, 계획 수립",
             "salary": "약 3,500만~5,000만 원"},
        ],
    },
    "ISTP": {
        "nickname": "실용적인 해결사",
        "vibe": "직접 탐구하고 실험하며 작동하는 해결책을 찾는 유형",
        "jobs": [
            {"job": "기계·자동차 엔지니어", "major": "기계공학과, 자동차공학과",
             "fit": "원리 이해, 실습 선호, 문제 해결 능력",
             "salary": "약 3,300만~4,800만 원"},
            {"job": "정보보안 전문가", "major": "정보보호학과, 컴퓨터공학과",
             "fit": "분석력, 집중력, 기술을 직접 시험하는 태도",
             "salary": "약 3,500만~5,000만 원"},
        ],
    },
    "ISFP": {
        "nickname": "감각적인 창작자",
        "vibe": "자신만의 감각을 살리고 주변의 분위기를 섬세하게 느끼는 유형",
        "jobs": [
            {"job": "시각 디자이너", "major": "시각디자인학과, 산업디자인학과",
             "fit": "미적 감각, 관찰력, 사용자 입장에서 생각하는 태도",
             "salary": "약 2,800만~4,200만 원"},
            {"job": "사진·영상 제작자", "major": "영상학과, 사진학과, 미디어학과",
             "fit": "표현력, 감각, 현장을 관찰하는 능력",
             "salary": "약 2,700만~4,000만 원"},
        ],
    },
    "INFP": {
        "nickname": "상상력 풍부한 이야기꾼",
        "vibe": "가치와 가능성을 중요하게 생각하고 창의적으로 표현하는 유형",
        "jobs": [
            {"job": "작가·에디터", "major": "문예창작학과, 국어국문학과, 미디어학과",
             "fit": "상상력, 언어 감각, 깊이 있는 주제 탐구",
             "salary": "약 2,700만~4,200만 원"},
            {"job": "UX 콘텐츠 디자이너", "major": "디자인학과, HCI, 미디어학과",
             "fit": "공감 능력, 창의성, 사용자 경험을 이해하는 태도",
             "salary": "약 3,000만~4,500만 원"},
        ],
    },
    "INTP": {
        "nickname": "호기심 많은 탐구자",
        "vibe": "질문을 던지고 원리를 파고들며 새로운 아이디어를 만드는 유형",
        "jobs": [
            {"job": "연구원", "major": "관심 분야의 자연과학·공학 계열 학과",
             "fit": "탐구심, 논리력, 가설을 검증하는 태도",
             "salary": "약 3,000만~4,800만 원"},
            {"job": "AI·머신러닝 엔지니어", "major": "컴퓨터공학과, 인공지능학과, 수학과",
             "fit": "수학적 사고, 실험 정신, 새로운 기술 학습",
             "salary": "약 4,000만~6,000만 원"},
        ],
    },
    "ESTP": {
        "nickname": "에너지 넘치는 실행가",
        "vibe": "현장에서 빠르게 판단하고 사람들과 직접 부딪히며 배우는 유형",
        "jobs": [
            {"job": "마케팅 기획자", "major": "경영학과, 광고홍보학과",
             "fit": "순발력, 소통 능력, 시장 반응을 읽는 감각",
             "salary": "약 3,000만~4,500만 원"},
            {"job": "이벤트·공연 기획자", "major": "문화콘텐츠학과, 공연예술학과",
             "fit": "현장 대응력, 추진력, 협업 능력",
             "salary": "약 2,800만~4,200만 원"},
        ],
    },
    "ESFP": {
        "nickname": "즐거움을 나누는 분위기 메이커",
        "vibe": "사람들과 교류하고 생생한 경험을 만들어 가는 유형",
        "jobs": [
            {"job": "호텔·관광 서비스 기획자", "major": "호텔관광학과, 관광경영학과",
             "fit": "친화력, 서비스 감각, 다양한 사람을 이해하는 태도",
             "salary": "약 2,800만~4,200만 원"},
            {"job": "방송·미디어 진행자", "major": "방송영상학과, 언론정보학과",
             "fit": "표현력, 순발력, 대중과 소통하는 능력",
             "salary": "약 2,800만~4,500만 원"},
        ],
    },
    "ENFP": {
        "nickname": "아이디어가 샘솟는 활동가",
        "vibe": "새로운 가능성을 발견하고 사람들과 아이디어를 나누는 유형",
        "jobs": [
            {"job": "브랜드 마케터", "major": "경영학과, 광고홍보학과, 미디어학과",
             "fit": "창의성, 소통 능력, 트렌드에 대한 호기심",
             "salary": "약 3,000만~4,800만 원"},
            {"job": "교육 콘텐츠 기획자", "major": "교육학과, 교육공학과, 콘텐츠학과",
             "fit": "아이디어 발상, 공감, 복잡한 내용을 쉽게 전달하는 능력",
             "salary": "약 3,000만~4,500만 원"},
        ],
    },
    "ENTP": {
        "nickname": "재치 있는 발명가",
        "vibe": "기존 방식에 질문을 던지고 새로운 접근법을 시도하는 유형",
        "jobs": [
            {"job": "창업·사업개발 기획자", "major": "경영학과, 경제학과, 창업학과",
             "fit": "아이디어 발상, 설득력, 기회를 발견하는 능력",
             "salary": "약 3,200만~5,000만 원"},
            {"job": "서비스 기획자", "major": "산업공학과, 경영정보학과, 컴퓨터공학과",
             "fit": "문제 정의, 논리적 토론, 다양한 의견 조율",
             "salary": "약 3,300만~5,000만 원"},
        ],
    },
    "ESTJ": {
        "nickname": "믿음직한 관리자",
        "vibe": "목표와 역할을 명확히 하고 일을 효율적으로 이끄는 유형",
        "jobs": [
            {"job": "프로젝트 매니저", "major": "산업공학과, 경영학과",
             "fit": "조직력, 책임감, 일정과 자원 관리",
             "salary": "약 3,500만~5,200만 원"},
            {"job": "물류·운영 관리자", "major": "물류학과, 산업공학과, 경영학과",
             "fit": "실행력, 체계적인 관리, 협업과 의사소통",
             "salary": "약 3,200만~4,800만 원"},
        ],
    },
    "ESFJ": {
        "nickname": "사람을 연결하는 협력가",
        "vibe": "주변 사람들과 조화를 이루고 함께 성과를 만드는 유형",
        "jobs": [
            {"job": "인사·교육 담당자", "major": "경영학과, 교육학과, 심리학과",
             "fit": "공감, 조율 능력, 구성원의 성장을 돕는 태도",
             "salary": "약 3,000만~4,500만 원"},
            {"job": "공공·복지 분야 기획자", "major": "사회복지학과, 행정학과",
             "fit": "협력, 책임감, 사람과 제도를 연결하는 능력",
             "salary": "약 2,800만~4,200만 원"},
        ],
    },
    "ENFJ": {
        "nickname": "성장을 이끄는 리더",
        "vibe": "사람의 가능성을 발견하고 공동의 목표를 향해 이끄는 유형",
        "jobs": [
            {"job": "교육·진로 컨설턴트", "major": "교육학과, 상담학과, 심리학과",
             "fit": "경청, 동기 부여, 설명과 소통 능력",
             "salary": "약 2,900만~4,500만 원"},
            {"job": "홍보·커뮤니케이션 전문가", "major": "언론홍보학과, 광고홍보학과",
             "fit": "공감, 설득력, 관계 형성과 메시지 전달",
             "salary": "약 3,000만~4,600만 원"},
        ],
    },
    "ENTJ": {
        "nickname": "목표 지향적인 지휘자",
        "vibe": "도전적인 목표를 세우고 전략적으로 실행하는 유형",
        "jobs": [
            {"job": "경영 컨설턴트", "major": "경영학과, 경제학과, 산업공학과",
             "fit": "전략적 사고, 분석력, 의사결정 능력",
             "salary": "약 3,800만~5,800만 원"},
            {"job": "제품·사업 책임자", "major": "경영학과, 컴퓨터공학과, 산업공학과",
             "fit": "목표 설정, 리더십, 여러 분야를 통합하는 능력",
             "salary": "약 3,800만~5,800만 원"},
        ],
    },
}

# =========================================================
# 2. 서울 관광지 TOP 10 데이터
# =========================================================

ATTRACTIONS = [
    {
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "화장품 쇼핑, 길거리 음식, 활기찬 도심 분위기를 즐길 수 있는 대표 관광 지역입니다.",
        "description_en": "A lively shopping district known for cosmetics, street food and a busy city atmosphere.",
        "search": "Myeongdong Seoul",
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": "남산에서 서울의 도심 풍경과 야경을 감상할 수 있습니다.",
        "description_en": "Enjoy panoramic views of Seoul from Namsan, especially around sunset.",
        "search": "N Seoul Tower",
    },
    {
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5125,
        "lon": 127.0590,
        "category": "쇼핑·문화",
        "description": "대형 쇼핑·전시 공간과 개방형 별마당도서관으로 유명합니다.",
        "description_en": "A large shopping and exhibition complex featuring Starfield Library.",
        "search": "COEX Starfield Library Seoul",
    },
    {
        "name": "강남역 일대",
        "english": "Gangnam Station Area",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "도심·쇼핑",
        "description": "현대적인 상점과 음식점, 카페가 모여 있는 서울의 대표 번화가입니다.",
        "description_en": "A busy modern district filled with shops, restaurants and cafés.",
        "search": "Gangnam Station Seoul",
    },
    {
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·공연",
        "description": "거리 공연, 개성 있는 상점, 음악과 젊은 문화로 유명합니다.",
        "description_en": "Known for street performances, independent shops and music.",
        "search": "Hongdae Street Seoul",
    },
    {
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5669,
        "lon": 127.0095,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축물과 디자인 전시, 야간 경관을 즐길 수 있습니다.",
        "description_en": "A striking architectural landmark hosting design exhibitions and events.",
        "search": "Dongdaemun Design Plaza Seoul",
    },
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·전통문화",
        "description": "조선 왕조의 대표 궁궐로 한국의 전통 건축과 역사를 경험할 수 있습니다.",
        "description_en": "Seoul's best-known royal palace, offering a glimpse into Korean history.",
        "search": "Gyeongbokgung Palace Seoul",
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·거리",
        "description": "전통 한옥이 모여 있는 지역입니다. 실제 주민이 거주하므로 조용히 관람해 주세요.",
        "description_en": "A traditional hanok neighborhood. Please keep noise low because people live here.",
        "search": "Bukchon Hanok Village Seoul",
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡, 김밥 등 한국 길거리 음식과 전통시장 분위기를 경험할 수 있습니다.",
        "description_en": "A traditional market popular for Korean street food and local atmosphere.",
        "search": "Gwangjang Market Seoul",
    },
    {
        "name": "서울숲",
        "english": "Seoul Forest",
        "lat": 37.5444,
        "lon": 127.0374,
        "category": "공원·자연",
        "description": "도심 속 산책과 휴식을 즐길 수 있는 넓은 공원입니다.",
        "description_en": "A spacious urban park for walking and relaxing, close to Seongsu-dong.",
        "search": "Seoul Forest",
    },
]


# =========================================================
# 3. Folium 지도 생성 함수
# =========================================================

def make_seoul_map(selected_name=None):

    seoul_map = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for index, place in enumerate(ATTRACTIONS, start=1):

        is_selected = place["name"] == selected_name

        popup_html = f"""
        <div style="width:230px; font-family:Arial,sans-serif;">
            <h4>{index}. {place['name']}</h4>
            <b>{place['english']}</b><br>
            <span>{place['category']}</span>
            <hr>
            <p>{place['description']}</p>
        </div>
        """

        folium.Marker(
            location=[place["lat"], place["lon"]],
            tooltip=f"{index}. {place['name']} ({place['english']})",
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(
                color="red" if is_selected else "blue",
                icon="star" if is_selected else "info-sign",
                prefix="glyphicon",
            ),
        ).add_to(seoul_map)

    return seoul_map


# =========================================================
# 4. 앱 제목 및 탭
# =========================================================

st.title("🧭 MBTI 진로 추천 & 서울 관광 지도")

st.caption(
    "나의 성향에 맞는 진로를 살펴보고, "
    "외국인 관광객에게 인기 있는 서울 명소도 찾아보세요."
)

career_tab, travel_tab, about_tab = st.tabs(
    ["🎯 MBTI 진로 추천", "🗺️ 서울 관광 TOP 10", "ℹ️ 안내"]
)


# =========================================================
# 5. MBTI 진로 추천
# =========================================================

with career_tab:

    st.header("나의 MBTI로 진로 탐색하기")

    st.write(
        "MBTI는 진로를 결정하는 기준이 아니라, "
        "나의 관심과 강점을 생각해 보는 출발점입니다."
    )

    mbti = st.selectbox(
        "나의 MBTI를 선택하세요",
        list(CAREERS.keys()),
    )

    profile = CAREERS[mbti]

    st.subheader(f"{mbti} · {profile['nickname']}")

    st.info(profile["vibe"])

    columns = st.columns(2)

    for index, job in enumerate(profile["jobs"]):

        with columns[index]:

            st.markdown(f"### {index + 1}. {job['job']}")

            st.markdown(
                f"**관련 학과**  \n{job['major']}"
            )

            st.markdown(
                f"**잘 발휘할 수 있는 강점**  \n{job['fit']}"
            )

            st.markdown(
                f"**연봉 참고 범위**  \n{job['salary']}"
            )

            st.caption(
                "참고용 추정 범위이며 실제 연봉과 다를 수 있습니다."
            )

    st.warning(
        "MBTI만으로 적합한 직업을 단정할 수는 없습니다. "
        "흥미, 가치관, 과목 선호도와 경험도 함께 살펴보세요."
    )

    st.markdown(
        "[고용24 직업정보](https://www.work24.go.kr/) · "
        "[커리어넷 진로정보](https://www.career.go.kr/)"
    )


# =========================================================
# 6. 서울 관광 지도 - Folium
# =========================================================

with travel_tab:

    st.header("외국인 관광객을 위한 서울 관광 명소 TOP 10")

    st.write(
        "서울의 대표 관광 명소 10곳을 Folium 지도에 표시했습니다. "
        "마커를 클릭하면 관광지 설명을 볼 수 있습니다."
    )

    place_names = [
        f"{index}. {place['name']} ({place['english']})"
        for index, place in enumerate(ATTRACTIONS, start=1)
    ]

    selected_label = st.selectbox(
        "관광지를 선택하면 지도에서 해당 마커가 빨간색으로 표시됩니다.",
        place_names,
    )

    selected_index = place_names.index(selected_label)

    selected_place = ATTRACTIONS[selected_index]

    info_col1, info_col2 = st.columns([2, 1])

    with info_col1:

        st.subheader(selected_place["name"])

        st.caption(selected_place["english"])

        st.write(selected_place["description"])

        st.write(selected_place["description_en"])

    with info_col2:

        st.metric("관광지 번호", f"{selected_index + 1} / 10")

        st.caption(selected_place["category"])

        google_map_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + selected_place["search"].replace(" ", "+")
        )

        st.link_button(
            "Google 지도에서 길찾기",
            google_map_url,
        )

    st.divider()

    # Folium 지도 생성
    seoul_map = make_seoul_map(selected_place["name"])

    # Streamlit 화면에 Folium 지도 출력
    st_folium(
        seoul_map,
        width=None,
        height=620,
        returned_objects=[],
        use_container_width=True,
        key="seoul_tourism_folium_map",
    )

    st.caption(
        "파란색 마커는 추천 관광지, 빨간색 마커는 현재 선택한 관광지입니다. "
        "마커를 클릭하면 한국어 설명과 영어 이름을 확인할 수 있습니다."
    )

    st.divider()

    st.subheader("서울 관광지 TOP 10 목록")

    for index, place in enumerate(ATTRACTIONS, start=1):

        with st.expander(
            f"{index}. {place['name']} · {place['english']}"
        ):

            st.write(place["description"])

            st.write(place["description_en"])

            st.caption(f"분류: {place['category']}")

            url = (
                "https://www.google.com/maps/search/?api=1&query="
                + place["search"].replace(" ", "+")
            )

            st.link_button(
                "Google 지도에서 위치 보기",
                url,
                key=f"google_map_{index}",
            )


# =========================================================
# 7. 안내
# =========================================================

with about_tab:

    st.header("데이터와 이용 안내")

    st.markdown(
        """
        ### 관광지 선정 참고 자료

        - 서울시 외국인 방문 동향 및 관광 관련 자료
        - 서울의 대표 관광 명소
        - 외국인 관광객이 많이 찾는 쇼핑·문화·역사·자연 관광 지역

        ### 지도 안내

        - 지도는 Folium과 OpenStreetMap 타일을 사용합니다.
        - 마커를 클릭하면 관광지 설명을 볼 수 있습니다.
        - 지도 확대·축소와 이동이 가능합니다.
        - 관광지 좌표는 해당 장소의 대략적인 중심 위치입니다.
        - 지도 타일을 불러오려면 인터넷 연결이 필요합니다.

        ### 주의 사항

        - TOP 10은 공식 통계 순위가 아닌 여행 추천용 큐레이션입니다.
        - 운영 시간, 휴무일, 입장료는 방문 전에 확인하세요.
        - 북촌한옥마을은 주민 거주 지역이므로 정숙하게 관람해 주세요.

        ### 진로 정보

        - 연봉은 직업별 참고용 추정 범위입니다.
        - 실제 연봉은 경력과 기업에 따라 달라집니다.
        - MBTI는 진로 적성을 확정하는 검사가 아닙니다.
        """
    )

    st.markdown(
        "[서울시 공식 홈페이지](https://english.seoul.go.kr/)  \n"
        "[한국문화관광연구원](https://www.kcti.re.kr/)  \n"
        "[OpenStreetMap](https://www.openstreetmap.org/)"
    )


# =========================================================
# 8. 하단 안내
# =========================================================

st.divider()

st.caption(
    "© MBTI 진로 탐색 및 서울 관광 정보 교육용 앱"
)
