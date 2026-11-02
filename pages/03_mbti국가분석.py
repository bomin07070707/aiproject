
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
import numpy as np
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="세계 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# ==========================================
# 2. 화면 디자인
# ==========================================
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #2563EB;
    padding: 15px;
}

.sub-title {
    text-align: center;
    color: #777777;
    font-size: 16px;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    background-color: #F0F5FF;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🌍 세계 MBTI 분석 대시보드</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '국가별 MBTI 분포 및 MBTI 유형별 국가 순위 분석'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# 3. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    possible_paths = [
        base_dir / "countriesMBTI_16types.csv",
        base_dir / "data" / "countriesMBTI_16types.csv",
        Path.cwd() / "countriesMBTI_16types.csv",
        Path.cwd() / "data" / "countriesMBTI_16types.csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.is_file():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "countriesMBTI_16types.csv 파일을 찾을 수 없습니다."
        )

    try:
        data = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError:
        data = pd.read_csv(
            file_path,
            encoding="cp949"
        )

    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError("Country 컬럼이 없습니다.")

    mbti_types = [
        "INFJ", "ISFJ", "INTP", "ISFP",
        "ENTP", "INFP", "ENTJ", "ISTP",
        "INTJ", "ESFP", "ESTJ", "ENFP",
        "ESTP", "ISTJ", "ENFJ", "ESFJ"
    ]

    missing = [
        col for col in mbti_types
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"누락된 MBTI 컬럼: {missing}"
        )

    for col in mbti_types:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data["Country"] = (
        data["Country"].astype(str).str.strip()
    )

    data = data.dropna(
        subset=["Country"] + mbti_types
    )

    data = data[
        data["Country"] != ""
    ]

    data = data.drop_duplicates(
        subset=["Country"]
    )

    if data.empty:
        raise ValueError("분석할 데이터가 없습니다.")

    return data, mbti_types


try:
    df, mbti_types = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.info(
        "GitHub 저장소에 app.py와 "
        "countriesMBTI_16types.csv 파일이 있는지 확인하세요."
    )
    st.stop()

# ==========================================
# 4. 공통 데이터
# ==========================================
countries = sorted(
    df["Country"].unique().tolist()
)

st.success(
    f"데이터 불러오기 성공! 전체 {len(countries)}개 국가"
)

# ==========================================
# 5. 분석 모드 선택
# ==========================================
st.divider()

st.header("📊 분석 메뉴")

analysis_mode = st.radio(
    "분석 방법을 선택하세요.",
    [
        "🌐 국가별 MBTI 분석",
        "🏆 MBTI별 국가 순위 분석"
    ],
    horizontal=True
)

# ==========================================
# 6. 공통 그래프 색상 함수
# ==========================================
def make_colors(count):

    if count <= 0:
        return []

    if count == 1:
        return ["#E53935"]

    blue_gradient = pc.sample_colorscale(
        "Blues",
        np.linspace(0.85, 0.20, count - 1)
    )

    return ["#E53935"] + blue_gradient


