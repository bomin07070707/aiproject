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
    page_title="세계 국가별 MBTI 분석",
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
    '<div class="main-title">🌍 세계 국가별 MBTI 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '국가별 MBTI 16가지 성격 유형 분포를 분석합니다.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# 3. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "countriesMBTI_16types.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "countriesMBTI_16types.csv 파일을 찾을 수 없습니다."
        )

    # CSV 인코딩 자동 대응
    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

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
            f"다음 MBTI 컬럼이 없습니다: {missing}"
        )

    for col in mbti_types:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(
        subset=["Country"] + mbti_types
    )

    return data, mbti_types


try:
    df, mbti_types = load_data()

except Exception as error:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()

# ==========================================
# 4. 국가 선택
# ==========================================
st.subheader("🌐 분석할 국가 선택")

countries = sorted(
    df["Country"].unique().tolist()
)

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "국가를 선택하세요.",
    countries,
    index=default_index
)

# ==========================================
# 5. 선택 국가 데이터 분석
# ==========================================
country_data = df[
    df["Country"] == selected_country
].iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [
        country_data[mbti] * 100
        for mbti in mbti_types
    ]
})

# 비율이 높은 순서대로 정렬
chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# ==========================================
# 6. 그래프 색상 설정
# ==========================================

# 1위는 빨간색
first_color = "#E53935"

# 2~16위는 파란색 그라데이션
blue_gradient = pc.sample_colorscale(
    "Blues",
    np.linspace(0.85, 0.20, 15)
)

colors = [first_color] + blue_gradient

# ==========================================
# 7. 핵심 분석 결과
# ==========================================
first_mbti = chart_data.iloc[0]["MBTI"]
first_rate = chart_data.iloc[0]["비율"]

last_mbti = chart_data.iloc[-1]["MBTI"]
last_rate = chart_data.iloc[-1]["비율"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택 국가",
    selected_country
)

col2.metric(
    "1위 MBTI",
    first_mbti
)

col3.metric(
    "1위 비율",
    f"{first_rate:.2f}%"
)

# ==========================================
# 8. MBTI 막대그래프
# ==========================================
st.divider()

st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_data["MBTI"],
        y=chart_data["비율"],

        marker=dict(
            color=colors,
            line=dict(width=0)
        ),

        text=[
            f"{value:.2f}%"
            for value in chart_data["비율"]
        ],

        textposition="outside",

        textfont=dict(
            size=12,
            color="#333333"
        ),

        hovertemplate=(
            "<b>MBTI: %{x}</b><br>"
            "비율: %{y:.2f}%"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title=dict(
        text=f"{selected_country} MBTI 16가지 유형별 분포",
        x=0.5,
        xanchor="center",
        font=dict(size=22)
    ),

    xaxis=dict(
        title="MBTI 유형",
        tickfont=dict(size=12)
    ),

    yaxis=dict(
        title="비율 (%)",
        rangemode="tozero"
    ),

    height=600,

    plot_bgcolor="white",
    paper_bgcolor="white",

    showlegend=False,

    margin=dict(
        l=50,
        r=40,
        t=100,
        b=70
    )
)

fig.update_xaxes(
    showgrid=False
)

fig.update_yaxes(
    gridcolor="#EAEAEA"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 9. MBTI 순위표
# ==========================================
st.divider()

st.subheader("🏆 MBTI 순위표")

ranking = chart_data.copy()

ranking.insert(
    0,
    "순위",
    range(1, len(ranking) + 1)
)

ranking["비율"] = ranking["비율"].map(
    lambda value: f"{value:.2f}%"
)

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 10. 데이터 안내
# ==========================================
st.divider()

st.caption(
    "데이터 출처: countriesMBTI_16types.csv"
)

st.caption(
    "※ 비율은 원본 데이터에 100을 곱하여 표시합니다. "
    "원본 데이터의 국가별 비율 합계는 정확히 100%가 아닐 수 있습니다."
)

st.success(
    f"{selected_country}의 분석이 완료되었습니다."
)
