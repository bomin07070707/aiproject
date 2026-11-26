
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="지역별 평균소득월액 분석",
    page_icon="📈",
    layout="wide"
)

st.title("📈 지역별 평균소득월액 분석")
st.write("국민연금공단 자료를 활용한 지역별 소득 분석")


# =====================================
# 2. CSV 파일 경로 설정
# =====================================

# app.py는 pages 폴더
# CSV는 상위 폴더

CSV_FILE = (
    Path(__file__).resolve().parent.parent
    / "국민연금공단_자격 시구신고 평균소득월액_20251231.csv"
)


# =====================================
# 3. 데이터 불러오기
# =====================================

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
        raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

    # 필요한 열 확인
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
            f"CSV 파일에 필요한 열이 없습니다: {missing}"
        )

    # 데이터 정리
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


# =====================================
# 4. 데이터 로딩 오류 처리
# =====================================

try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "CSV 파일이 상위 폴더에 있는지 확인해 주세요."
    )

    st.stop()

except Exception as error:

    st.error(f"데이터 로딩 오류: {error}")

    st.stop()


# =====================================
# 5. 지역 검색 기능
# =====================================

st.subheader("🔎 분석할 지역 검색")

region_input = st.text_input(
    "지역명을 입력하세요.",
    placeholder="예: 서울특별시종로구, 부산광역시해운대구"
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


# 검색 결과가 없을 때
if region_input.strip() and matched.empty:

    st.warning(
        "검색한 지역이 없습니다. "
        "지역명을 다시 확인해 주세요."
    )

    st.stop()


# 검색 결과 선택
if not matched.empty:

    selected_region = st.selectbox(
        "분석할 지역을 선택하세요.",
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

    # 주요 통계 표시
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
            f"전체 지역 평균보다 {difference:,.0f}원 높습니다."
        )

    else:

        st.info(
            f"전체 지역 평균보다 {abs(difference):,.0f}원 낮습니다."
        )

else:

    selected_region = None

    st.info(
        "지역명을 입력하면 해당 지역의 평균소득월액을 확인할 수 있습니다."
    )


# =====================================
# 6. 선형회귀 알고리즘
# =====================================

chart_df = df.copy()

# 가나다순 지역 순번 생성
chart_df["지역순번"] = range(len(chart_df))

# 독립변수 X
X = chart_df[["지역순번"]]

# 종속변수 Y
y = chart_df["평균소득월액"]

# 선형회귀 모델 생성
model = LinearRegression()

# 모델 학습
model.fit(X, y)

# 추세선 계산
chart_df["회귀추세선"] = model.predict(X)


# =====================================
# 7. 선그래프 만들기
# =====================================

st.divider()

st.subheader("📊 시군구별 평균소득월액 선그래프")

st.write(
    "전국 시군구별 평균소득월액과 "
    "선형회귀 추세선을 비교합니다."
)

fig = go.Figure()


# 실제 데이터 선그래프
fig.add_trace(
    go.Scatter(
        x=chart_df["시군구"],
        y=chart_df["평균소득월액"],
        mode="lines+markers",
        name="평균소득월액",
        line=dict(width=2),
        marker=dict(size=5),
        hovertemplate=(
            "%{x}<br>"
            "평균소득월액: %{y:,.0f}원"
            "<extra></extra>"
        )
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
        ),
        hovertemplate=(
            "%{x}<br>"
            "회귀 추세값: %{y:,.0f}원"
            "<extra></extra>"
        )
    )
)


# 사용자가 검색한 지역 강조
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
                size=16,
                symbol="star"
            )
        )
    )


# 그래프 디자인 및 가로폭 확대
fig.update_layout(
    xaxis_title="시군구",
    yaxis_title="평균소득월액 (원)",
    hovermode="x unified",
    legend_title="그래프 항목",
    height=700,
    width=3000,
    margin=dict(
        l=50,
        r=50,
        t=50,
        b=180
    )
)

# 가로축 지역명 표시 간격 조절
fig.update_xaxes(
    tickangle=-60,
    tickfont=dict(size=10),
    tickmode="linear",
    dtick=5
)

fig.update_yaxes(
    tickformat=","
)

# 넓은 그래프 표시
st.plotly_chart(
    fig,
    use_container_width=False
)

st.caption(
    "회귀 추세선은 가나다순 지역 순번을 기준으로 계산한 참고선입니다. "
    "시간에 따른 소득 변화나 미래 예측을 의미하지 않습니다."
)


# =====================================
# 8. 선형회귀 알고리즘 설명
# =====================================

st.divider()

st.subheader("📘 선형회귀 알고리즘 알아보기")

st.write("""
선형회귀(Linear Regression)는 데이터를 분석하여
입력값과 결과값 사이의 관계를 직선으로 표현하는
대표적인 머신러닝 알고리즘입니다.

데이터의 전체적인 경향을 가장 잘 설명하는
직선을 찾아내는 것이 핵심입니다.
""")


# 작동 원리
st.markdown("### ① 선형회귀의 작동 원리")

st.markdown("""
**1단계. 데이터 입력**

분석에 필요한 입력값(X)과 결과값(Y)을 준비합니다.

**2단계. 직선 만들기**

데이터의 전체적인 경향을 나타내는 직선을 찾습니다.

**3단계. 오차 계산**

실제 데이터와 직선이 예측한 값의 차이를 계산합니다.

**4단계. 최적의 직선 찾기**

오차 제곱의 합이 가장 작아지도록
직선의 기울기와 절편을 결정합니다.

**5단계. 결과 활용**

완성된 직선을 이용하여 데이터의 관계를 설명하거나
새로운 값을 예측할 수 있습니다.
""")


# 선형회귀 수식
st.markdown("### ② 선형회귀 기본 수식")

st.latex(
    r"\hat{y} = b_0 + b_1x"
)

st.write("""
- x : 입력값
- ŷ : 예측값
- b₀ : 직선의 절편
- b₁ : 직선의 기울기
""")


# 실제 데이터 적용
st.markdown("### ③ 이번 데이터에서의 활용")

st.info("""
이번 분석에서는 다음과 같이 적용했습니다.

- X값: 가나다순으로 정렬한 지역의 순번
- Y값: 해당 지역의 평균소득월액
- 알고리즘: 선형회귀(Linear Regression)
- 결과: 전체 지역의 소득 분포에 대한 직선형 추세선

따라서 이 추세선은 지역별 소득 수준을
단순하게 비교하기 위한 참고 자료입니다.
""")


# 분석의 한계
st.markdown("### ④ 선형회귀 분석의 주의점")

st.warning("""
현재 데이터는 2025년 12월 한 시점의 자료입니다.

따라서 과거에서 미래로 이어지는 소득 변화는
분석할 수 없습니다.

또한 지역 순번은 실제 거리나 소득에 영향을 주는
의미 있는 수치가 아닙니다.

미래의 평균소득월액을 예측하려면
여러 연도와 월의 데이터가 추가로 필요합니다.
""")


# =====================================
# 9. 데이터 미리보기
# =====================================

st.divider()

st.subheader("📋 전체 데이터 확인")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"전체 분석 지역 수: {len(df)}개"
)

st.success("지역별 평균소득월액 분석이 완료되었습니다!")
