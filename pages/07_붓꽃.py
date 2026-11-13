
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.inspection import permutation_importance

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="AI 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")

st.write(
    "꽃잎 길이와 너비를 입력하고 "
    "3가지 머신러닝 알고리즘으로 붓꽃 품종을 예측해 보세요!"
)

st.divider()

# =====================================
# 2. 데이터 불러오기
# =====================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8-sig")

    columns = ["꽃잎길이", "꽃잎너비", "품종"]

    for col in columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV 파일에 {col} 열이 없습니다."
            )

    df = df[columns].copy()

    df["꽃잎길이"] = pd.to_numeric(
        df["꽃잎길이"], errors="coerce"
    )
    df["꽃잎너비"] = pd.to_numeric(
        df["꽃잎너비"], errors="coerce"
    )

    df = df.dropna()

    if df.empty or df["품종"].nunique() < 2:
        raise ValueError("학습 데이터가 부족합니다.")

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.info(
        "Iris.csv 파일이 app.py와 같은 폴더에 있는지 확인하세요."
    )
    st.stop()


# =====================================
# 3. 데이터 범위 확인
# =====================================
length_min = float(df["꽃잎길이"].min())
length_max = float(df["꽃잎길이"].max())

width_min = float(df["꽃잎너비"].min())
width_max = float(df["꽃잎너비"].max())

st.subheader("📏 꽃잎 크기 입력")

st.info(
    f"""
    입력 가능한 범위를 확인하세요!

    🌷 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm

    🌷 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm
    """
)

col1, col2 = st.columns(2)

with col1:
    input_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=float(np.clip(4.5, length_min, length_max)),
        step=0.1,
        format="%.1f"
    )

with col2:
    input_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(np.clip(1.5, width_min, width_max)),
        step=0.1,
        format="%.1f"
    )


# =====================================
# 4. 알고리즘 설명
# =====================================
st.divider()
st.subheader("🧠 분류 알고리즘 선택")

algorithm_names = [
    "랜덤 포레스트 (Random Forest)",
    "K-최근접 이웃 (KNN)",
    "서포트 벡터 머신 (SVM)"
]

algorithm_descriptions = {
    algorithm_names[0]: """
    **랜덤 포레스트**

    여러 개의 결정 트리가 각각 품종을 예측하고
    투표를 통해 최종 품종을 결정합니다.

    - 여러 트리의 예측 결과를 종합
    - 복잡한 데이터 분류에 활용
    - 특성 중요도 분석 가능
    """,

    algorithm_names[1]: """
    **K-최근접 이웃 (KNN)**

    입력한 데이터와 가장 가까운 K개의 데이터를 찾아
    가장 많이 등장한 품종으로 분류합니다.

    - 주변 데이터와의 거리를 이용
    - 가까운 데이터의 영향을 많이 받음
    - K값에 따라 예측 결과가 달라질 수 있음
    """,

    algorithm_names[2]: """
    **서포트 벡터 머신 (SVM)**

    서로 다른 품종을 가장 잘 구분할 수 있는
    분류 경계를 학습합니다.

    - 품종 사이의 경계를 찾음
    - 새로운 데이터의 위치를 기준으로 분류
    - RBF 커널로 복잡한 경계도 학습 가능
    """
}

selected_algorithm = st.selectbox(
    "사용할 머신러닝 알고리즘을 선택하세요.",
    algorithm_names
)

st.markdown(
    algorithm_descriptions[selected_algorithm]
)

# =====================================
# 5. 머신러닝 모델 만들기
# =====================================
X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

models = {
    algorithm_names[0]: RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_features="sqrt"
    ),

    algorithm_names[1]: Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=5))
    ]),

    algorithm_names[2]: Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=42
        ))
    ])
}

# =====================================
# 6. 3가지 알고리즘 성능 비교
# =====================================
st.divider()
st.subheader("📊 3가지 알고리즘 성능 비교")

comparison_results = []

fitted_models = {}

with st.spinner("3가지 알고리즘을 학습하고 있습니다..."):

    for name, model in models.items():

        scores = cross_val_score(
            model,
            X,
            y,
            cv=5,
            scoring="accuracy"
        )

        model.fit(X, y)

        fitted_models[name] = model

        comparison_results.append({
            "알고리즘": name,
            "평균 정확도(%)": scores.mean() * 100,
            "최고 정확도(%)": scores.max() * 100,
            "최저 정확도(%)": scores.min() * 100
        })

comparison_df = pd.DataFrame(comparison_results)

