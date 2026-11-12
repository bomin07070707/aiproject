
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="월별 기온 예측 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 미래 예측")
st.markdown(
    "과거 기온 데이터를 분석하고 선형회귀 알고리즘으로 "
    "미래의 평균기온을 예측해 보세요!"
)

# ---------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, encoding="cp949")
    else:
        file_candidates = [
            Path("temperature.csv"),
            Path("temperature (1).csv")
        ]

        file_path = next(
            (p for p in file_candidates if p.exists()),
            None
        )

        if file_path is None:
            raise FileNotFoundError(
                "temperature.csv 파일을 찾을 수 없습니다."
            )

        # 여러 인코딩을 순서대로 시도
        data = None
        for encoding in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
            try:
                data = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if data is None:
            raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

    return data


uploaded_file = st.sidebar.file_uploader(
    "temperature.csv 파일 업로드",
    type=["csv"]
)

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.info(
        "temperature.csv 파일을 app.py와 같은 폴더에 넣거나 "
        "왼쪽 메뉴에서 CSV 파일을 업로드해 주세요."
    )
    st.stop()

# ---------------------------------
# 3. 데이터 전처리
# ---------------------------------
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일에 '일시', '평균기온(℃)' 열이 필요합니다."
    )
    st.stop()

df["날짜"] = pd.to_datetime(
    df["일시"].astype(str).str.strip(),
    format="%b-%y",
    errors="coerce"
)

df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()

# ---------------------------------
# 4. 사용자 입력
# ---------------------------------
st.sidebar.header("🔍 분석 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: month_names[x]
)

# 선택한 월의 데이터만 추출
month_df = df[df["월"] == selected_month].copy()
month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 2개 연도 이상 필요합니다.")
    st.stop()

latest_year = int(month_df["연도"].max())

forecast_year = st.sidebar.number_input(
    "예측할 연도를 입력하세요",
    min_value=latest_year + 1,
    max_value=latest_year + 50,
    value=latest_year + 5,
    step=1
)

forecast_year = int(forecast_year)

# ---------------------------------
# 5. 선형회귀 알고리즘
# ---------------------------------
x = month_df["연도"].values.astype(float)
y = month_df["평균기온(℃)"].values.astype(float)

# 최소제곱법을 이용한 직선 계산
slope, intercept = np.polyfit(x, y, 1)

# 회귀식에 따른 과거 예측값
y_fitted = slope * x + intercept

# 미래 기온 예측
predicted_temp = slope * forecast_year + intercept

# 결정계수 R² 계산
ss_res = np.sum((y - y_fitted) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)

if ss_tot == 0:
    r_squared = 1.0 if ss_res == 0 else 0.0
else:
    r_squared = 1 - (ss_res / ss_tot)

# ---------------------------------
# 6. 예측 결과 표시
# ---------------------------------
st.subheader(
    f"📊 {month_names[selected_month]} 평균기온 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "분석 데이터 개수",
        f"{len(month_df)}개 연도"
    )

with col2:
    st.metric(
        "마지막 관측 연도",
        f"{latest_year}년"
    )

with col3:
    st.metric(
        f"{forecast_year}년 예측 평균기온",
        f"{predicted_temp:.2f} ℃"
    )

st.divider()

