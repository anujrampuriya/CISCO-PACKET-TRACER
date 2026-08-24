import pandas as pd
from src.checker import check_case
from src.engine import diagnose_with_ai


CSV_PATH = "data/cases.csv"

# Representative cases for AI testing.
# These cover different network fault categories.
AI_TEST_CASES = [
    "NET-001",
    "NET-004",
    "NET-005",
    "NET-006",
    "NET-008",
    "NET-015",
    "NET-023",
]


def run_deterministic_tests(df):
    print("\n" + "=" * 70)
    print("DETERMINISTIC RULE ENGINE TEST")
    print("=" * 70)

    passed = 0

    for _, row in df.iterrows():
        case = row.to_dict()
        result = check_case(case)

        if result["status"] == "ERRORS_DETECTED":
            status = "PASS"
            passed += 1
        else:
            status = "NO FINDING"

        rules = ", ".join(
            finding["rule_id"]
            for finding in result["findings"]
        )

        print(
            f"{case['case_id']} | "
            f"{status:<11} | "
            f"Expected: {case['expected_fault']} | "
            f"Rules: {rules or 'None'}"
        )

    print("-" * 70)
    print(f"Deterministic cases with findings: {passed}/{len(df)}")

    return passed


def run_ai_tests(df):
    print("\n" + "=" * 70)
    print("HUGGING FACE AI DIAGNOSTIC ACCURACY TEST")
    print("=" * 70)

    ai_cases = df[df["case_id"].isin(AI_TEST_CASES)]

    successful_calls = 0
    accurate_cases = 0

    for _, row in ai_cases.iterrows():
        case = row.to_dict()

        print(f"\nTesting {case['case_id']}...")
        print(f"Expected fault: {case['expected_fault']}")

        try:
            result = diagnose_with_ai(case)

            # Required structured fields from the AI engine
            required_fields = [
                "root_cause",
                "osi_layer",
                "confidence",
                "evidence",
                "next_command",
                "fix_steps",
            ]

            missing = [
                field
                for field in required_fields
                if field not in result
            ]

            if missing:
                print(f"Result: FAIL - Missing fields: {missing}")
                continue

            successful_calls += 1

            root_cause = str(
                result.get("root_cause", "")
            ).lower()

            expected_fault = str(
                case["expected_fault"]
            ).lower()

            # Break expected fault into meaningful words.
            expected_words = [
                word.strip(".,:-()/")
                for word in expected_fault.split()
                if len(word.strip(".,:-()/")) >= 4
            ]

            # Find expected-fault terms present in the AI root cause.
            matches = [
                word
                for word in expected_words
                if word in root_cause
            ]

            match_ratio = (
                len(matches) / len(expected_words)
                if expected_words
                else 0
            )

            # Lightweight lexical accuracy check.
            # This is not a semantic evaluator.
            if match_ratio >= 0.40:
                print("Accuracy result: PASS")
                accurate_cases += 1
            else:
                print("Accuracy result: REVIEW")

            print(f"AI root cause: {result['root_cause']}")
            print(f"AI confidence: {result['confidence']}")
            print(f"Matched expected terms: {matches}")

        except Exception as e:
            print("Result: FAIL")
            print(f"Error: {e}")

    print("\n" + "-" * 70)
    print(f"Successful AI calls: {successful_calls}/{len(ai_cases)}")
    print(f"AI diagnosis matches: {accurate_cases}/{len(ai_cases)}")

    if len(ai_cases) > 0:
        accuracy = (accurate_cases / len(ai_cases)) * 100
        print(f"Estimated AI diagnostic accuracy: {accuracy:.1f}%")

    return successful_calls, accurate_cases


def main():
    print("\nNetSage AI - Automated Test Runner")

    df = pd.read_csv(CSV_PATH)

    print(f"Total cases loaded: {len(df)}")

    deterministic_passed = run_deterministic_tests(df)

    ai_successful, ai_accurate = run_ai_tests(df)

    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)

    print(
        f"Deterministic Engine: "
        f"{deterministic_passed}/{len(df)} cases produced findings"
    )

    print(
        f"AI Engine: "
        f"{ai_successful}/{len(AI_TEST_CASES)} successful API calls"
    )

    print(
        f"AI Accuracy: "
        f"{ai_accurate}/{len(AI_TEST_CASES)} cases matched expected faults"
    )

    if len(AI_TEST_CASES) > 0:
        accuracy = (
            ai_accurate / len(AI_TEST_CASES)
        ) * 100

        print(
            f"Estimated AI diagnostic accuracy: "
            f"{accuracy:.1f}%"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()