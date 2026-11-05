
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

HOT_PINK = "#FF1493"
FONT_FAMILY = "Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif"


# ---------------------------------------------------------
# CSV 파일 읽기
# app.py는 pages 폴더 안에 있고
# population.csv는 상위 폴더에 있음
# ---------------------------------------------------------
@st.cache_data
def load_population_data():

    project_folder = Path(__file__).resolve().parent.parent
    csv_path = project_folder / "population.csv"

    if not csv_path.exists():
        st.error(
            f"population.csv 파일을 찾을 수 없습니다.\n\n"
            f"찾으려는 위치: {csv_path}\n\n"
            "population.csv가 pages 폴더의 상위 폴더에 "
            "있는지 확인해주세요."
        )
        st.stop()

    # 한글 인코딩 자동 대응
    encodings = [
        "euc-kr",
        "cp949",
        "utf-8-sig",
        "utf-8"
    ]

    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                csv_path,
                encoding=encoding
            )
            return data, encoding

        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        "CSV 파일의 한글 인코딩을 읽을 수 없습니다. "
        "EUC-KR, CP949 또는 UTF-8 형식인지 확인해주세요."
    ) from last_error


try:
    df, used_encoding = load_population_data()

except Exception as error:
    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )
    st.stop()


# ---------------------------------------------------------
# 데이터 정리
# ---------------------------------------------------------
if "행정구역" not in df.columns:
    st.error("CSV 파일에 '행정구역' 열이 없습니다.")
    st.stop()


# 행정구역 이름 정리
def clean_region(value):

    name = str(value).strip()

    # 행정구역 코드 제거
    name = re.sub(
        r"\s*\(\d+\)\s*$",
        "",
        name
    ).strip()

    # 서울시 전체
    if name == "서울특별시":
        return name

    # 자치구 이름만 남기기
    if name.startswith("서울특별시"):
        name = name.replace(
            "서울특별시",
            "",
            1
        ).strip()

    return name


df["행정구역_표시"] = df["행정구역"].apply(
    clean_region
)


# 숫자 데이터 변환
for column in df.columns:

    if column not in [
        "행정구역",
        "행정구역_표시"
    ]:

        df[column] = pd.to_numeric(
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce"
        )


# ---------------------------------------------------------
# 연도 및 연령대 설정
# ---------------------------------------------------------
years = sorted({
    int(match.group(1))
    for column in df.columns
    if (match := re.match(
        r"(\d{4})년_",
        str(column)
    ))
})

if not years:
    st.error("연도 정보를 열 이름에서 찾을 수 없습니다.")
    st.stop()


age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# ---------------------------------------------------------
# 화면 제목
# ---------------------------------------------------------
st.title(
    "📊 서울시 행정구별·성별·연령별 인구 분석"
)

st.write(
    "행정구역, 성별, 연도를 선택하면 "
    "연령대별 인구수를 핫핑크 꺾은선 그래프로 "
    "확인할 수 있습니다."
)


# ---------------------------------------------------------
# 선택 메뉴
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)


with col1:

    region_options = sorted(
        df["행정구역_표시"].dropna().unique().tolist(),
        key=lambda x: (x != "서울특별시", x)
    )

    selected_region = st.selectbox(
        "🏙️ 행정구역 선택",
        region_options,
        index=0
    )


with col2:

    selected_gender = st.selectbox(
        "👥 성별 선택",
        ["전체", "남성", "여성"]
    )


with col3:

    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1
    )


# ---------------------------------------------------------
# 선택한 조건에 맞는 행 찾기
# ---------------------------------------------------------
selected_rows = df[
    df["행정구역_표시"] == selected_region
]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()


row = selected_rows.iloc[0]


# 성별에 따른 열 이름
gender_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[selected_gender]


# 선택한 연도의 연령별 인구 열
population_columns = [
    f"{selected_year}년_{gender_prefix}거주자_{age}"
    for age in age_groups
]


# 필요한 열이 있는지 확인
missing_columns = [
    column
    for column in population_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "선택한 조건에 해당하는 연령별 데이터 열을 "
        "찾을 수 없습니다:\n\n"
        + ", ".join(missing_columns)
    )

    st.stop()


# ---------------------------------------------------------
# 그래프용 데이터 생성
# ---------------------------------------------------------
population_values = [
    row[column]
    for column in population_columns
]

chart_df = pd.DataFrame({
    "나이": age_groups,
    "인구수": population_values
})


chart_df["인구수"] = pd.to_numeric(
    chart_df["인구수"],
    errors="coerce"
)

chart_df = chart_df.dropna(
    subset=["인구수"]
)


if chart_df.empty:
    st.warning(
        "선택한 조건에 표시할 인구 데이터가 없습니다."
    )
    st.stop()


# ---------------------------------------------------------
# 요약 정보
# ---------------------------------------------------------
total_population = int(
    chart_df["인구수"].sum()
)

max_age_row = chart_df.loc[
    chart_df["인구수"].idxmax()
]


metric1, metric2 = st.columns(2)


metric1.metric(
    "선택한 연령대 인구 합계",
    f"{total_population:,}명"
)


metric2.metric(
    "인구가 가장 많은 연령대",
    str(max_age_row["나이"]),
    f'{int(max_age_row["인구수"]):,}명'
)


# ---------------------------------------------------------
# 핫핑크 꺾은선 그래프
# ---------------------------------------------------------
fig = go.Figure()


fig.add_trace(
    go.Scatter(

        x=chart_df["나이"],

        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color=HOT_PINK,
            width=4
        ),

        marker=dict(
            color=HOT_PINK,
            size=9
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


# 세로축 최대값을 10만 명 단위로 올림
max_population = float(
    chart_df["인구수"].max()
)

y_max = max(
    100000,
    int(max_population / 100000 + 1) * 100000
)


fig.update_layout(

    title=dict(
        text=(
            f"{selected_region} · "
            f"{selected_year}년 · "
            f"{selected_gender} 연령별 인구"
        ),
        x=0.5,
        xanchor="center"
    ),

    # 가로축
    xaxis=dict(
        title="나이",

        type="category",

        categoryorder="array",

        categoryarray=age_groups,

        tickmode="array",

        tickvals=age_groups,

        ticktext=age_groups,

        showgrid=True,

        gridcolor="#E6E6E6",

        gridwidth=1,

        showline=True,

        linecolor="#888888"
    ),

    # 세로축
    yaxis=dict(
        title="인구수 (명)",

        rangemode="tozero",

        range=[0, y_max],

        dtick=100000,

        tickformat=",",

        showgrid=True,

        gridcolor="#D8D8D8",

        gridwidth=1,

        zeroline=True,

        zerolinecolor="#999999"
    ),

    # 글자 설정
    font=dict(
        family=FONT_FAMILY,
        size=13,
        color="#222222"
    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    hovermode="x unified",

    margin=dict(
        l=30,
        r=30,
        t=75,
        b=45
    ),

    height=560,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


st.info(
    "가로축은 0~9세부터 100세 이상까지 "
    "10세 단위로 표시하며, "
    "세로축 눈금과 가로 격자선은 "
    "10만 명 단위입니다."
)


# ---------------------------------------------------------
# 상세 데이터 표
# ---------------------------------------------------------
with st.expander(
    "📋 그래프에 사용된 연령별 인구 데이터 보기"
):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].map(
        lambda value: f"{int(value):,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# 데이터 및 인코딩 정보
# ---------------------------------------------------------
with st.expander(
    "🔎 데이터 및 인코딩 정보"
):

    st.write(
        f"- 사용한 한글 인코딩: **{used_encoding}**"
    )

    st.write(
        f"- 데이터 크기: **{df.shape[0]}행 × "
        f"{df.shape[1] - 2}개 데이터 열**"
    )

    st.write(
        f"- 결측치 총 개수: "
        f"**{int(df.isna().sum().sum()):,}개**"
    )

    st.write(
        "- CSV 파일은 pages 폴더의 상위 폴더에 있어야 합니다."
    )
