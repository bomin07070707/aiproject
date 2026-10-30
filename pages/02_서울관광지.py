
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="MBTI 진로 추천 & 서울 관광 지도",
    page_icon="🧭",
    layout="wide",
)

# ==========================================
# 1. MBTI 진로 추천 데이터
# ==========================================

CAREERS = {
    "ISTJ": {
        "nickname": "꼼꼼한 현실주의자",
        "vibe": "체계와 책임감을 바탕으로 목표를 이루는 유형",
        "jobs": [
            {
                "job": "회계·세무 전문가",
                "major": "회계학과, 세무학과, 경영학과",
                "fit": "정확성, 책임감, 숫자와 규칙을 꼼꼼하게 다루는 태도",
                "salary": "약 3,000만~4,500만 원"
            },
            {
                "job": "데이터 분석가",
                "major": "통계학과, 데이터사이언스학과",
                "fit": "논리적 사고, 세부 사항 확인, 문제 해결",
                "salary": "약 3,500만~5,000만 원"
            }
        ]
    },
    "ISFJ": {
        "nickname": "따뜻한 수호자",
        "vibe": "다른 사람에게 실질적인 도움을 주는 유형",
        "jobs": [
            {
                "job": "간호사",
                "major": "간호학과",
                "fit": "배려심, 꼼꼼함, 협력과 책임감",
                "salary": "약 3,000만~4,200만 원"
            },
            {
                "job": "초등교사",
                "major": "초등교육과",
                "fit": "인내심, 공감 능력, 꾸준한 소통",
                "salary": "약 3,000만~4,500만 원"
            }
        ]
    },
    "INFJ": {
        "nickname": "통찰력 있는 조언자",
        "vibe": "사람과 사회의 의미를 고민하는 유형",
        "jobs": [
            {
                "job": "상담 전문가",
                "major": "심리학과, 상담심리학과",
                "fit": "경청, 공감, 깊이 있는 관찰",
                "salary": "약 2,800만~4,000만 원"
            },
            {
                "job": "콘텐츠 기획자",
                "major": "국어국문학과, 미디어학과",
                "fit": "통찰력, 글쓰기, 창의력",
                "salary": "약 3,000만~4,500만 원"
            }
        ]
    },
    "INTJ": {
        "nickname": "전략적인 설계자",
        "vibe": "큰 그림을 그리고 문제를 구조적으로 해결하는 유형",
        "jobs": [
            {
                "job": "소프트웨어 개발자",
                "major": "컴퓨터공학과, 소프트웨어학과",
                "fit": "논리력, 독립적인 탐구, 지속적인 학습",
                "salary": "약 3,500만~5,500만 원"
            },
            {
                "job": "전략기획 전문가",
                "major": "경영학과, 경제학과",
                "fit": "분석력, 장기적인 관점, 계획 수립",
                "salary": "약 3,500만~5,000만 원"
            }
        ]
    },
    "ISTP": {
        "nickname": "실용적인 해결사",
        "vibe": "직접 탐구하고 실험하며 해결책을 찾는 유형",
        "jobs": [
            {
                "job": "기계 엔지니어",
                "major": "기계공학과, 자동차공학과",
                "fit": "원리 이해, 실습, 문제 해결",
                "salary": "약 3,300만~4,800만 원"
            },
            {
                "job": "정보보안 전문가",
                "major": "정보보호학과, 컴퓨터공학과",
                "fit": "분석력, 집중력, 기술 탐구",
                "salary": "약 3,500만~5,000만 원"
            }
        ]
    },
    "ISFP": {
        "nickname": "감각적인 창작자",
        "vibe": "자신만의 감각과 창의성을 살리는 유형",
        "jobs": [
            {
                "job": "시각 디자이너",
                "major": "시각디자인학과, 산업디자인학과",
                "fit": "미적 감각, 관찰력, 창의성",
                "salary": "약 2,800만~4,200만 원"
            },
            {
                "job": "사진·영상 제작자",
                "major": "영상학과, 사진학과",
                "fit": "표현력, 감각, 관찰 능력",
                "salary": "약 2,700만~4,000만 원"
            }
        ]
    },
    "INFP": {
        "nickname": "상상력 풍부한 이야기꾼",
        "vibe": "가치와 가능성을 중요하게 생각하는 유형",
        "jobs": [
            {
                "job": "작가·에디터",
                "major": "문예창작학과, 국어국문학과",
                "fit": "상상력, 언어 감각, 주제 탐구",
                "salary": "약 2,700만~4,200만 원"
            },
            {
                "job": "UX 콘텐츠 디자이너",
                "major": "디자인학과, 미디어학과",
                "fit": "공감 능력, 창의성, 사용자 이해",
                "salary": "약 3,000만~4,500만 원"
            }
        ]
    },
    "INTP": {
        "nickname": "호기심 많은 탐구자",
        "vibe": "질문을 던지고 원리를 탐구하는 유형",
        "jobs": [
            {
                "job": "연구원",
                "major": "자연과학·공학 계열 학과",
                "fit": "탐구심, 논리력, 가설 검증",
                "salary": "약 3,000만~4,800만 원"
            },
            {
                "job": "AI 엔지니어",
                "major": "컴퓨터공학과, 인공지능학과",
                "fit": "수학적 사고, 실험 정신",
                "salary": "약 4,000만~6,000만 원"
            }
        ]
    },
    "ESTP": {
        "nickname": "에너지 넘치는 실행가",
        "vibe": "현장에서 빠르게 판단하고 행동하는 유형",
        "jobs": [
            {
                "job": "마케팅 기획자",
                "major": "경영학과, 광고홍보학과",
                "fit": "순발력, 소통 능력, 시장 분석",
                "salary": "약 3,000만~4,500만 원"
            },
            {
                "job": "이벤트 기획자",
                "major": "문화콘텐츠학과, 공연예술학과",
                "fit": "현장 대응력, 추진력, 협업",
                "salary": "약 2,800만~4,200만 원"
            }
        ]
    },
    "ESFP": {
        "nickname": "즐거움을 나누는 분위기 메이커",
        "vibe": "사람들과 교류하고 경험을 만들어 가는 유형",
        "jobs": [
            {
                "job": "호텔·관광 서비스 기획자",
                "major": "호텔관광학과, 관광경영학과",
                "fit": "친화력, 서비스 감각, 소통",
                "salary": "약 2,800만~4,200만 원"
            },
            {
                "job": "방송·미디어 진행자",
                "major": "방송영상학과, 언론정보학과",
                "fit": "표현력, 순발력, 대중 소통",
                "salary": "약 2,800만~4,500만 원"
            }
        ]
    },
    "ENFP": {
        "nickname": "아이디어가 샘솟는 활동가",
        "vibe": "새로운 가능성을 발견하고 아이디어를 나누는 유형",
        "jobs": [
            {
                "job": "브랜드 마케터",
                "major": "경영학과, 광고홍보학과",
                "fit": "창의성, 소통 능력, 트렌드 관심",
                "salary": "약 3,000만~4,800만 원"
            },
            {
                "job": "교육 콘텐츠 기획자",
                "major": "교육학과, 교육공학과",
                "fit": "아이디어, 공감, 설명 능력",
                "salary": "약 3,000만~4,500만 원"
            }
        ]
    },
    "ENTP": {
        "nickname": "재치 있는 발명가",
        "vibe": "새로운 접근법을 시도하는 유형",
        "jobs": [
            {
                "job": "창업·사업개발 기획자",
                "major": "경영학과, 경제학과",
                "fit": "아이디어, 설득력, 기회 발견",
                "salary": "약 3,200만~5,000만 원"
            },
            {
                "job": "서비스 기획자",
                "major": "산업공학과, 경영정보학과",
                "fit": "문제 정의, 논리적 토론, 의견 조율",
                "salary": "약 3,300만~5,000만 원"
            }
        ]
    },
    "ESTJ": {
        "nickname": "믿음직한 관리자",
        "vibe": "목표와 역할을 명확히 하고 일을 이끄는 유형",
        "jobs": [
            {
                "job": "프로젝트 매니저",
                "major": "산업공학과, 경영학과",
                "fit": "조직력, 책임감, 일정 관리",
                "salary": "약 3,500만~5,200만 원"
            },
            {
                "job": "물류·운영 관리자",
                "major": "물류학과, 산업공학과",
                "fit": "실행력, 체계적인 관리, 협업",
                "salary": "약 3,200만~4,800만 원"
            }
        ]
    },
    "ESFJ": {
        "nickname": "사람을 연결하는 협력가",
        "vibe": "주변 사람들과 조화를 이루는 유형",
        "jobs": [
            {
                "job": "인사·교육 담당자",
                "major": "경영학과, 교육학과",
                "fit": "공감, 조율 능력, 구성원 지원",
                "salary": "약 3,000만~4,500만 원"
            },
            {
                "job": "공공·복지 분야 기획자",
                "major": "사회복지학과, 행정학과",
                "fit": "협력, 책임감, 소통",
                "salary": "약 2,800만~4,200만 원"
            }
        ]
    },
    "ENFJ": {
        "nickname": "성장을 이끄는 리더",
        "vibe": "사람의 가능성을 발견하고 이끄는 유형",
        "jobs": [
            {
                "job": "교육·진로 컨설턴트",
                "major": "교육학과, 상담학과",
                "fit": "경청, 동기 부여, 소통",
                "salary": "약 2,900만~4,500만 원"
            },
            {
                "job": "홍보·커뮤니케이션 전문가",
                "major": "언론홍보학과, 광고홍보학과",
                "fit": "공감, 설득력, 관계 형성",
                "salary": "약 3,000만~4,600만 원"
            }
        ]
    },
    "ENTJ": {
        "nickname": "목표 지향적인 지휘자",
        "vibe": "도전적인 목표를 세우고 전략적으로 실행하는 유형",
        "jobs": [
            {
                "job": "경영 컨설턴트",
                "major": "경영학과, 경제학과",
                "fit": "전략적 사고, 분석력, 의사결정",
                "salary": "약 3,800만~5,800만 원"
            },
            {
                "job": "제품·사업 책임자",
                "major": "경영학과, 컴퓨터공학과",
                "fit": "목표 설정, 리더십, 통합적 사고",
                "salary": "약 3,800만~5,800만 원"
            }
        ]
    }
}

