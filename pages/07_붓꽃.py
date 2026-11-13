
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "머신러닝이 붓꽃의 품종을 예측합니다."
)

st.divider()

# ---------------------------------
# 2. 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8-sig")

    required_columns = [
        "꽃잎길이", "꽃잎너비", "품종"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 열이 없습니다."
            )

    df = df[required_columns].copy()

    df["꽃잎길이"] = pd.to_numeric(
        df["꽃잎길이"], errors="coerce"
    )
    df["꽃잎너비"] = pd.to_numeric(
        df["꽃잎너비"], errors="coerce"
    )
    df = df.dropna()

    if df.empty or df["품종"].nunique() < 2:
        raise ValueError("학습에 필요한 데이터가 부족합니다.")

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.info(
        "Iris.csv 파일이 app.py와 같은 폴더에 있는지 확인하세요."
    )
    st.stop()

# ---------------------------------
# 3. 입력 범위 설정
# ---------------------------------
petal_length_min = float(df["꽃잎길이"].min())
petal_length_max = float(df["꽃잎길이"].max())

petal_width_min = float(df["꽃잎너비"].min())
petal_width_max = float(df["꽃잎너비"].max())

st.subheader("📏 꽃잎 크기 입력")

st.info(
    f"""
    **입력 가능한 범위**

    - 꽃잎 길이: {petal_length_min:.1f} ~ {petal_length_max:.1f} cm
    - 꽃잎 너비: {petal_width_min:.1f} ~ {petal_width_max:.1f} cm

    입력 범위는 업로드된 Iris.csv 데이터의 실제 최솟값과
    최댓값을 기준으로 설정했습니다.
    """
)

col1, col2 = st.columns(2)

with col1:
    input_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=petal_length_min,
        max_value=petal_length_max,
        value=4.5,
        step=0.1,
        format="%.1f"
    )

with col2:
    input_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=petal_width_min,
        max_value=petal_width_max,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

# ---------------------------------
# 4. 랜덤 포레스트 모델 학습
# ---------------------------------
X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    max_features="sqrt"
)

# 5겹 교차검증
cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

# 전체 데이터로 최종 학습
model.fit(X, y)

# ---------------------------------
# 5. 사용자 입력값 예측
# ---------------------------------
input_data = pd.DataFrame(
    [[input_length, input_width]],
    columns=["꽃잎길이", "꽃잎너비"]
)

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

st.divider()
st.subheader("🤖 AI 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.success(f"🌸 예측된 품종: {prediction}")

with result_col2:
    confidence = np.max(probabilities) * 100
    st.metric(
        "가장 높은 예측 확률",
        f"{confidence:.1f}%"
    )

# ---------------------------------
# 6. 품종별 예측 확률
# ---------------------------------
st.subheader("📊 품종별 예측 확률")

prob_df = pd.DataFrame({
    "품종": model.classes_,
    "예측 확률(%)": probabilities * 100
})

prob_df = prob_df.sort_values(
    "예측 확률(%)", ascending=False
)

st.bar_chart(
    prob_df.set_index("품종"),
    horizontal=True
)

st.dataframe(
    prob_df.style.format({
        "예측 확률(%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------
# 7. 분류 결과 시각화
# ---------------------------------
st.divider()
st.subheader("📍 꽃잎 크기와 품종 분류 시각화")

st.write(
    "배경 색상은 AI가 각 위치를 어떤 품종으로 "
    "분류하는지 보여줍니다. "
    "초록색 별은 사용자가 입력한 꽃잎 크기입니다."
)

# 그래프 영역 생성
x_min = petal_length_min - 0.3
x_max = petal_length_max + 0.3
y_min = petal_width_min - 0.2
y_max = petal_width_max + 0.2

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 250),
    np.linspace(y_min, y_max, 250)
)

grid_data = pd.DataFrame({
    "꽃잎길이": xx.ravel(),
    "꽃잎너비": yy.ravel()
})

Z = model.predict(grid_data)

class_to_num = {
    name: i for i, name in enumerate(model.classes_)
}

Z_num = np.array([
    class_to_num[name] for name in Z
]).reshape(xx.shape)

# 품종별 그래프 색상
colors = ["#F4A6A6", "#A6C8F4", "#B8DDA8"]
cmap = ListedColormap(colors)

fig, ax = plt.subplots(figsize=(10, 7))

# AI 분류 영역
ax.contourf(
    xx, yy, Z_num,
    alpha=0.30,
    cmap=cmap,
    levels=np.arange(len(model.classes_) + 1) - 0.5
)

# 기존 데이터 표시
for i, species in enumerate(model.classes_):
    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎길이"],
        subset["꽃잎너비"],
        label=species,
        color=colors[i],
        edgecolors="black",
        s=45,
        alpha=0.85
    )

# 사용자가 입력한 값: 초록색 별
ax.scatter(
    input_length,
    input_width,
    marker="*",
    color="limegreen",
    edgecolors="black",
    s=450,
    linewidths=1.5,
    label="Your Input",
    zorder=10
)

ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)

ax.set_title(
    f"AI Iris Classification: {prediction}",
    fontsize=15
)

ax.legend(loc="best")
ax.grid(alpha=0.2)

st.pyplot(fig)
plt.close(fig)

# ---------------------------------
# 8. 왜 이 품종으로 분류했을까?
# ---------------------------------
st.divider()
st.subheader("🔍 왜 이 품종으로 분류했을까?")

st.write(
    "랜덤 포레스트 모델의 특성 중요도를 통해 "
    "두 가지 입력값 중 어떤 변수가 분류에 더 많이 "
    "기여했는지 확인할 수 있습니다."
)

importance_df = pd.DataFrame({
    "측정 항목": ["꽃잎 길이", "꽃잎 너비"],
    "중요도": model.feature_importances_
})

importance_df = importance_df.sort_values(
    "중요도", ascending=False
)

st.bar_chart(
    importance_df.set_index("측정 항목"),
    horizontal=True
)

st.write("**이번 입력값 분석**")

st.write(
    f"- 입력한 꽃잎 길이: {input_length:.1f} cm"
)
st.write(
    f"- 입력한 꽃잎 너비: {input_width:.1f} cm"
)
st.write(
    f"- 가장 높은 예측 확률을 보인 품종: {prediction}"
)

st.info(
    "그래프의 배경은 랜덤 포레스트가 학습한 "
    "분류 영역입니다. 초록색 별이 위치한 영역의 "
    "분류 결과가 바로 예측된 품종입니다. "
    "여러 결정 트리의 예측을 종합해 결과를 결정합니다."
)

# ---------------------------------
# 9. 모델 성능 확인
# ---------------------------------
st.divider()
st.subheader("📈 머신러닝 모델 성능")

accuracy = cv_scores.mean() * 100

st.metric(
    "5겹 교차검증 평균 정확도",
    f"{accuracy:.2f}%"
)

st.write(
    "전체 데이터를 5개 그룹으로 나누어 "
    "교차검증을 진행한 평균 정확도입니다."
)

cv_df = pd.DataFrame({
    "검증 그룹": [
        f"{i+1}번째" for i in range(len(cv_scores))
    ],
    "정확도(%)": cv_scores * 100
})

st.bar_chart(
    cv_df.set_index("검증 그룹")
)

# ---------------------------------
# 10. 데이터 확인
# ---------------------------------
with st.expander("📚 학습에 사용한 데이터 확인"):
    st.write(f"전체 데이터: {len(df)}개")
    st.dataframe(df, use_container_width=True)

st.caption(
    "🌸 Iris 품종 예측 AI | "
    "Pandas + Scikit-learn + Streamlit"
)
