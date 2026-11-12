
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="기온 예측 알고리즘 비교",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 미래 예측")
st.markdown("""
과거 기온 데이터를 이용하여 미래 기온을 예측해 보세요!

선형회귀, 다항회귀, 랜덤 포레스트 회귀
3가지 알고리즘의 결과를 비교할 수 있습니다.
""")

# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def read_csv_data(file_bytes=None):

    if file_bytes is not None:
        source = io.BytesIO(file_bytes)
    else:
        candidates = [
            Path("temperature.csv"),
            Path("temperature (1).csv")
        ]

        file_path = next(
            (p for p in candidates if p.exists()),
            None
        )

        if file_path is None:
            raise FileNotFoundError(
                "temperature.csv 파일이 없습니다."
            )

        source = file_path

    last_error = None

    for encoding in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
        try:
            return pd.read_csv(source, encoding=encoding)
        except UnicodeDecodeError as e:
            last_error = e
            if file_bytes is not None:
                source.seek(0)

    raise ValueError(f"CSV 인코딩 오류: {last_error}")


uploaded_file = st.sidebar.file_uploader(
    "📂 temperature.csv 파일 업로드",
    type=["csv"]
)

try:
    file_bytes = (
        uploaded_file.getvalue()
        if uploaded_file is not None
        else None
    )

    df = read_csv_data(file_bytes)

except Exception as e:
    st.error(f"데이터 불러오기 실패: {e}")
    st.info(
        "temperature.csv 파일을 app.py와 같은 폴더에 넣거나 "
        "왼쪽 메뉴에서 파일을 업로드하세요."
    )
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV에 '일시', '평균기온(℃)' 열이 필요합니다.")
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
    st.error("분석 가능한 데이터가 없습니다.")
    st.stop()

# ==========================================
# 4. 사용자 입력
# ==========================================

st.sidebar.header("🔍 분석 조건")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

available_months = sorted(df["월"].unique())

selected_month = st.sidebar.selectbox(
    "분석할 월 선택",
    available_months,
    format_func=lambda x: month_names[x]
)

month_df = df[
    df["월"] == selected_month
].sort_values("연도").copy()

if len(month_df) < 3:
    st.error("선택한 월의 데이터가 3개 연도 이상 필요합니다.")
    st.stop()

latest_year = int(month_df["연도"].max())

forecast_year = st.sidebar.number_input(
    "예측할 연도 입력",
    min_value=latest_year + 1,
    max_value=latest_year + 50,
    value=latest_year + 5,
    step=1
)

forecast_year = int(forecast_year)

# ==========================================
# 5. 회귀 알고리즘 선택
# ==========================================

st.sidebar.divider()
st.sidebar.header("🤖 회귀 알고리즘 선택")

algorithm_names = [
    "선형회귀",
    "다항회귀",
    "랜덤 포레스트 회귀"
]

selected_algorithm = st.sidebar.selectbox(
    "사용할 알고리즘",
    algorithm_names
)

# ==========================================
# 6. 데이터 학습
# ==========================================

X = month_df[["연도"]].values.astype(float)
y = month_df["평균기온(℃)"].values.astype(float)

models = {
    "선형회귀": LinearRegression(),

    "다항회귀": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    ),

    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        min_samples_leaf=2,
        random_state=42
    )
}

predictions = {}
scores = {}
fitted_values = {}

for name, model in models.items():

    model.fit(X, y)

    # 미래 기온 예측
    future_X = np.array(
        [[forecast_year]],
        dtype=float
    )

    predictions[name] = float(
        model.predict(future_X)[0]
    )

    # 과거 데이터에 대한 예측
    fitted = model.predict(X)
    fitted_values[name] = fitted

    # 결정계수 계산
    scores[name] = float(model.score(X, y))

# ==========================================
# 7. 선택한 알고리즘 예측 결과
# ==========================================

st.subheader(
    f"📊 {month_names[selected_month]} 평균기온 예측"
)

selected_prediction = predictions[selected_algorithm]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 알고리즘",
        selected_algorithm
    )

with col2:
    st.metric(
        "예측 연도",
        f"{forecast_year}년"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{selected_prediction:.2f} ℃"
    )