# ==========================================
# 2. 서울 관광지 TOP 10 데이터
# ==========================================

ATTRACTIONS = [
    {
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "화장품 쇼핑, 길거리 음식, 활기찬 도심 분위기를 즐길 수 있는 대표 관광 지역입니다.",
        "description_en": "A lively shopping district known for cosmetics, street food and a busy city atmosphere.",
        "search": "Myeongdong Seoul"
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": "남산에서 서울의 도심 풍경과 야경을 감상할 수 있습니다.",
        "description_en": "Enjoy panoramic views of Seoul from Namsan.",
        "search": "N Seoul Tower"
    },
    {
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5125,
        "lon": 127.0590,
        "category": "쇼핑·문화",
        "description": "대형 쇼핑 공간과 개방형 별마당도서관으로 유명합니다.",
        "description_en": "A shopping complex featuring the famous Starfield Library.",
        "search": "COEX Starfield Library Seoul"
    },
    {
        "name": "강남역 일대",
        "english": "Gangnam Station Area",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "도심·쇼핑",
        "description": "현대적인 상점과 음식점, 카페가 모여 있는 번화가입니다.",
        "description_en": "A modern district filled with shops, restaurants and cafés.",
        "search": "Gangnam Station Seoul"
    },
    {
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·공연",
        "description": "거리 공연, 개성 있는 상점, 음악과 젊은 문화로 유명합니다.",
        "description_en": "Known for street performances, independent shops and music.",
        "search": "Hongdae Street Seoul"
    },
    {
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5669,
        "lon": 127.0095,
        "category": "건축·전시",
        "description": "독특한 건축물과 디자인 전시, 야간 경관을 즐길 수 있습니다.",
        "description_en": "A striking architectural landmark hosting design exhibitions.",
        "search": "Dongdaemun Design Plaza Seoul"
    },
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·전통문화",
        "description": "조선 왕조의 대표 궁궐로 한국의 전통 건축과 역사를 경험할 수 있습니다.",
        "description_en": "Seoul's best-known royal palace.",
        "search": "Gyeongbokgung Palace Seoul"
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·거리",
        "description": "전통 한옥이 모여 있는 지역입니다. 실제 주민이 거주하므로 조용히 관람해 주세요.",
        "description_en": "A traditional hanok neighborhood. Please keep noise low.",
        "search": "Bukchon Hanok Village Seoul"
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡, 김밥 등 한국 음식과 전통시장 분위기를 경험할 수 있습니다.",
        "description_en": "A traditional market popular for Korean street food.",
        "search": "Gwangjang Market Seoul"
    },
    {
        "name": "서울숲",
        "english": "Seoul Forest",
        "lat": 37.5444,
        "lon": 127.0374,
        "category": "공원·자연",
        "description": "도심 속 산책과 휴식을 즐길 수 있는 넓은 공원입니다.",
        "description_en": "A spacious urban park for walking and relaxing.",
        "search": "Seoul Forest"
    }
]

