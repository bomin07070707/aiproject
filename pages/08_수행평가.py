
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="서울 자치구 평균소득 분석",
    page_icon="📊",
    layout="wide"
)

st.title("🏙️ 서울 자치구별 평균소득 분석")
st.markdown(
    "국민연금 데이터를 활용해 서울 25개 자치구의 "
    "평균소득월액을 비교하고 머신러닝으로 분석합니다."
)

# =========================
# CSV 경로
# Python 파일은 pages 폴더
# CSV 파일은 상위 폴더
# =========================
CSV_FILE = (
    Path(__file__).resolve().parent.parent
    / "국민연금공단_자격 시구신고 평균소득월액_20251231.csv"
)

# =========================
# 서울 자치구 목록
# =========================
SEOUL_GU = [
    "종로구", "중구", "용산구", "성동구", "광진구",
    "동대문구", "중랑구", "성북구", "강북구", "도봉구",
    "노원구", "은평구", "서대문구", "마포구", "양천구",
    "강서구", "구로구", "금천구", "영등포구", "동작구",
    "관악구", "서초구", "강남구", "송파구", "강동구"
]

# =========================
# 데이터 불러오기
# =========================
@st.cache_data
def load_data():

    encodings = ["cp949", "utf-8-sig", "euc-kr"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                CSV_FILE,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 읽을 수 없습니다.")

try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "CSV 파일을 Python 파일이 있는 pages 폴더의 "
        "상위 폴더에 넣어주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

# =========================
# 데이터 확인
# =========================
required_columns = ["시군구", "평균소득월액"]

if not all(col in df.columns for col in required_columns):
    st.error("필요한 컬럼이 CSV에 없습니다.")
    st.write("현재 컬럼:", df.columns.tolist())
    st.stop()

# =========================
# 데이터 정리
# =========================
df["시군구"] = (
    df["시군구"]
    .astype(str)
    .str.strip()
)

df["평균소득월액"] = (
    df["평균소득월액"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("원", "", regex=False)
    .str.strip()
)

df["평균소득월액"] = pd.to_numeric(
    df["평균소득월액"],
    errors="coerce"
)

df = df.dropna(
    subset=["시군구", "평균소득월액"]
)

# =========================
# 서울 25개 자치구 필터링
# =========================
def find_seoul_gu(region_name):

    for gu in SEOUL_GU:
        if gu in region_name:
            return gu

    return None

df["자치구"] = df["시군구"].apply(find_seoul_gu)

df = df.dropna(subset=["자치구"])

# 자치구별 평균값 계산
df = (
    df.groupby("자치구", as_index=False)
    ["평균소득월액"]
    .mean()
)

# 서울 25개 구 순서와 무관하게 데이터만 존재하는 구 표시
df = df.sort_values(
    by="평균소득월액",
    ascending=False
).reset_index(drop=True)

if df.empty:
    st.error(
        "서울 자치구 데이터를 찾지 못했습니다. "
        "CSV의 시군구 이름을 확인해주세요."
    )
    st.stop()

# =========================
# 서울 평균 계산
# =========================
seoul_mean = df["평균소득월액"].mean()

# =========================
# 지역 검색
# =========================
st.subheader("🔎 서울 자치구 검색")

search_text = st.text_input(
    "자치구 이름을 입력하세요.",
    placeholder="예: 강남구, 송파구, 마포구"
)

if search_text:
    search_df = df[
        df["자치구"].str.contains(
            search_text,
            case=False,
            na=False
        )
    ]
else:
    search_df = df.copy()

if search_df.empty:
    st.warning("검색 결과가 없습니다.")
    st.stop()

selected_gu = st.selectbox(
    "분석할 자치구 선택",
    search_df["자치구"].tolist()
)

# =========================
# 선택 지역 분석
# =========================
selected_income = df.loc[
    df["자치구"] == selected_gu,
    "평균소득월액"
].iloc[0]

difference = selected_income - seoul_mean

# =========================
# 순위 계산
# =========================
rank_df = df.sort_values(
    by="평균소득월액",
    ascending=False
).reset_index(drop=True)

rank_df["순위"] = rank_df.index + 1

selected_rank = rank_df.loc[
    rank_df["자치구"] == selected_gu,
    "순위"
].iloc[0]

# =========================
# 지표 표시
# =========================
st.subheader("💰 서울 자치구 소득 현황")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "선택 자치구",
    selected_gu
)

col2.metric(
    "평균소득월액",
    f"{selected_income:,.0f}원"
)

col3.metric(
    "서울 자치구 평균",
    f"{seoul_mean:,.0f}원"
)

col4.metric(
    "소득 순위",
    f"{int(selected_rank)}위 / {len(df)}개 구"
)

st.metric(
    "서울 평균 대비 차이",
    f"{difference:,.0f}원"
)

# =========================
# 막대그래프
# =========================
st.subheader("📊 서울 자치구별 평균소득월액")

graph_df = df.sort_values(
    by="평균소득월액",
    ascending=False
).reset_index(drop=True)

colors = [
    "#FF4B4B" if gu == selected_gu else "#4A90E2"
    for gu in graph_df["자치구"]
]

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=graph_df["자치구"],
        y=graph_df["평균소득월액"],
        marker_color=colors,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "평균소득월액: %{y:,.0f}원"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title="서울 자치구별 평균소득월액 (높은 순)",
    height=650,
    xaxis=dict(
        title="자치구",
        tickangle=-45
    ),
    yaxis=dict(
        title="평균소득월액 (원)",
        tickformat=",",
        gridcolor="lightgray"
    ),
    margin=dict(
        l=60,
        r=30,
        t=80,
        b=100
    ),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# 머신러닝 알고리즘 선택
# =========================
st.markdown("---")

st.subheader("🤖 머신러닝 알고리즘 비교")

algorithm = st.selectbox(
    "분석 알고리즘을 선택하세요.",
    [
        "선형회귀 (Linear Regression)",
        "랜덤포레스트 (Random Forest)"
    ]
)

# =========================
# 머신러닝 데이터 준비
# =========================
model_df = graph_df.copy()

# 소득 순위 부여
model_df["순위"] = range(
    1,
    len(model_df) + 1
)

X = model_df[["순위"]]

y = model_df["평균소득월액"]

# =========================
# 모델 선택 및 학습
# =========================
if algorithm == "선형회귀 (Linear Regression)":

    model = LinearRegression()

    model.fit(X, y)

    predictions = model.predict(X)

    model_name = "선형회귀"

else:

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=3,
        random_state=42
    )

    model.fit(X, y)

    predictions = model.predict(X)

    model_name = "랜덤포레스트"