st.success(
    f"{forecast_year}년 {month_names[selected_month]}의 "
    f"예상 평균기온은 **{selected_prediction:.2f}℃**입니다."
)

# ==========================================
# 8. 세 가지 알고리즘 그래프 비교
# ==========================================

st.divider()

st.subheader("📈 3가지 알고리즘의 예측 추세 비교")

st.caption(
    "파란색 점은 실제 관측값이며, 세 가지 색상의 선은 "
    "각 알고리즘이 학습한 예측 추세입니다."
)

colors = {
    "선형회귀": "red",
    "다항회귀": "green",
    "랜덤 포레스트 회귀": "purple"
}

# 과거부터 미래까지 예측 구간 생성
X_graph = np.linspace(
    X.min(),
    forecast_year,
    300
).reshape(-1, 1)

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 데이터
ax.scatter(
    X.flatten(),
    y,
    color="royalblue",
    s=65,
    label="Actual Temperature",
    zorder=5
)

ax.plot(
    X.flatten(),
    y,
    color="skyblue",
    alpha=0.5,
    linewidth=1
)

# 각 알고리즘의 추세선
for name, model in models.items():

    graph_predictions = model.predict(X_graph)

    # 선택한 알고리즘은 굵게 표시
    if name == selected_algorithm:
        line_width = 3.5
        line_style = "-"
        alpha = 1
    else:
        line_width = 2
        line_style = "--"
        alpha = 0.7

    ax.plot(
        X_graph.flatten(),
        graph_predictions,
        color=colors[name],
        linewidth=line_width,
        linestyle=line_style,
        alpha=alpha,
        label=name
    )

    # 미래 예측 지점
    ax.scatter(
        forecast_year,
        predictions[name],
        color=colors[name],
        marker="*",
        s=220,
        edgecolors="black",
        linewidths=0.5,
        zorder=6
    )

    # 선택한 알고리즘에 예측값 표시
    if name == selected_algorithm:
        ax.annotate(
            f"{forecast_year}년\n{predictions[name]:.2f}℃",
            xy=(forecast_year, predictions[name]),
            xytext=(10, 12),
            textcoords="offset points",
            color=colors[name],
            fontsize=11,
            fontweight="bold"
        )

ax.axvline(
    latest_year,
    color="gray",
    linestyle=":",
    alpha=0.8,
    label="Last Observation"
)

