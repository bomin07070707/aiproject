
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="지역별 평균소득월액 분석",
    page_icon="📈",
    layout="wide"
)

st.title("📈 지역별 평균소득월액 분석")
st.caption("국민연금공단 · 2025년 12월 31일 기준")

# CSV 파일 경로
CSV_FILE = Path(__file__).parent / "국민연금공단_자격 시구신고 평균소득월액_20251231.csv"


# 데이터 불러오기
@st.cache_data
def load_data():

    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            data = pd.read_csv(
                CSV_FILE,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    required_columns = [
        "기준년월",
        "시군구",
        "평균소득월액"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"필요한 열이 없습니다: {missing}"
        )

    data = data[required_columns].copy()

    data["시군구"] = (
        data["시군구"].astype(str).str.strip()
    )

    data["평균소득월액"] = pd.to_numeric(
        data["평균소득월액"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["시군구", "평균소득월액"]
    )

    data = data.sort_values(
        "시군구"
    ).reset_index(drop=True)

    return data


# 데이터 로딩 오류 처리
try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 CSV 파일을 같은 폴더에 넣어 주세요."
    )
    st.stop()

except Exception as error:
    st.error(f"데이터 오류: {error}")
    st.stop()


# --------------------------------
# 1. 지역 검색
# --------------------------------

st.subheader("🔎 지역 검색")

region_input = st.text_input(
    "분석할 지역명을 입력하세요.",
    placeholder="예: 서울특별시종로구 또는 해운대구"
)

if region_input.strip():

    matched = df[
        df["시군구"].str.contains(
            region_input.strip(),
            case=False,
            na=False
        )
    ]

else:
    matched = df.iloc[0:0]


if region_input.strip() and matched.empty:

    st.warning(
        "일치하는 지역이 없습니다. 지역명을 다시 입력해 주세요."
    )
    st.stop()


if not matched.empty:

    selected_region = st.selectbox(
        "검색 결과에서 지역을 선택하세요.",
        matched["시군구"].tolist()
    )

    selected_value = float(
        df.loc[
            df["시군구"] == selected_region,
            "평균소득월액"
        ].iloc[0]
    )

    national_average = df[
        "평균소득월액"
    ].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "선택 지역",
        selected_region
    )

    col2.metric(
        "평균소득월액",
        f"{selected_value:,.0f}원"
    )

    col3.metric(
        "전체 지역 평균",
        f"{national_average:,.0f}원"
    )

    difference = selected_value - national_average

    if difference >= 0:
        st.success(
            f"전체 평균보다 {difference:,.0f}원 높습니다."
        )
    else:
        st.info(
            f"전체 평균보다 {abs(difference):,.0f}원 낮습니다."
        )

else:

    selected_region = None

    st.info(
        "지역명을 입력하면 해당 지역의 소득 정보를 확인할 수 있습니다."
    )


# --------------------------------
# 2. 선형회귀 알고리즘
# --------------------------------

chart_df = df.copy()

# 가나다순 지역 순번을 X값으로 사용
chart_df["지역순번"] = range(len(chart_df))

X = chart_df[["지역순번"]]

y = chart_df["평균소득월액"]

# 선형회귀 모델 생성
model = LinearRegression()

# 모델 학습
model.fit(X, y)

# 추세선 예측
chart_df["회귀추세선"] = model.predict(X)


# --------------------------------
# 3. 선그래프
# --------------------------------

st.divider()

st.subheader("📊 시군구별 평균소득월액 선그래프")

st.write(
    "가나다순으로 정렬한 지역별 평균소득월액입니다."
)

fig = go.Figure()

# 실제 평균소득월액
fig.add_trace(
    go.Scatter(
        x=chart_df["시군구"],
        y=chart_df["평균소득월액"],
        mode="lines+markers",
        name="평균소득월액",
        line=dict(width=2),
        marker=dict(size=5)
    )
)

# 선형회귀 추세선
fig.add_trace(
    go.Scatter(
        x=chart_df["시군구"],
        y=chart_df["회귀추세선"],
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            width=3,
            dash="dash"
        )
    )
)

# 검색 지역 강조
if selected_region:

    selected_row = chart_df[
        chart_df["시군구"] == selected_region
    ]

    fig.add_trace(
        go.Scatter(
            x=selected_row["시군구"],
            y=selected_row["평균소득월액"],
            mode="markers",
            name="검색한 지역",
            marker=dict(
                size=15,
                symbol="star"
            )
        )
    )


fig.update_layout(
    xaxis_title="시군구 (가나다순)",
    yaxis_title="평균소득월액 (원)",
    hovermode="x unified",
    legend_title="그래프 항목",
    height=650,
    margin=dict(
        l=30,
        r=30,
        t=40,
        b=150
    )
)

fig.update_xaxes(
    tickangle=-70,
    tickfont=dict(size=9)
)

fig.update_yaxes(
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "주의: 회귀 추세선의 X축은 가나다순 지역 순번입니다. "
    "시간에 따른 소득 변화나 미래 예측을 의미하지 않습니다."
)


# --------------------------------
# 4. 선형회귀 알고리즘 설명
# --------------------------------

st.divider()

st.subheader("📘 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 입력값(X)과 결과값(Y) 사이의 관계를
직선으로 나타내는 머신러닝 알고리즘입니다.

데이터의 전체적인 경향을 가장 잘 설명하는
직선을 찾아내는 것이 핵심입니다.
""")

st.markdown("### ① 작동 원리")

st.markdown("""
1. **데이터 입력:** X값과 Y값을 준비합니다.
2. **직선 만들기:** 데이터의 경향을 설명하는 직선을 찾습니다.
3. **오차 계산:** 실제값과 예측값의 차이를 계산합니다.
4. **최적의 직선 찾기:** 오차 제곱의 합이 가장 작아지도록 기울기와 절편을 결정합니다.
5. **결과 활용:** 만들어진 직선으로 데이터의 관계를 설명하거나 새로운 값을 예측합니다.
""")

st.markdown("### ② 선형회귀 기본 수식")

st.latex(r"\hat{y} = b_0 + b_1x")

st.write("""
- x : 입력값
- ŷ : 예측값
- b₀ : 직선의 절편
- b₁ : 직선의 기울기
""")

st.markdown("### ③ 이번 데이터에서의 활용과 한계")

st.warning("""
현재 데이터는 2025년 12월 한 시점의 지역별 평균소득월액입니다.

따라서 특정 지역의 과거와 미래 소득 변화를
학습할 수 있는 시간 데이터가 아닙니다.

현재 그래프의 회귀 추세선은 가나다순 지역 순번에 따른
참고용 추세선입니다.

미래의 소득을 예측하려면 여러 연도와 월의
평균소득월액 데이터가 필요합니다.
""")


# --------------------------------
# 5. 데이터 확인
# --------------------------------

st.divider()

st.subheader("📋 데이터 미리보기")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"분석에 사용한 지역 수: {len(df)}개"
)

