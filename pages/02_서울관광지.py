
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from urllib.parse import quote_plus

st.set_page_config(
    page_title="서울 1박 2일 관광 코스",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 서울 주요 관광지 1박 2일 코스")
st.caption("매일 09:00~19:00 · 관광지 10곳 · 식사 장소와 호텔 링크 포함")

st.info(
    "동선은 서울 중심부와 동남·서북권을 날짜별로 묶은 추천 예시입니다. "
    "실제 이동 시간은 교통·대기 상황에 따라 달라질 수 있어요."
)


# Google Maps 검색 링크 생성
def map_link(place: str) -> str:
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(place + ", Seoul, South Korea")
    )


# 관광지 데이터
spots = [
    {
        "no": 1, "day": "1일차",
        "name": "경복궁",
        "lat": 37.5796, "lon": 126.9770,
        "desc": "조선 왕궁과 근정전, 경회루 관람"
    },
    {
        "no": 2, "day": "1일차",
        "name": "북촌한옥마을",
        "lat": 37.5826, "lon": 126.9830,
        "desc": "전통 한옥 골목 산책"
    },
    {
        "no": 3, "day": "1일차",
        "name": "동대문디자인플라자(DDP)",
        "lat": 37.5671, "lon": 127.0095,
        "desc": "건축물 외관과 디자인 전시 공간"
    },
    {
        "no": 4, "day": "1일차",
        "name": "광장시장",
        "lat": 37.5700, "lon": 127.0005,
        "desc": "전통시장 구경과 간식"
    },
    {
        "no": 5, "day": "1일차",
        "name": "명동거리",
        "lat": 37.5636, "lon": 126.9869,
        "desc": "쇼핑 거리와 도심 분위기"
    },
    {
        "no": 6, "day": "1일차",
        "name": "N서울타워",
        "lat": 37.5512, "lon": 126.9882,
        "desc": "남산 전망 감상"
    },
    {
        "no": 7, "day": "2일차",
        "name": "서울숲",
        "lat": 37.5444, "lon": 127.0374,
        "desc": "도심 공원 산책"
    },
    {
        "no": 8, "day": "2일차",
        "name": "코엑스·별마당도서관",
        "lat": 37.5129, "lon": 127.0591,
        "desc": "실내 복합문화공간과 별마당도서관"
    },
    {
        "no": 9, "day": "2일차",
        "name": "강남역 일대",
        "lat": 37.4979, "lon": 127.0276,
        "desc": "강남 대표 상권과 거리 풍경"
    },
    {
        "no": 10, "day": "2일차",
        "name": "홍대 걷고싶은거리",
        "lat": 37.5563, "lon": 126.9236,
        "desc": "거리 공연·상점·청년 문화"
    },
]


# 식당 데이터
food = [
    {
        "name": "애즈라이크(서촌)",
        "lat": 37.5780, "lon": 126.9724,
        "kind": "아침",
        "menu": "브런치·샌드위치·커피",
        "day": "1일차"
    },
    {
        "name": "인사도담",
        "lat": 37.5740, "lon": 126.9852,
        "kind": "점심",
        "menu": "한식·불고기 등",
        "day": "1일차"
    },
    {
        "name": "예지식당(명동)",
        "lat": 37.5642, "lon": 126.9851,
        "kind": "저녁",
        "menu": "한식 백반·만두 등",
        "day": "1일차"
    },
    {
        "name": "어니언 성수",
        "lat": 37.5447, "lon": 127.0560,
        "kind": "아침",
        "menu": "베이커리·커피",
        "day": "2일차"
    },
    {
        "name": "멘쇼쿠 코엑스점",
        "lat": 37.5099, "lon": 127.0600,
        "kind": "점심",
        "menu": "일식 정식·라멘",
        "day": "2일차"
    },
    {
        "name": "육지 홍대",
        "lat": 37.5516, "lon": 126.9228,
        "kind": "저녁",
        "menu": "돼지고기 구이",
        "day": "2일차"
    },
]