# =========================
# 모델 결과 그래프
# =========================
st.subheader(f"📈 {model_name} 분석 결과")

model_fig = go.Figure()

# 실제 데이터 막대
model_fig.add_trace(
    go.Bar(
        x=model_df["자치구"],
        y=model_df["평균소득월액"],
        name="실제 평균소득",
        marker_color=[
            "#FF4B4B" if gu == selected_gu else "#4A90E2"
            for gu in model_df["자치구"]
        ],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "실제 소득: %{y:,.0f}원"
            "<extra></extra>"
        )
    )
)

# 모델 예측 선
model_fig.add_trace(
    go.Scatter(
        x=model_df["자치구"],
        y=predictions,
        name="모델 예측값",
        mode="lines+markers",
        line=dict(
            width=3,
            color="#2ECC71"
        ),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "예측값: %{y:,.0f}원"
            "<extra></extra>"
        )
    )
)

model_fig.update_layout(
    title=f"서울 자치구 소득과 {model_name} 결과",
    height=650,
    xaxis=dict(
        title="자치구",
        tickangle=-45
    ),
    yaxis=dict(
        title="평균소득월액 (원)",
        tickformat=",",
        gridcolor="lightgray"
    ),
    legend=dict(
        orientation="h",
        y=-0.25
    ),
    margin=dict(
        l=60,
        r=30,
        t=80,
        b=120
    )
)

