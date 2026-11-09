
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 전체 연도의 최고기온과 최저기온을 비교합니다.")

# CSV 한글 인코딩 처리
@st.cache_data
def load_data(file_bytes):
    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
        try:
            return pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")

# 파일 불러오기
uploaded_file = st.file_uploader(
    "temperature.csv 파일 업로드",
    type=["csv"]
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
elif Path("temperature.csv").exists():
    file_bytes = Path("temperature.csv").read_bytes()
else:
    st.warning("temperature.csv 파일을 업로드해 주세요.")
    st.stop()

try:
    df = load_data(file_bytes)
except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

# 필요한 열 확인
required = ["일시", "최고기온(℃)", "최저기온(℃)"]

if not all(col in df.columns for col in required):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

# 월 이름 변환
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

# 날짜 분리
parts = (
    df["일시"].astype(str).str.strip()
    .str.extract(r"^([A-Za-z]{3})-(\d{2})$")
)

df["월번호"] = parts[0].str.title().map(month_map)

valid = parts[1].notna() & df["월번호"].notna()
df = df.loc[valid].copy()

# 두 자리 연도 복원
year_values = parts.loc[valid, 1].astype(int).tolist()

if not year_values:
    st.error("날짜 데이터를 확인해 주세요.")
    st.stop()

years = []
century = 1900
previous = year_values[0]

for y in year_values:
    if previous - y > 50:
        century += 100
    years.append(century + y)
    previous = y

df["연도"] = years

# 기온 숫자 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# 월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_name = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    list(month_names.values())
)

selected_month = {
    name: number
    for number, name in month_names.items()
}[selected_name]

# 선택한 월의 데이터
month_df = df[df["월번호"] == selected_month]

# 연도별 최고기온과 최저기온
yearly = (
    month_df.groupby("연도", as_index=False)
    .agg(
        최고기온=("최고기온(℃)", "max"),
        최저기온=("최저기온(℃)", "min")
    )
    .sort_values("연도")
)

yearly = yearly.dropna(
    subset=["최고기온", "최저기온"],
    how="all"
)

# 그래프
if yearly.empty:
    st.info("선택한 월의 기온 데이터가 없습니다.")

else:
    fig = go.Figure()

    # 최고기온: 핑크색
    fig.add_trace(go.Scatter(
        x=yearly["연도"],
        y=yearly["최고기온"],
        mode="lines+markers",
        name="최고 기온",
        line=dict(color="#FF69B4", width=2.5),
        marker=dict(color="#FF69B4", size=6),
        connectgaps=False
    ))

    # 최저기온: 하늘색
    fig.add_trace(go.Scatter(
        x=yearly["연도"],
        y=yearly["최저기온"],
        mode="lines+markers",
        name="최저 기온",
        line=dict(color="#87CEEB", width=2.5),
        marker=dict(color="#87CEEB", size=6),
        connectgaps=False
    ))

    # 그래프 제목과 축 설정
    fig.update_layout(
        title=dict(
            text="월별 기온분석",
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="연도",
        yaxis_title="온도 (℃)",
        legend=dict(
            title="범례",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        template="plotly_white",
        height=600
    )

    fig.update_xaxes(
        showgrid=True,
        dtick=10
    )

    fig.update_yaxes(showgrid=True)

    st.subheader(f"📊 {selected_name} 연도별 기온 분석")

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        f"분석 연도: {int(yearly['연도'].min())}년 ~ "
        f"{int(yearly['연도'].max())}년"
    )

    # 데이터 표
    with st.expander("연도별 기온 데이터 확인하기"):
        display = yearly.rename(columns={
            "최고기온": "최고기온(℃)",
            "최저기온": "최저기온(℃)"
        })
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )
