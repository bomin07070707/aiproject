
import re
import math
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

MALE_PINK = "#FF1493"
FEMALE_GREEN = "#00A86B"
TOTAL_PURPLE = "#7950A8"
FONT_FAMILY = "Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif"

# 세로축 눈금 간격: 5만 명
Y_TICK_INTERVAL = 50000


# ---------------------------------------------------------
# CSV 파일 읽기
# app.py는 pages 폴더 안, population.csv는 상위 폴더
# ---------------------------------------------------------
@st.cache_data
def load_population_data():
    project_folder = Path(__file__).resolve().parent.parent
    csv_path = project_folder / "population.csv"

    if not csv_path.exists():
        st.error(
            f"population.csv 파일을 찾을 수 없습니다.\n\n"
            f"찾으려는 위치: {csv_path}\n\n"
            "population.csv가 pages 폴더의 상위 폴더에 있는지 확인해주세요."
        )
        st.stop()

    encodings = ["euc-kr", "cp949", "utf-8-sig", "utf-8"]
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(csv_path, encoding=encoding)
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
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


# ---------------------------------------------------------
# 데이터 정리
# ---------------------------------------------------------
if "행정구역" not in df.columns:
    st.error("CSV 파일에 '행정구역' 열이 없습니다.")
    st.stop()


def clean_region(value):
    name = str(value).strip()
    name = re.sub(r"\s*\(\d+\)\s*$", "", name).strip()

    if name == "서울특별시":
        return name

    if name.startswith("서울특별시"):
        name = name.replace("서울특별시", "", 1).strip()

    return name


df["행정구역_표시"] = df["행정구역"].apply(clean_region)

# 인구수에 포함된 쉼표를 제거하고 숫자로 변환
for column in df.columns:
    if column not in ["행정구역", "행정구역_표시"]:
        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )


# ---------------------------------------------------------
# 연도 및 연령대 설정
# ---------------------------------------------------------
years = sorted({
    int(match.group(1))
    for column in df.columns
    if (match := re.match(r"(\d{4})년_", str(column)))
})

if not years:
    st.error("연도 정보를 열 이름에서 찾을 수 없습니다.")
    st.stop()


age_groups = [
    "0~9세", "10~19세", "20~29세", "30~39세",
    "40~49세", "50~59세", "60~69세", "70~79세",
    "80~89세", "90~99세", "100세 이상"
]


# ---------------------------------------------------------
# 화면 제목 및 기본 선택 메뉴
# ---------------------------------------------------------
st.title("📊 서울시 행정구별·성별·연령별 인구 분석")

st.write(
    "행정구역과 연도를 선택하면 남녀 연령별 인구를 비교하고, "
    "원하는 연령대 인구가 많은 자치구 순위를 확인할 수 있습니다."
)

col1, col2 = st.columns(2)

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
    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1
    )


# ---------------------------------------------------------
# 1. 선택한 행정구역의 남녀 연령별 인구 비교
# ---------------------------------------------------------
selected_rows = df[df["행정구역_표시"] == selected_region]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()

row = selected_rows.iloc[0]

male_columns = [
    f"{selected_year}년_남_거주자_{age}"
    for age in age_groups
]

female_columns = [
    f"{selected_year}년_여_거주자_{age}"
    for age in age_groups
]

missing_columns = [
    column
    for column in male_columns + female_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "남성 또는 여성의 연령별 데이터 열을 찾을 수 없습니다:\n\n"
        + ", ".join(missing_columns)
    )
    st.stop()


chart_df = pd.DataFrame({
    "나이": age_groups,
    "남성": [row[column] for column in male_columns],
    "여성": [row[column] for column in female_columns]
})

for column in ["남성", "여성"]:
    chart_df[column] = pd.to_numeric(
        chart_df[column],
        errors="coerce"
    )

chart_df = chart_df.dropna(subset=["남성", "여성"])

if chart_df.empty:
    st.warning("선택한 조건에 표시할 인구 데이터가 없습니다.")
    st.stop()


male_total = int(chart_df["남성"].sum())
female_total = int(chart_df["여성"].sum())

metric1, metric2 = st.columns(2)

metric1.metric("남성 인구 합계", f"{male_total:,}명")
metric2.metric("여성 인구 합계", f"{female_total:,}명")


# ---------------------------------------------------------
# 남녀 꺾은선 그래프
# ---------------------------------------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["남성"],
        mode="lines+markers",
        name="남성",
        line=dict(color=MALE_PINK, width=4),
        marker=dict(color=MALE_PINK, size=9),
        hovertemplate="나이: %{x}<br>남성 인구: %{y:,.0f}명<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["여성"],
        mode="lines+markers",
        name="여성",
        line=dict(color=FEMALE_GREEN, width=4),
        marker=dict(color=FEMALE_GREEN, size=9),
        hovertemplate="나이: %{x}<br>여성 인구: %{y:,.0f}명<extra></extra>"
    )
)


# 세로축 최대값을 5만 명 단위로 올림
max_population = float(chart_df[["남성", "여성"]].max().max())

y_max = max(
    Y_TICK_INTERVAL,
    math.ceil(max_population / Y_TICK_INTERVAL) * Y_TICK_INTERVAL
)


fig.update_layout(
    title=dict(
        text=f"{selected_region} · {selected_year}년 남녀 연령별 인구 비교",
        x=0.5,
        xanchor="center"
    ),

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

    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        range=[0, y_max],
        dtick=Y_TICK_INTERVAL,
        tickformat=",",
        showgrid=True,
        gridcolor="#D8D8D8",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#999999"
    ),

    font=dict(
        family=FONT_FAMILY,
        size=13,
        color="#222222"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    margin=dict(l=30, r=30, t=75, b=45),
    height=560,

    legend=dict(
        title="성별",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "남성은 핫핑크, 여성은 초록색으로 표시됩니다. "
    "가로축은 10세 단위 연령대이며, "
    "세로축 눈금과 격자선은 5만 명 단위입니다."
)


with st.expander("📋 그래프에 사용된 남녀 연령별 인구 데이터 보기"):
    display_df = chart_df.copy()

    display_df["남성"] = display_df["남성"].map(
        lambda value: f"{int(value):,}명"
    )

    display_df["여성"] = display_df["여성"].map(
        lambda value: f"{int(value):,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# 2. 선택한 연령대 인구가 많은 자치구 순위
# ---------------------------------------------------------
st.divider()
st.header("🏆 연령대별 인구가 많은 자치구 순위")

st.write(
    "연령대를 선택하면 해당 연령대 인구가 많은 자치구부터 "
    "막대그래프로 보여줍니다."
)

rank_col1, rank_col2, rank_col3 = st.columns(3)

with rank_col1:
    selected_age = st.selectbox(
        "🎂 순위를 확인할 연령대",
        age_groups,
        index=2,
        key="ranking_age"
    )

with rank_col2:
    selected_rank_gender = st.selectbox(
        "👥 순위 기준 성별",
        ["전체", "남성", "여성"],
        index=0,
        key="ranking_gender"
    )

with rank_col3:
    rank_count = st.selectbox(
        "📊 표시할 자치구 개수",
        [10, 25],
        index=0,
        format_func=lambda x: f"상위 {x}개 자치구",
        key="ranking_count"
    )


# 서울특별시 전체 합계 행은 제외하고 자치구만 분석
district_df = df[
    df["행정구역_표시"] != "서울특별시"
].copy()


if selected_rank_gender == "전체":
    ranking_column = f"{selected_year}년_거주자_{selected_age}"
elif selected_rank_gender == "남성":
    ranking_column = f"{selected_year}년_남_거주자_{selected_age}"
else:
    ranking_column = f"{selected_year}년_여_거주자_{selected_age}"


if ranking_column not in district_df.columns:
    st.error(f"순위 분석에 필요한 열을 찾을 수 없습니다: {ranking_column}")

else:
    ranking_df = district_df[
        ["행정구역_표시", ranking_column]
    ].copy()

    ranking_df[ranking_column] = pd.to_numeric(
        ranking_df[ranking_column],
        errors="coerce"
    )

    ranking_df = ranking_df.dropna(subset=[ranking_column])

    ranking_df = ranking_df.sort_values(
        by=ranking_column,
        ascending=False
    ).head(rank_count)

    ranking_df = ranking_df.rename(
        columns={
            "행정구역_표시": "자치구",
            ranking_column: "인구수"
        }
    )

    if ranking_df.empty:
        st.warning("선택한 연령대의 순위 데이터가 없습니다.")

    else:
        first_district = ranking_df.iloc[0]

        st.metric(
            f"{selected_age} 인구가 가장 많은 자치구",
            first_district["자치구"],
            f'{int(first_district["인구수"]):,}명'
        )

        rank_fig = go.Figure()

        rank_fig.add_trace(
            go.Bar(
                x=ranking_df["인구수"],
                y=ranking_df["자치구"],
                orientation="h",
                marker=dict(color=TOTAL_PURPLE),
                text=ranking_df["인구수"].map(
                    lambda value: f"{int(value):,}명"
                ),
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{y}<br>인구수: %{x:,.0f}명<extra></extra>"
            )
        )

        rank_fig.update_layout(
            title=dict(
                text=(
                    f"{selected_year}년 {selected_age} "
                    f"{selected_rank_gender} 인구 자치구 순위"
                ),
                x=0.5,
                xanchor="center"
            ),

            xaxis=dict(
                title="인구수 (명)",
                tickformat=",",
                showgrid=True,
                gridcolor="#E6E6E6"
            ),

            yaxis=dict(
                title="자치구",
                autorange="reversed",
                showgrid=False
            ),

            font=dict(
                family=FONT_FAMILY,
                size=13,
                color="#222222"
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",
            height=max(450, len(ranking_df) * 32 + 130),
            margin=dict(l=35, r=90, t=75, b=50)
        )

        st.plotly_chart(rank_fig, use_container_width=True)

        table_df = ranking_df.copy()

        table_df.insert(
            0,
            "순위",
            range(1, len(table_df) + 1)
        )

        table_df["인구수"] = table_df["인구수"].map(
            lambda value: f"{int(value):,}명"
        )

        with st.expander("📋 자치구별 순위 데이터 보기"):
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True
            )


# ---------------------------------------------------------
# 데이터 및 인코딩 정보
# ---------------------------------------------------------
with st.expander("🔎 데이터 및 인코딩 정보"):
    st.write(f"- 사용한 한글 인코딩: **{used_encoding}**")

    st.write(
        f"- 데이터 크기: **{df.shape[0]}행 × "
        f"{df.shape[1] - 2}개 데이터 열**"
    )

    st.write(
        f"- 결측치 총 개수: **{int(df.isna().sum().sum()):,}개**"
    )

    st.write("- CSV 파일은 pages 폴더의 상위 폴더에 있어야 합니다.")