# ==========================================
# 7. 국가별 MBTI 분석
# ==========================================
if analysis_mode == "🌐 국가별 MBTI 분석":

    st.subheader("🌐 국가를 선택하세요.")

    default_index = (
        countries.index("South Korea")
        if "South Korea" in countries
        else 0
    )

    selected_country = st.selectbox(
        "분석 국가",
        countries,
        index=default_index,
        key="country_select"
    )

    country_data = df[
        df["Country"] == selected_country
    ].iloc[0]

    chart_data = pd.DataFrame({
        "MBTI": mbti_types,
        "비율": [
            country_data[m] * 100
            for m in mbti_types
        ]
    })

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 핵심 결과
    first_mbti = chart_data.iloc[0]["MBTI"]
    first_rate = chart_data.iloc[0]["비율"]

    c1, c2, c3 = st.columns(3)

    c1.metric("선택 국가", selected_country)
    c2.metric("1위 MBTI", first_mbti)
    c3.metric("최고 비율", f"{first_rate:.2f}%")

    # 그래프
    st.divider()

    st.subheader(
        f"📈 {selected_country}의 MBTI 16가지 비율"
    )

    colors = make_colors(len(chart_data))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_data["MBTI"],
            y=chart_data["비율"],
            marker_color=colors,
            text=[
                f"{v:.2f}%"
                for v in chart_data["비율"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=f"{selected_country} MBTI 분포",
        xaxis_title="MBTI 유형",
        yaxis_title="비율 (%)",
        height=600,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=80, b=60)
    )

    fig.update_yaxes(
        rangemode="tozero",
        gridcolor="#EEEEEE"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 순위표
    st.subheader("🏅 MBTI 순위표")

    ranking = chart_data.copy()

    ranking.insert(
        0,
        "순위",
        range(1, len(ranking) + 1)
    )

    ranking["비율"] = ranking["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 8. MBTI별 국가 순위 분석
# ==========================================
else:

    st.subheader("🏆 MBTI 유형을 선택하세요.")

    selected_mbti = st.selectbox(
        "MBTI 유형 선택",
        mbti_types,
        index=mbti_types.index("INFP"),
        key="mbti_select"
    )

    st.markdown(
        f"### 🌍 {selected_mbti} 비율이 높은 국가 순위"
    )

    # 국가별 해당 MBTI 비율 계산
    country_ranking = df[
        ["Country", selected_mbti]
    ].copy()

    country_ranking["비율"] = (
        country_ranking[selected_mbti] * 100
    )

    # 높은 순서대로 정렬
    country_ranking = country_ranking.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 순위 부여
    country_ranking.insert(
        0,
        "순위",
        range(1, len(country_ranking) + 1)
    )

    # 상위 국가 선택
    display_option = st.selectbox(
        "그래프에 표시할 국가 수",
        [
            "상위 10개국",
            "상위 20개국",
            "상위 30개국",
            "상위 50개국",
            "상위 100개국",
            "전체 국가"
        ],
        index=1
    )

    if display_option == "전체 국가":
        display_count = len(country_ranking)
    else:
        display_count = int(
            display_option.split()[1].replace("개국", "")
        )

    display_data = country_ranking.head(
        display_count
    ).copy()

    # 1위 국가 정보
    first_country = country_ranking.iloc[0]["Country"]
    first_rate = country_ranking.iloc[0]["비율"]

    last_country = country_ranking.iloc[-1]["Country"]
    last_rate = country_ranking.iloc[-1]["비율"]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "선택 MBTI",
        selected_mbti
    )

    c2.metric(
        "1위 국가",
        first_country
    )

    c3.metric(
        "1위 비율",
        f"{first_rate:.2f}%"
    )

    # ======================================
    # 국가 순위 그래프
    # ======================================
    st.divider()

    st.subheader(
        f"🥇 {selected_mbti} 국가별 순위 그래프"
    )

    colors = make_colors(len(display_data))

    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x=display_data["비율"],
            y=display_data["Country"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(width=0)
            ),
            text=[
                f"{v:.2f}%"
                for v in display_data["비율"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"MBTI: {selected_mbti}<br>"
                "비율: %{x:.2f}%"
                "<extra></extra>"
            )
        )
    )

    fig2.update_layout(
        title=dict(
            text=f"{selected_mbti} 국가별 비율 순위",
            x=0.5,
            xanchor="center",
            font=dict(size=22)
        ),

        xaxis=dict(
            title="비율 (%)",
            rangemode="tozero",
            showgrid=True,
            gridcolor="#EEEEEE"
        ),

        yaxis=dict(
            title="국가",
            autorange="reversed"
        ),

        height=max(
            600,
            min(2200, len(display_data) * 32)
        ),

        showlegend=False,

        plot_bgcolor="white",
        paper_bgcolor="white",

        margin=dict(
            l=120,
            r=80,
            t=90,
            b=60
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ======================================
    # 국가별 순위표
    # ======================================
    st.divider()

    st.subheader(
        f"📋 {selected_mbti} 국가별 순위표"
    )

    table_data = display_data[
        ["순위", "Country", "비율"]
    ].copy()

    table_data.columns = [
        "순위",
        "국가",
        "비율 (%)"
    ]

    table_data["비율 (%)"] = (
        table_data["비율 (%)"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

    # 전체 국가 순위 다운로드
    download_data = country_ranking.copy()

    download_data.columns = [
        "순위",
        "국가",
        "원본 비율",
        "비율 (%)"
    ]

    csv_data = download_data.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 전체 국가 순위 CSV 다운로드",
        data=csv_data,
        file_name=f"{selected_mbti}_국가별_순위.csv",
        mime="text/csv"
    )

# ==========================================
# 9. 전체 원본 데이터
# ==========================================
st.divider()

with st.expander("📂 전체 국가 원본 데이터 확인"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv_download = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "전체 데이터 다운로드",
        data=csv_download,
        file_name="world_mbti_data.csv",
        mime="text/csv"
    )

# ==========================================
# 10. 하단 안내
# ==========================================
st.divider()

st.caption(
    "자료: countriesMBTI_16types.csv"
)

st.caption(
    "※ 비율은 원본 데이터에 100을 곱하여 표시합니다. "
    "국가별 비율 합계는 정확히 100%가 아닐 수 있습니다."
)

st.success("세계 MBTI 분석이 완료되었습니다.")
