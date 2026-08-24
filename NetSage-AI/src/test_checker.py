import pandas as pd
from checker import check_case

df = pd.read_csv("data/cases.csv")

for _, case in df.iterrows():
    result = check_case(case.to_dict())

    print(
        case["case_id"],
        "→",
        result["status"],
        "→",
        [f["rule_id"] for f in result["findings"]]
    )