import pandas as pd
import pickle
import random

# CSV 파일을 데이터프레임으로 읽기
df = pd.read_csv("word.cvs", header=None, names=["Index", "Value"])
print("Original DataFrame:")
print(df)

with open("words.pkl", "wb") as f:
    pickle.dump(df, f)

with open("words.pkl", "rb") as f:
    loaded_df = pickle.load(f)


# 데이터프레임의 행 수 확인
num_rows = len(loaded_df)

print(num_rows)

# 랜덤하게 10개의 행 인덱스 선택
random_indices = random.sample(range(num_rows), 10)

# 랜덤하게 선택된 행 가져오기
random_rows = loaded_df.iloc[random_indices]

# 두 번째 열을 스트링으로 합치기 (공백 문자로 구분)
result_string = " ".join(random_rows.iloc[:, 1])

print(result_string)