# 호텔 데이터
hotels = [
    {
        "name": "서머셋 팰리스 서울",
        "area": "종로·안국",
        "note": "궁궐·북촌·인사동 중심 일정에 편리한 레지던스형 숙소",
        "lat": 37.5758, "lon": 126.9815
    },
    {
        "name": "프레이저 플레이스 센트럴 서울",
        "area": "시청·서대문",
        "note": "객실 유형이 다양한 레지던스형 숙소",
        "lat": 37.5627, "lon": 126.9687
    },
    {
        "name": "UH 스위트 센트럴 서울",
        "area": "시청·무교동",
        "note": "도심 관광지와 명동 접근성을 고려할 만한 숙소",
        "lat": 37.5670, "lon": 126.9802
    },
]


# 날짜별 관광 동선
day1 = [
    (s["lat"], s["lon"])
    for s in spots if s["day"] == "1일차"
]

day2 = [
    (s["lat"], s["lon"])
    for s in spots if s["day"] == "2일차"
]


# --------------------------------------------------
# 1. 전체 지도
# --------------------------------------------------

st.subheader("1. 서울 관광·식사·호텔 전체 지도")

map_obj = folium.Map(
    location=[37.557, 126.995],
    zoom_start=12,
    control_scale=True,
    tiles="OpenStreetMap"
)


# 관광지 마커
for s in spots:
    color = "blue" if s["day"] == "1일차" else "purple"

    folium.Marker(
        [s["lat"], s["lon"]],
        tooltip=f"{s['no']}. {s['name']} ({s['day']})",
        popup=(
            f"<b>{s['no']}. {s['name']}</b><br>"
            f"{s['desc']}<br>"
            f"<a href='{map_link(s['name'])}' target='_blank'>"
            "지도에서 자세히 보기</a>"
        ),
        icon=folium.Icon(
            color=color,
            icon="camera",
            prefix="fa"
        ),
    ).add_to(map_obj)


# 날짜별 관광 동선
folium.PolyLine(
    day1,
    color="#2471A3",
    weight=4,
    opacity=0.8,
    tooltip="1일차 관광 동선"
).add_to(map_obj)

folium.PolyLine(
    day2,
    color="#8E44AD",
    weight=4,
    opacity=0.8,
    tooltip="2일차 관광 동선"
).add_to(map_obj)


# 식당 마커
for f in food:
    folium.Marker(
        [f["lat"], f["lon"]],
        tooltip=f"식당: {f['name']} ({f['day']} {f['kind']})",
        popup=(
            f"<b>{f['name']}</b><br>"
            f"{f['day']} {f['kind']}<br>"
            f"{f['menu']}<br>"
            f"<a href='{map_link(f['name'])}' target='_blank'>"
            "식당 지도·정보</a>"
        ),
        icon=folium.Icon(
            color="orange",
            icon="cutlery",
            prefix="fa"
        ),
    ).add_to(map_obj)


# 호텔 마커
for h in hotels:
    folium.Marker(
        [h["lat"], h["lon"]],
        tooltip=f"호텔: {h['name']}",
        popup=(
            f"<b>{h['name']}</b><br>"
            f"{h['area']}<br>"
            f"{h['note']}<br>"
            f"<a href='{map_link(h['name'])}' target='_blank'>"
            "호텔 위치·정보</a>"
        ),
        icon=folium.Icon(
            color="green",
            icon="bed",
            prefix="fa"
        ),
    ).add_to(map_obj)


folium.LayerControl().add_to(map_obj)

st_folium(
    map_obj,
    height=590,
    use_container_width=True
)

st.caption(
    "지도 범례: 파란색 관광지=1일차 / 보라색 관광지=2일차 / "
    "주황색=식당 / 초록색=호텔. "
    "선은 관광지 사이의 개략적 연결선이며 실제 대중교통 경로가 아닙니다."
)