st.dataframe(
    comparison_df.style.format({
        "평균 정확도(%)": "{:.2f}",
        "최고 정확도(%)": "{:.2f}",
        "최저 정확도(%)": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.bar_chart(
    comparison_df.set_index("알고리즘")[
        ["평균 정확도(%)"]
    ],
    horizontal=True
)

st.caption(
    "정확도는 5겹 교차검증 결과입니다. "
    "각 알고리즘은 동일한 데이터와 입력 변수로 평가합니다."
)


# =====================================
# 7. 선택한 알고리즘으로 예측
# =====================================
model = fitted_models[selected_algorithm]

input_data = pd.DataFrame(
    [[input_length, input_width]],
    columns=["꽃잎길이", "꽃잎너비"]
)

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

st.divider()
st.subheader("🤖 AI 품종 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.success(
        f"🌸 예측된 품종: {prediction}"
    )

with result_col2:
    st.metric(
        "가장 높은 예측 확률",
        f"{probabilities.max() * 100:.2f}%"
    )


# =====================================
# 8. 알고리즘별 예측 결과 비교
# =====================================
st.subheader("🔎 알고리즘별 예측 결과 비교")

prediction_results = []

for name, fitted_model in fitted_models.items():

    pred = fitted_model.predict(input_data)[0]

    prob = fitted_model.predict_proba(input_data)[0]

    prediction_results.append({
        "알고리즘": name,
        "예측 품종": pred,
        "예측 확률(%)": prob.max() * 100
    })

prediction_df = pd.DataFrame(prediction_results)

st.dataframe(
    prediction_df.style.format({
        "예측 확률(%)": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.write(
    "알고리즘마다 학습 방식이 다르기 때문에 "
    "같은 입력값에서도 예측 결과와 확률이 달라질 수 있습니다."
)


# =====================================
# 9. 품종별 예측 확률
# =====================================
st.subheader("📈 선택한 알고리즘의 품종별 예측 확률")

prob_df = pd.DataFrame({
    "품종": model.classes_,
    "예측 확률(%)": probabilities * 100
})

prob_df = prob_df.sort_values(
    "예측 확률(%)",
    ascending=False
)

st.bar_chart(
    prob_df.set_index("품종"),
    horizontal=True
)


# =====================================
# 10. 분류 영역 그래프
# =====================================
st.divider()
st.subheader("📍 AI 분류 영역 시각화")

st.write(
    "배경 색상은 AI가 각 위치를 어떤 품종으로 분류하는지 "
    "나타냅니다. 초록색 별은 사용자가 입력한 값입니다."
)

x_min = length_min - 0.3
x_max = length_max + 0.3

y_min = width_min - 0.2
y_max = width_max + 0.2

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

colors = [
    "#F4A6A6",
    "#A6C8F4",
    "#B8DDA8"
]

cmap = ListedColormap(colors)

fig, ax = plt.subplots(figsize=(10, 7))

ax.contourf(
    xx,
    yy,
    Z_num,
    alpha=0.35,
    cmap=cmap,
    levels=np.arange(len(model.classes_) + 1) - 0.5
)

# 기존 붓꽃 데이터
for i, species in enumerate(model.classes_):

    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎길이"],
        subset["꽃잎너비"],
        color=colors[i],
        label=species,
        edgecolors="black",
        s=45,
        alpha=0.85
    )

# 사용자 입력값: 초록색 별
ax.scatter(
    input_length,
    input_width,
    marker="*",
    color="limegreen",
    edgecolors="black",
    linewidths=1.5,
    s=450,
    label="Your Input",
    zorder=10
)

ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)

ax.set_title(
    f"{selected_algorithm}\nPredicted: {prediction}",
    fontsize=14
)

ax.legend()
ax.grid(alpha=0.2)

st.pyplot(fig)
plt.close(fig)


# =====================================
# 11. 품종 분류 이유 분석
# =====================================
st.divider()
st.subheader("🔍 왜 이 품종으로 분류했을까?")

st.write(
    "두 가지 입력 변수 중 어떤 변수가 예측에 "
    "더 많은 영향을 주었는지 분석합니다."
)

with st.spinner("변수 중요도를 분석하고 있습니다..."):

    importance = permutation_importance(
        model,
        X,
        y,
        n_repeats=10,
        random_state=42,
        scoring="accuracy"
    )

importance_df = pd.DataFrame({
    "측정 항목": ["꽃잎 길이", "꽃잎 너비"],
    "중요도": importance.importances_mean
})

importance_df = importance_df.sort_values(
    "중요도",
    ascending=False
)

st.bar_chart(
    importance_df.set_index("측정 항목"),
    horizontal=True
)

most_important = importance_df.iloc[0]["측정 항목"]

st.info(
    f"이번 분석에서 {most_important} 변수가 "
    "모델의 예측 정확도에 더 큰 영향을 주었습니다. "
    "이는 해당 변수를 섞었을 때 정확도가 얼마나 "
    "감소하는지를 이용한 분석입니다."
)

st.caption(
    "변수 중요도는 전체 데이터에서 측정한 값이며, "
    "개별 입력값의 예측 원인을 완전히 설명하는 것은 아닙니다."
)


# =====================================
# 12. 입력 데이터 확인
# =====================================
st.divider()
st.subheader("📝 나의 입력 데이터")

st.write(f"꽃잎 길이: {input_length:.1f} cm")
st.write(f"꽃잎 너비: {input_width:.1f} cm")
st.write(f"선택한 알고리즘: {selected_algorithm}")
st.write(f"예측 품종: {prediction}")

with st.expander("학습 데이터 전체 보기"):
    st.dataframe(df, use_container_width=True)

st.caption(
    "🌸 Iris AI Classification | "
    "Pandas + Scikit-learn + Streamlit"
)
