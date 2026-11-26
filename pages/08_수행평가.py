
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="지역별 평균소득 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 지역별 평균소득월액 분석")
st.markdown("국민연금 데이터를 활용하여 지역별 평균소득월액을 비교해 봅니다.")

# =========================
# CSV 파일 경로
# Python 파일은 pages 폴더
# CSV는 상위 폴더에 위치
# =========================
CSV_FILE = (
    Path(__file__).resolve().parent.parent
    / "국민연금공단_자격 시구신고 평균소득월액_20251231.csv"
)

# =========================
# 데이터 불러오기
# =========================
@st.cache_data
def load_data():

    encodings = ["cp949", "utf-8-sig", "euc-kr"]

    for encoding in encodings:
        try:
            df = pd.read_csv(CSV_FILE, encoding=encoding)
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

# =========================
# 데이터 처리
# =========================
try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "CSV 파일은 Python 파일이 있는 pages 폴더의 "
        "상위 폴더에 위치해야 합니다."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 컬럼 확인
required_columns = ["시군구", "평균소득월액"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 필요한 컬럼이 없습니다.")
    st.write("현재 데이터 컬럼:", df.columns.tolist())
    st.stop()

# 데이터 정리
df["시군구"] = df["시군구"].astype(str).str.strip()

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

df = df.dropna(subset=["시군구", "평균소득월액"])

# 지역별 평균값 정리
df = (
    df.groupby("시군구", as_index=False)["평균소득월액"]
    .mean()
)

# =========================
# 전체 평균
# =========================
national_mean = df["평균소득월액"].mean()

# =========================
# 지역 검색
# =========================
st.subheader("🔎 지역 검색")

search_text = st.text_input(
    "지역 이름을 입력하세요.",
    placeholder="예: 강남구, 서울, 부산"
)

# 검색어가 입력되었을 때 필터링
if search_text:
    search_df = df[
        df["시군구"].str.contains(
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

selected_region = st.selectbox(
    "분석할 지역 선택",
    search_df["시군구"].tolist()
)

# =========================
# 선택 지역 데이터
# =========================
selected_data = df[
    df["시군구"] == selected_region
]

selected_income = selected_data[
    "평균소득월액"
].iloc[0]

difference = selected_income - national_mean

# =========================
# 숫자 표시
# =========================
st.subheader("💰 지역 소득 분석")

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택 지역",
    selected_region
)

col2.metric(
    "평균소득월액",
    f"{selected_income:,.0f}원"
)

col3.metric(
    "전체 지역 평균",
    f"{national_mean:,.0f}원"
)

st.metric(
    "전체 평균 대비 차이",
    f"{difference:,.0f}원",
    delta=f"{difference:,.0f}원"
)

# =========================
# 순위 확인
# =========================
rank_df = df.sort_values(
    by="평균소득월액",
    ascending=False
).reset_index(drop=True)

rank_df.index = rank_df.index + 1

selected_rank = (
    rank_df.index[
        rank_df["시구군"] == selected_region
    ]
    if "시구군" in rank_df.columns
    else rank_df.index[
        rank_df["시군구"] == selected_region
    ]
)

st.info(
    f"🏆 {selected_region}의 평균소득월액 순위는 "
    f"{int(selected_rank[0])}위입니다."
)

# =========================
# 막대그래프
# =========================
st.subheader("📊 지역별 평균소득월액 순위")

graph_df = df.sort_values(
    by="평균소득월액",
    ascending=False
).reset_index(drop=True)

# 선택 지역 강조
colors = [
    "#FF4B4B" if region == selected_region else "#4A90E2"
    for region in graph_df["시군구"]
]

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=graph_df["시군구"],
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
    title="지역별 평균소득월액 (높은 순)",
    width=3000,
    height=800,
    xaxis=dict(
        title="지역",
        tickangle=-60,
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        title="평균소득월액 (원)",
        tickformat=",",
        gridcolor="lightgray"
    ),
    margin=dict(
        l=80,
        r=50,
        t=100,
        b=250
    ),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=False
)

# =========================
# 선형회귀 분석
# =========================
st.subheader("🤖 선형회귀 분석")

# 소득 순위에 따라 번호 부여
regression_df = graph_df.copy()

regression_df["순위"] = range(
    1,
    len(regression_df) + 1
)

X = regression_df[["순위"]]

y = regression_df["평균소득월액"]

model = LinearRegression()

model.fit(X, y)

slope = model.coef_[0]

intercept = model.intercept_

# =========================
# 회귀 결과
# =========================
st.write("### 📐 선형회귀 결과")

st.write(
    f"**회귀식:** "
    f"평균소득월액 = {intercept:,.2f} "
    f"+ ({slope:,.2f} × 순위)"
)

st.write(
    f"**기울기:** {slope:,.2f}"
)

st.write(
    f"**절편:** {intercept:,.2f}"
)

st.write(
    f"**R² 결정계수:** {model.score(X, y):.4f}"
)

# =========================
# 알고리즘 설명
# =========================
st.markdown("---")

st.subheader("📖 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀는 데이터 사이의 관계를 직선 형태의 수식으로 나타내는
대표적인 머신러닝 알고리즘입니다.

### 1️⃣ 선형회귀의 기본 원리

선형회귀는 데이터의 관계를 다음과 같은 수식으로 표현합니다.

**y = ax + b**

- **x** : 입력값 (여기서는 소득 순위)
- **y** : 예측값
- **a** : 기울기
- **b** : 절편

### 2️⃣ 어떻게 작동할까요?

1. 각 지역의 소득 데이터를 수집합니다.
2. 평균소득이 높은 지역부터 순위를 부여합니다.
3. 순위와 소득 사이의 관계를 분석합니다.
4. 데이터와 가장 잘 맞는 직선을 찾습니다.

### 3️⃣ 기울기는 무엇을 의미할까요?

기울기는 순위가 1단계 낮아질 때
평균소득월액이 얼마나 변하는지 나타내는 수치입니다.

### 4️⃣ 결정계수 R²란?

R²는 모델이 데이터의 변화를 얼마나 설명하는지
대략적으로 나타내는 지표입니다.

- 1에 가까울수록 모델이 데이터에 잘 맞습니다.
- 0에 가까울수록 설명력이 낮습니다.

⚠️ **주의사항**

이번 분석은 지역을 평균소득 순위로 정렬한 뒤
순위를 입력값으로 사용한 분석입니다.

따라서 이 회귀분석은 지역 소득 순위의 패턴을
단순히 직선으로 표현한 것이며,
시간에 따른 소득 변화 예측이나 미래 소득 예측을 의미하지 않습니다.
""")

# =========================
# 데이터 확인
# =========================
st.markdown("---")

st.subheader("📋 지역별 평균소득 데이터")

display_df = graph_df.copy()

display_df.index = display_df.index + 1

display_df.index.name = "순위"

display_df["평균소득월액"] = display_df[
    "평균소득월액"
].apply(lambda x: f"{x:,.0f}원")

st.dataframe(
    display_df,
    use_container_width=True
)