# --------------------------------------------------
# 2. 1일차 일정표
# --------------------------------------------------

day1_rows = [
    [
        "09:00–09:35", "아침", "애즈라이크(서촌)",
        "브런치와 커피로 가볍게 시작",
        "경복궁역 주변 도보",
        map_link("애즈라이크 서촌")
    ],
    [
        "09:40–11:10", "관광 1", "경복궁",
        "근정전·경회루 등 관람",
        "도보", map_link("경복궁")
    ],
    [
        "11:20–12:05", "관광 2", "북촌한옥마을",
        "한옥 골목 산책",
        "도보", map_link("북촌한옥마을")
    ],
    [
        "12:15–13:10", "점심", "인사도담",
        "불고기 등 한식 메뉴",
        "도보·대중교통", map_link("인사도담")
    ],
    [
        "13:40–14:35", "관광 3",
        "동대문디자인플라자(DDP)",
        "건축물과 전시 공간 둘러보기",
        "지하철·도보", map_link("동대문디자인플라자")
    ],
    [
        "14:50–15:50", "관광 4", "광장시장",
        "시장 구경과 간식",
        "도보", map_link("광장시장")
    ],
    [
        "16:10–17:00", "관광 5", "명동거리",
        "쇼핑 거리 산책",
        "지하철·도보", map_link("명동거리")
    ],
    [
        "17:00–17:45", "저녁", "예지식당(명동)",
        "한식 백반 등 간단한 저녁",
        "도보", map_link("예지식당 명동")
    ],
    [
        "18:00–19:00", "관광 6", "N서울타워",
        "남산 전망 감상 후 일정 종료",
        "케이블카·버스 등", map_link("N서울타워")
    ],
]


# --------------------------------------------------
# 3. 2일차 일정표
# --------------------------------------------------

day2_rows = [
    [
        "09:00–09:40", "아침", "어니언 성수",
        "베이커리와 커피",
        "성수역 주변 도보", map_link("어니언 성수")
    ],
    [
        "09:45–11:15", "관광 7", "서울숲",
        "공원 산책과 휴식",
        "도보", map_link("서울숲")
    ],
    [
        "11:15–12:20", "이동·자유시간",
        "성수에서 코엑스로 이동",
        "이동 중 카페·상점은 여유에 따라 선택",
        "지하철·도보", map_link("서울숲역에서 코엑스")
    ],
    [
        "12:20–13:15", "점심", "멘쇼쿠 코엑스점",
        "일식 정식·라멘",
        "코엑스 내 도보", map_link("멘쇼쿠 코엑스점")
    ],
    [
        "13:20–14:35", "관광 8",
        "코엑스·별마당도서관",
        "실내 복합문화공간과 도서관",
        "도보", map_link("별마당도서관")
    ],
    [
        "14:55–15:55", "관광 9", "강남역 일대",
        "대표 상권과 거리 구경",
        "지하철·도보", map_link("강남역")
    ],
    [
        "15:55–17:00", "이동·자유시간",
        "강남에서 홍대로 이동",
        "교통 상황에 따라 여유시간 조정",
        "지하철", map_link("홍대입구역")
    ],
    [
        "17:00–18:00", "관광 10",
        "홍대 걷고싶은거리",
        "거리 공연과 상점 구경",
        "도보", map_link("홍대 걷고싶은거리")
    ],
    [
        "18:00–19:00", "저녁", "육지 홍대",
        "직원이 구워주는 돼지고기 구이",
        "도보", map_link("육지 홍대")
    ],
]


columns = [
    "시간", "구분", "장소",
    "일정", "이동", "지도 링크"
]


# --------------------------------------------------
# 4. 일정표 화면 출력
# --------------------------------------------------

st.subheader("2. 1일차 일정표 | 고궁·한옥·도심·남산")

st.dataframe(
    pd.DataFrame(day1_rows, columns=columns),
    hide_index=True,
    use_container_width=True,
    column_config={
        "지도 링크": st.column_config.LinkColumn(
            "지도 링크",
            display_text="지도 열기"
        )
    }
)


