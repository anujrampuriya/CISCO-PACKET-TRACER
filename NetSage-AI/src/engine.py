import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI
from src.checker import check_case

# Connect to Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")

client = None

if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN
    )

def load_cases():
    return pd.read_csv("data/cases.csv")


def build_diagnosis_input(case):
    rule_result = check_case(case)

    return {
        "case_id": case["case_id"],
        "symptom": case["symptom"],
        "topology": case["topology_note"],
        "show_outputs": case["show_outputs"],
        "osi_layer": case["osi_layer"],
        "concept": case["concept_tag"],
        "severity": case["severity"],
        "rule_checker": rule_result
    }

def diagnose_with_ai(case):

    data = build_diagnosis_input(case)

    # Load the project prompt
    with open("prompts/diagnose_prompt.md", "r", encoding="utf-8") as file:
        prompt_template = file.read()

    # Combine prompt + case information
    prompt = f"""
{prompt_template}

Case data:
{json.dumps(data, indent=2)}
"""

    # Check Hugging Face API credentials before making the request


    if client is None:
        return {
            "status": "AI_UNAVAILABLE",
            "error": "Hugging Face API token is not configured.",
            "root_cause": "",
            "osi_layer": data["osi_layer"],
            "confidence": "Unavailable",
            "evidence": [],
            "next_command": "",
            "fix_steps": []
        }

    try:
        # Ask Hugging Face for structured JSON
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Hugging Face returned an empty response.")

        result = json.loads(content)

        # Validate the expected AI response structure
        required_fields = [
            "root_cause",
            "osi_layer",
            "confidence",
            "evidence",
            "next_command",
            "fix_steps"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in result
        ]

        if missing_fields:
            return {
                "status": "AI_INVALID_RESPONSE",
                "error": (
                    "AI response is missing required fields: "
                    + ", ".join(missing_fields)
                ),
                "root_cause": "",
                "osi_layer": data["osi_layer"],
                "confidence": "Unavailable",
                "evidence": [],
                "next_command": "",
                "fix_steps": []
            }

        # Mark successful AI diagnosis
        result["status"] = "AI_DIAGNOSIS_SUCCESS"

        return result

    except json.JSONDecodeError:
        return {
            "status": "AI_INVALID_RESPONSE",
            "error": "Hugging Face returned a response that was not valid JSON.",
            "root_cause": "",
            "osi_layer": data["osi_layer"],
            "confidence": "Unavailable",
            "evidence": [],
            "next_command": "",
            "fix_steps": []
        }

    except Exception as e:
        return {
            "status": "AI_UNAVAILABLE",
            "error": f"Hugging Face API request failed: {str(e)}",
            "root_cause": "",
            "osi_layer": data["osi_layer"],
            "confidence": "Unavailable",
            "evidence": [],
            "next_command": "",
            "fix_steps": []
        }



if __name__ == "__main__":

    df = load_cases()

    # Test with NET-001 only
    case = df[df["case_id"] == "NET-001"].iloc[0].to_dict()

    result = diagnose_with_ai(case)

    print(json.dumps(result, indent=2))