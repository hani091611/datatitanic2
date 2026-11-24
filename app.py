
# ===== 1. 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px


# ===== 2. 페이지 설정 =====
st.set_page_config(
    page_title="Titanic 대시보드",
    layout="wide"
)


# ===== 3. 데이터 불러오기 =====
@st.cache_data
def load_data():
    # titanic.csv 파일을 읽고 캐시에 저장
    return pd.read_csv("titanic.csv")

df = load_data()


# ===== 4. 데이터 필터링 함수 =====
def filter_data(df, sexes, classes, age_range):

    # 성별 조건 적용
    filtered = df[df["sex"].isin(sexes)]

    # 객실 등급 조건 적용
    filtered = filtered[filtered["pclass"].isin(classes)]

    # 나이 범위 조건 적용
    min_age, max_age = age_range

    # 전체 범위(0~80)이면 나이 결측치도 포함  # [수정]
    if min_age == 0 and max_age == 80:  # [수정]
        filtered = filtered[  # [수정]
            filtered["age"].between(0, 80) | filtered["age"].isna()  # [수정]
        ]  # [수정]
    else:  # [수정]
        filtered = filtered[  # [수정]
            (filtered["age"] >= min_age) &  # [수정]
            (filtered["age"] <= max_age)  # [수정]
        ]  # [수정]

    # 세 조건을 모두 만족하는 데이터 반환
    return filtered


# ===== 5. KPI 계산 함수 =====
def kpi(df):

    # 데이터가 비어 있으면 0, 0, 0 반환
    if df.empty:
        return 0, 0, 0

    # 전체 승객 수 계산
    passenger_count = len(df)

    # 생존율 계산 및 소수 첫째 자리 반올림
    survival_rate = round(df["survived"].mean() * 100, 1)

    # 평균 나이 계산 및 소수 첫째 자리 반올림
    average_age = round(df["age"].mean(), 1)

    # 세 가지 KPI 반환
    return passenger_count, survival_rate, average_age


# ===== 6. 객실 등급별 생존율 그래프 함수 =====
def class_rate_bar(df):

    # 객실 등급별 생존율 계산
    rate = df.groupby("pclass")["survived"].mean().reset_index()

    # 생존율을 백분율로 변환
    rate["survived"] = rate["survived"] * 100

    # 막대그래프 생성
    fig = px.bar(
        rate,
        x="pclass",
        y="survived",
        text=rate["survived"].round(1),
        title="객실 등급별 생존율",
        labels={
            "pclass": "객실 등급",
            "survived": "생존율(%)"
        }
    )

    # 막대 위에 생존율 값 표시
    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside"
    )

    # 그래프 반환
    return fig


# ===== 7. 생존 여부별 나이 히스토그램 함수 =====
def age_hist(df):

    # 나이 히스토그램 생성 및 생존 여부별 색상 구분
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 승객 나이 분포",
        labels={
            "age": "나이(세)",
            "survived": "생존 여부"
        },
        color_discrete_map={
            0: "tomato",
            1: "royalblue"
        }
    )

    # 범례 이름을 한글로 변경
    fig.for_each_trace(
        lambda trace: trace.update(
            name="생존" if trace.name == "1" else "사망"
        )
    )

    # 그래프 반환
    return fig


# ===== 8. 대시보드 제목 =====
st.title("타이타닉, 누가 살아남았나?")


# ===== 9. 사이드바 필터 =====
st.sidebar.header("승객 필터")

# 성별 선택
sexes = st.sidebar.multiselect(
    "성별",
    options=["male", "female"],
    default=["male", "female"],
    format_func=lambda x: "남성" if x == "male" else "여성"
)

# 객실 등급 선택
classes = st.sidebar.multiselect(
    "객실 등급",
    options=[1, 2, 3],
    default=[1, 2, 3]
)

# 나이 범위 선택
age_range = st.sidebar.slider(
    "나이 범위",
    min_value=0,
    max_value=80,
    value=(0, 80)
)


# ===== 10. 필터 선택 여부 확인 [수정] =====

# 성별 또는 객실 등급을 선택하지 않은 경우 확인  # [수정]
if not sexes or not classes:  # [수정]
    st.warning("성별과 객실 등급을 하나 이상 선택해주세요.")  # [수정]
    st.stop()  # [수정]


# ===== 11. 데이터 필터링 =====
filtered_df = filter_data(
    df,
    sexes,
    classes,
    age_range
)


# ===== 12. 필터 결과 확인 [수정] =====

# 필터 결과가 0명인지 확인  # [수정]
if filtered_df.empty:  # [수정]
    st.warning("조건에 맞는 승객이 없습니다.")  # [수정]
    st.stop()  # [수정]


# ===== 13. KPI 숫자 카드 =====

# KPI 함수로 세 가지 지표 계산
passenger_count, survival_rate, average_age = kpi(filtered_df)

# 화면을 3개의 열로 나누기
col1, col2, col3 = st.columns(3)

# 첫 번째 카드: 승객 수
col1.metric("승객 수(명)", f"{passenger_count:,}")

# 두 번째 카드: 생존율
col2.metric("생존율(%)", f"{survival_rate:.1f}%")

# 세 번째 카드: 평균 나이
col3.metric("평균 나이(세)", f"{average_age:.1f}")


# ===== 14. 차트 2개 나란히 표시 =====

# 화면을 좌우 2개 영역으로 나누기
chart_col1, chart_col2 = st.columns(2)

# 왼쪽: 객실 등급별 생존율 막대그래프
with chart_col1:
    st.plotly_chart(
        class_rate_bar(filtered_df),
        use_container_width=True
    )

# 오른쪽: 생존 여부별 나이 히스토그램
with chart_col2:
    st.plotly_chart(
        age_hist(filtered_df),
        use_container_width=True
    )


# ===== 15. 데이터 보기 =====

# 접을 수 있는 데이터 영역 생성
with st.expander("데이터보기"):

    # 필터링된 데이터 표 표시
    st.dataframe(
        filtered_df,
        use_container_width=True
    )