# ==========================================
# 3. 앱 제목
# ==========================================

st.title("🧭 MBTI 진로 추천 & 서울 관광 지도")

st.caption(
    "나의 성향에 맞는 진로를 살펴보고, "
    "외국인 관광객에게 인기 있는 서울 명소도 찾아보세요."
)

career_tab, travel_tab, about_tab = st.tabs(
    ["🎯 MBTI 진로 추천", "🗺️ 서울 관광 TOP 10", "ℹ️ 안내"]
)

# ==========================================
# 4. MBTI 진로 추천 화면
# ==========================================

with career_tab:

    st.header("나의 MBTI로 진로 탐색하기")

    st.write(
        "MBTI는 진로를 결정하는 기준이 아니라 "
        "나의 관심과 강점을 생각해 보는 출발점입니다."
    )

    mbti = st.selectbox(
        "나의 MBTI를 선택하세요",
        list(CAREERS.keys())
    )

    profile = CAREERS[mbti]

    st.subheader(
        f"{mbti} · {profile['nickname']}"
    )

    st.info(profile["vibe"])

    cols = st.columns(2)

    for i, job in enumerate(profile["jobs"]):

        with cols[i]:

            st.markdown(
                f"### {i + 1}. {job['job']}"
            )

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

# ==========================================
# 5. 서울 관광지도 화면
# ==========================================