# ---------------------------------
# 7. 그래프 만들기
# ---------------------------------
st.subheader("📈 과거 기온과 미래 예측 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 관측 기온
ax.scatter(
    x, y,
    color="royalblue",
    s=65,
    label="실제 평균기온",
    zorder=3
)

# 실제 데이터 연결선
ax.plot(
    x, y,
    color="lightsteelblue",
    linewidth=1.5,
    alpha=0.8
)

# 회귀 추세선
trend_years = np.linspace(
    x.min(), forecast_year, 200
)
trend_temps = slope * trend_years + intercept

historical_mask = trend_years <= latest_year

ax.plot(
    trend_years[historical_mask],
    trend_temps[historical_mask],
    color="red",
    linewidth=2.5,
    label="선형회귀 추세선"
)

# 미래 예측 구간
ax.plot(
    [latest_year, forecast_year],
    [
        slope * latest_year + intercept,
        predicted_temp
    ],
    color="darkorange",
    linestyle="--",
    linewidth=2.5,
    label="미래 예측 구간"
)

# 미래 예측 지점
ax.scatter(
    forecast_year,
    predicted_temp,
    color="darkorange",
    marker="*",
    s=300,
    edgecolors="black",
    linewidths=0.8,
    label="미래 예측 기온",
    zorder=5
)

# 예측값 표시
ax.annotate(
    f"{forecast_year}년\n{predicted_temp:.2f}℃",
    xy=(forecast_year, predicted_temp),
    xytext=(10, 15),
    textcoords="offset points",
    fontsize=11,
    fontweight="bold",
    color="darkorange"
)

# 축과 제목
ax.set_title(
    f"{month_names[selected_month]} 월별 기온 분석",
    fontsize=17,
    fontweight="bold"
)

ax.set_xlabel("연도", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)

ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(loc="best")

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ---------------------------------
# 8. 회귀식과 분석 결과
# ---------------------------------
st.subheader("🧮 선형회귀 계산 결과")

st.latex(
    rf"\hat{{y}} = {slope:.4f}x + ({intercept:.4f})"
)

col1, col2 = st.columns(2)

with col1:
    st.metric("기울기 (Slope)", f"{slope:.4f}")

with col2:
    st.metric("결정계수 (R²)", f"{r_squared:.4f}")

if slope > 0:
    st.success(
        f"분석 결과, {month_names[selected_month]}의 "
        "평균기온은 장기적으로 상승하는 추세입니다."
    )
elif slope < 0:
    st.info(
        f"분석 결과, {month_names[selected_month]}의 "
        "평균기온은 장기적으로 하락하는 추세입니다."
    )
else:
    st.info("분석 결과, 장기적인 기온 변화 추세가 거의 없습니다.")

# ---------------------------------
# 9. 선형회귀 알고리즘 설명
# ---------------------------------
st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown("""
**선형회귀(Linear Regression)**는 과거의 데이터 사이에
가장 잘 맞는 직선을 찾아 미래의 값을 예측하는 머신러닝 알고리즘입니다.

이번 앱에서는 다음과 같이 작동합니다.

1. **데이터 수집:** 선택한 월의 여러 연도 평균기온을 모읍니다.
2. **관계 분석:** 가로축은 연도, 세로축은 평균기온으로 설정합니다.
3. **최적의 직선 찾기:** 실제 기온 데이터와 직선 사이의 오차 제곱합이
   가장 작아지도록 기울기와 절편을 계산합니다.
4. **미래 예측:** 만들어진 직선에 사용자가 입력한 연도를 대입합니다.
5. **결과 확인:** 그래프의 주황색 별표가 예측된 평균기온입니다.

### 그래프 색상 읽는 방법

- 🔵 파란색 점: 실제 관측된 평균기온
- 🔴 빨간색 선: 과거 데이터로 계산한 선형회귀 추세선
- 🟠 주황색 점선: 마지막 관측 연도부터 미래 예측 연도까지의 구간
- ⭐ 주황색 별표: 입력한 연도의 예측 평균기온

### 결정계수(R²)란?

결정계수는 회귀 직선이 실제 데이터의 변화를 얼마나 설명하는지
나타내는 값입니다.

- 1에 가까울수록 데이터의 변화와 직선의 관계가 강합니다.
- 0에 가까울수록 직선으로 설명할 수 있는 변화가 적습니다.

단, 결정계수가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
특히 먼 미래를 예측할수록 실제 기온과 차이가 커질 수 있습니다.
""")

# ---------------------------------
# 10. 실제 데이터 확인
# ---------------------------------
with st.expander("📋 선택한 월의 실제 기온 데이터 확인"):
    display_df = month_df[
        ["연도", "평균기온(℃)"]
    ].sort_values("연도")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "※ 본 예측은 과거 평균기온과 연도의 선형 관계를 이용한 "
    "통계적 추정값이며 실제 미래 기온을 보장하지 않습니다."
)