ax.set_title(
    f"{month_names[selected_month]} 평균기온 알고리즘 비교",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Year")
ax.set_ylabel("Average Temperature (℃)")

ax.grid(alpha=0.3)
ax.legend(loc="best")
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ==========================================
# 9. 미래 예측값 비교 그래프
# ==========================================

st.divider()

st.subheader("🏆 알고리즘별 미래 예측 기온 비교")

fig2, ax2 = plt.subplots(figsize=(10, 5))

names = list(predictions.keys())
values = list(predictions.values())

bar_colors = [
    colors[name] for name in names
]

bars = ax2.bar(
    names,
    values,
    color=bar_colors,
    alpha=0.8
)

for bar, value in zip(bars, values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}℃",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

ax2.set_title(
    f"{forecast_year}년 {month_names[selected_month]} 예측 결과"
)

ax2.set_ylabel("Predicted Temperature (℃)")
ax2.grid(axis="y", alpha=0.3)
fig2.tight_layout()

st.pyplot(fig2)
plt.close(fig2)

# ==========================================
# 10. 알고리즘별 결과 비교표
# ==========================================

st.subheader("📋 알고리즘별 결과 비교")

comparison_df = pd.DataFrame({
    "회귀 알고리즘": names,
    "예측 평균기온(℃)": [
        round(predictions[name], 2)
        for name in names
    ],
    "과거 데이터 결정계수(R²)": [
        round(scores[name], 4)
        for name in names
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "※ 결정계수는 학습에 사용한 과거 데이터에 대한 설명력입니다. "
    "미래 예측 정확도를 직접 나타내지는 않습니다."
)

# ==========================================
# 11. 선택한 알고리즘 설명
# ==========================================

st.divider()

st.subheader("📚 선택한 회귀 알고리즘 알아보기")

if selected_algorithm == "선형회귀":

    st.markdown("""
    ### 📏 선형회귀 (Linear Regression)

    선형회귀는 실제 데이터에 가장 잘 맞는 직선을 찾는 방법입니다.

    **작동 원리**

    1. 과거 연도와 평균기온 데이터를 수집합니다.
    2. 데이터와 직선 사이의 오차를 계산합니다.
    3. 오차의 제곱합이 가장 작아지는 직선을 찾습니다.
    4. 미래 연도를 직선에 대입하여 기온을 예측합니다.

    **특징**

    - 직선 형태로 기온의 장기적인 추세를 분석합니다.
    - 계산이 간단하고 결과를 이해하기 쉽습니다.
    - 기온 변화가 곡선 형태라면 충분히 설명하지 못할 수 있습니다.
    """)

    st.latex(r"\hat{y} = b_0 + b_1x")

elif selected_algorithm == "다항회귀":

    st.markdown("""
    ### 📈 다항회귀 (Polynomial Regression)

    다항회귀는 직선이 아닌 곡선을 이용하여 데이터의 관계를 분석합니다.

    이번 앱에서는 2차 다항식을 사용합니다.

    **작동 원리**

    1. 과거 연도와 평균기온 데이터를 수집합니다.
    2. 연도뿐 아니라 연도의 제곱 항도 함께 사용합니다.
    3. 데이터에 가장 잘 맞는 곡선을 계산합니다.
    4. 계산된 곡선을 이용해 미래 기온을 예측합니다.

    **특징**

    - 상승과 하락이 함께 나타나는 패턴을 표현할 수 있습니다.
    - 직선으로 설명하기 어려운 데이터에 활용할 수 있습니다.
    - 미래로 멀리 예측하면 곡선이 실제와 크게 달라질 수 있습니다.
    """)

    st.latex(r"\hat{y} = b_0 + b_1x + b_2x^2")

elif selected_algorithm == "랜덤 포레스트 회귀":

    st.markdown("""
    ### 🌳 랜덤 포레스트 회귀 (Random Forest Regression)

    랜덤 포레스트는 여러 개의 결정트리를 만들고
    각 트리의 예측 결과를 평균하여 최종값을 구하는 방법입니다.

    **작동 원리**

    1. 과거 데이터를 이용해 여러 개의 학습용 표본을 만듭니다.
    2. 각각의 표본으로 여러 결정트리를 학습합니다.
    3. 각 트리가 예측한 기온을 계산합니다.
    4. 여러 트리의 예측값을 평균하여 최종 기온을 구합니다.

    **특징**

    - 복잡하고 비선형적인 관계를 분석할 수 있습니다.
    - 여러 트리의 결과를 종합하기 때문에 개별 트리보다 안정적일 수 있습니다.
    - 학습 데이터의 범위를 벗어난 미래 연도에서는 새로운 상승·하락 추세를 외삽하지 못합니다.
    """)

    st.latex(
        r"\hat{y} = \frac{1}{N}"
        r"\sum_{i=1}^{N} T_i(x)"
    )

# ==========================================
# 12. 랜덤 포레스트 예측 시 주의점
# ==========================================

st.info("""
💡 **알고리즘 비교할 때 알아두기**

랜덤 포레스트는 과거 학습 데이터 범위 안의 패턴을 분석하는 데 강점이 있지만,
학습한 연도보다 더 먼 미래의 기온이 계속 상승하거나 하락하는 현상을
직접 예측하지는 못합니다.

반면 선형회귀와 다항회귀는 수학적 추세선을 미래까지 연장합니다.

따라서 세 알고리즘의 미래 예측값이 다르게 나타나는 것은
각 알고리즘의 작동 방식이 서로 다르기 때문입니다.
""")

# ==========================================
# 13. 실제 데이터 확인
# ==========================================

with st.expander("📂 과거 실제 기온 데이터 확인"):

    st.dataframe(
        month_df[["연도", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "※ 이 앱은 학습용 통계 분석 프로그램입니다. "
    "예측 결과는 실제 기상예보와 다를 수 있습니다."
)