with travel_tab:

    st.header(
        "외국인 관광객이 즐겨 찾는 서울 명소 TOP 10"
    )

    st.write(
        "서울의 주요 관광 명소를 선정해 지도에 표시했습니다. "
        "공식 단일 순위가 아닌 여행 추천 목록입니다."
    )

    left, right = st.columns([1, 2])

    # 관광지 선택
    with left:

        selected_name = st.selectbox(
            "관광지를 선택하세요",
            [
                f"{i + 1}. {place['name']} ({place['english']})"
                for i, place in enumerate(ATTRACTIONS)
            ]
        )

        selected_index = [
            f"{i + 1}. {place['name']} ({place['english']})"
            for i, place in enumerate(ATTRACTIONS)
        ].index(selected_name)

        selected = ATTRACTIONS[selected_index]

        st.subheader(selected["name"])

        st.caption(selected["english"])

        st.markdown(
            f"**분류:** {selected['category']}"
        )

        st.write(selected["description"])

        st.write(selected["description_en"])

        map_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + selected["search"].replace(" ", "+")
        )

        st.link_button(
            "Google 지도에서 위치 보기",
            map_url
        )

    # 서울 지도
    with right:

        st.subheader("서울 관광지 위치 지도")

        map_df = pd.DataFrame(
            [
                {
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "name": p["name"]
                }
                for p in ATTRACTIONS
            ]
        )

        st.map(
            map_df,
            latitude="lat",
            longitude="lon",
            size=120,
            color="#E4572E",
            zoom=11
        )

        st.caption(
            "지도 위의 점은 관광지의 대략적인 중심 위치입니다."
        )

    # 관광지 전체 목록
    st.divider()

    st.subheader("관광지 TOP 10 목록")

    for i, place in enumerate(ATTRACTIONS, start=1):

        with st.expander(
            f"{i}. {place['name']} · {place['english']}"
        ):

            st.write(place["description"])

            st.caption(
                f"분류: {place['category']}"
            )

            url = (
                "https://www.google.com/maps/search/?api=1&query="
                + place["search"].replace(" ", "+")
            )

            st.link_button(
                "지도에서 찾기",
                url,
                key=f"map_{i}"
            )

# ==========================================
# 6. 안내 화면
# ==========================================

with about_tab:

    st.header("데이터와 이용 안내")

    st.markdown(
        """
        ### 관광지 선정 참고 자료

        - 서울시 외국인 방문 동향 분석
        - 외국인 관광객 방문 지역 및 관광 리뷰
        - 서울의 대표 관광 명소

        ### 주의 사항

        - 관광지 TOP 10은 여행 추천용 목록이며 공식 순위가 아닙니다.
        - 지도 좌표는 관광지 중심의 대략적인 위치입니다.
        - 운영 시간, 휴무일, 입장료는 방문 전에 확인하세요.
        - 북촌한옥마을은 주민 거주 지역이므로 정숙하게 관람해 주세요.

        ### 진로 정보

        - 연봉은 직업별 참고용 추정 범위입니다.
        - 실제 연봉은 경력과 기업에 따라 달라집니다.
        - MBTI는 진로 적성을 확정하는 검사가 아닙니다.
        """
    )

    st.markdown(
        "[서울시 관광 정보](https://english.seoul.go.kr/)  \n"
        "[한국문화관광연구원](https://www.kcti.re.kr/)"
    )

# ==========================================
# 7. 하단 안내
# ==========================================

st.divider()

st.caption(
    "© MBTI 진로 탐색 및 서울 관광 정보 교육용 앱"
)