st.subheader("3. 2일차 일정표 | 공원·코엑스·강남·홍대")

st.dataframe(
    pd.DataFrame(day2_rows, columns=columns),
    hide_index=True,
    use_container_width=True,
    column_config={
        "지도 링크": st.column_config.LinkColumn(
            "지도 링크",
            display_text="지도 열기"
        )
    }
)


# --------------------------------------------------
# 5. 식당 추천
# --------------------------------------------------

st.subheader("4. 동선에 맞춘 식당 추천")

meal_rows = [
    [
        "1일차 아침", "애즈라이크(서촌)",
        "브런치·샌드위치·커피",
        "경복궁 방문 전 가볍게 먹기 좋은 서촌 권역",
        map_link("애즈라이크 서촌")
    ],
    [
        "1일차 점심", "인사도담",
        "한식·불고기 등",
        "북촌에서 인사동 방향으로 이동하며 들르기 편한 위치",
        map_link("인사도담")
    ],
    [
        "1일차 저녁", "예지식당(명동)",
        "한식 백반·만두 등",
        "명동 산책 후 남산으로 이동하기 전 식사",
        map_link("예지식당 명동")
    ],
    [
        "2일차 아침", "어니언 성수",
        "베이커리·커피",
        "서울숲 산책 전 성수에서 아침",
        map_link("어니언 성수")
    ],
    [
        "2일차 점심", "멘쇼쿠 코엑스점",
        "일식 정식·라멘",
        "별마당도서관 관람 전 코엑스 안에서 식사",
        map_link("멘쇼쿠 코엑스점")
    ],
    [
        "2일차 저녁", "육지 홍대",
        "돼지고기 구이",
        "홍대 거리 구경 후 저녁 식사",
        map_link("육지 홍대")
    ],
]


st.dataframe(
    pd.DataFrame(
        meal_rows,
        columns=[
            "식사", "식당", "추천 메뉴",
            "동선상 추천 이유", "링크"
        ]
    ),
    hide_index=True,
    use_container_width=True,
    column_config={
        "링크": st.column_config.LinkColumn(
            "식당 위치·정보",
            display_text="지도에서 보기"
        )
    }
)

st.caption(
    "식당 영업시간·휴무·대기시간은 방문일에 다시 확인하세요. "
    "메뉴와 가격은 매장 사정에 따라 바뀔 수 있습니다."
)


# --------------------------------------------------
# 6. 호텔 추천
# --------------------------------------------------

st.subheader("5. 숙소 추천")

hotel_rows = [
    [
        h["name"],
        h["area"],
        h["note"],
        map_link(h["name"])
    ]
    for h in hotels
]

st.dataframe(
    pd.DataFrame(
        hotel_rows,
        columns=["호텔", "권역", "추천 이유", "링크"]
    ),
    hide_index=True,
    use_container_width=True,
    column_config={
        "링크": st.column_config.LinkColumn(
            "호텔 위치·정보",
            display_text="호텔 정보 보기"
        )
    }
)


for h in hotels:
    st.markdown(
        f"- **{h['name']}** — {h['area']} · "
        f"[지도·연락처·예약 정보 확인]({map_link(h['name'])})"
    )


st.warning(
    "호텔 요금·객실·예약 가능 여부는 날짜와 인원에 따라 달라집니다. "
    "보호자 또는 예약 담당자와 숙박 조건을 확인하고 예약하세요."
)

st.markdown("---")

st.caption(
    "참고: 경복궁은 화요일 휴궁 등 관광지별 휴무·운영시간이 달라질 수 있습니다. "
    "북촌은 주민 거주지역이므로 지정된 관람 구역과 안내 표지를 지켜 주세요. "
    "일정은 이동·대기 시간을 고려한 추천안이며, 현장 상황에 맞춰 조정하세요."
)