st.plotly_chart(
    model_fig,
    use_container_width=True
)

# =========================
# 모델 성능 확인
# =========================
r2 = model.score(X, y)

st.metric(
    "모델 결정계수 (R²)",
    f"{r2:.4f}"
)

# =========================
# 알고리즘 설명
# =========================
st.markdown("---")

if algorithm == "선형회귀 (Linear Regression)":

    st.subheader("📖 선형회귀 알고리즘 설명")

    st.markdown("""
    ### 1. 선형회귀란?

    선형회귀는 데이터의 관계를 직선으로 표현하여
    값의 패턴을 분석하는 머신러닝 알고리즘입니다.

    ### 2. 기본 수식

    **y = ax + b**

    - x : 소득 순위
    - y : 모델이 예측한 소득
    - a : 기울기
    - b : 절편

    ### 3. 작동 방식

    1. 서울 자치구의 소득 데이터를 수집합니다.
    2. 소득이 높은 순서대로 순위를 부여합니다.
    3. 순위와 소득 사이의 관계를 분석합니다.
    4. 데이터와 가장 잘 맞는 직선을 계산합니다.

    ### 4. 특징

    - 계산이 빠르고 구조가 단순합니다.
    - 데이터의 전체적인 경향을 직선으로 표현합니다.
    - 복잡한 관계를 표현하는 데 한계가 있습니다.
    """)

    st.write(
        f"**기울기:** {model.coef_[0]:,.2f}"
    )

    st.write(
        f"**절편:** {model.intercept_:,.2f}"
    )

else:

    st.subheader("🌳 랜덤포레스트 알고리즘 설명")

    st.markdown("""
    ### 1. 랜덤포레스트란?

    랜덤포레스트는 여러 개의 의사결정나무를 만들어
    결과를 종합하는 머신러닝 알고리즘입니다.

    ### 2. 작동 방식

    1. 여러 개의 의사결정나무를 생성합니다.
    2. 각 나무가 데이터의 특징을 학습합니다.
    3. 여러 나무가 각각 예측을 수행합니다.
    4. 회귀에서는 여러 나무의 예측값을 평균하여 최종 결과를 계산합니다.

    ### 3. 특징

    - 여러 나무를 결합해 결과를 계산합니다.
    - 직선이 아닌 복잡한 관계도 학습할 수 있습니다.
    - 데이터에 따라 선형회귀와 다른 예측 결과를 보여줍니다.
    - 학습에 사용된 데이터에 지나치게 맞춰질 수도 있습니다.
    """)

    st.write(
        f"**사용한 의사결정나무 개수:** "
        f"{model.n_estimators}개"
    )

    st.write(
        f"**나무의 최대 깊이:** "
        f"{model.max_depth}"
    )

# =========================
# 주의사항
# =========================
st.markdown("---")

st.warning("""
⚠️ **분석 시 주의사항**

이 분석은 자치구를 평균소득 순위로 정렬한 뒤
순위를 입력값으로 사용하여 머신러닝 모델을 학습한 것입니다.

따라서 모델의 예측선은 소득 순위와 소득 간 패턴을
설명하기 위한 시각화입니다.

실제 미래 소득을 예측하는 모델은 아닙니다.
또한 결정계수는 학습 데이터에 대한 값이므로
실제 예측 성능을 의미하지 않습니다.
""")

# =========================
# 데이터 테이블
# =========================
st.markdown("---")

st.subheader("📋 서울 자치구 소득 순위")

display_df = graph_df.copy()

display_df["순위"] = display_df.index + 1

display_df = display_df[
    ["순위", "자치구", "평균소득월액"]
]

display_df["평균소득월액"] = display_df[
    "평균소득월액"
].apply(lambda x: f"{x:,.0f}원")

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True
)
