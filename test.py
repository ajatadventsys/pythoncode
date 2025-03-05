import os
import json
import pdfplumber
import requests # type: ignore

# PDF File Path
pdf_path = r"C:\Users\admin\Downloads\LabSolutions.pdf"

# Output Directory
output_pdf_path = r"C:\Users\admin\Downloads\Response"
os.makedirs(output_pdf_path, exist_ok=True)

# API Key & URL
API_KEY = ""
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def extract_text(pdf_path):
    """Extract text from a PDF and return as a string."""
    extracted_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text.strip())

    return "\n\n".join(extracted_text)  # Efficient string joining

# Extract text from PDF
extracted_text = extract_text(pdf_path)

# List of different prompts
prompts = [
    ("First", "URS from User Manual/Guide:", "You are an expert in Computer System Validation (CSV). Analyze the provided User Manual and extract all testable user requirements for the 'Biovia ELN' project.\n\n#### **Key Instructions:**\n1. Extract only testable requirements. If a requirement cannot be tested, do not include it.\n2. Each requirement must have a **unique URS ID** in sequential order (URS-001, URS-002, etc.).\n3. Each requirement must start with 'system shall' and must be:\n   - **Concise** (≤150 characters) but detailed enough for testing.\n   - **Categorized** under one of: [Business Functional Requirements, Security Requirements, Configuration Requirements, Technical Requirements, Regulatory Requirements, Documentation Requirements, Report/Output Requirements, Error Handling/Alarm Requirements, Data Requirements, Operational Requirements].\n4. Elaborate requirements from the document, ensuring clarity and specificity.\n\n#### **Output Format (Strictly in JSON)**\n[\n  { \"URS ID\": \"URS-XXX\", \"Requirement\": \"<detailed requirement>\", \"Category\": \"<category>\" }\n]"),
    ("Second", "Specification from Above URS:", "For each of the user requirements extracted in **1.1 URS**, generate a **Functional Design Specification (FDS)** or **Functional Configuration Specification (FCS)** as applicable. \n\n#### **Key Instructions:**\n1. Each **requirement** from the **URS list** should be mapped to one or more **functional specifications**.\n2. Requirements may be **merged** into a single specification **or** a single requirement may be **split into multiple specifications** if applicable.\n3. Each specification must include:\n   - The original **Requirement** from the URS.\n   - A **Specification Type**: Either `Functional Design Specification` or `Functional Configuration Specification`.\n   - A **unique Specification ID** (`SPEC-001`, `SPEC-002`, etc.).\n   - A **detailed Specification** (≤ 250 characters) describing how the requirement will be met.\n   - A **Category** aligned with the URS category.\n4. **Ensure consistency**: The same URS input should always generate the same number of specifications.\n5. **Output Format (Strictly in JSON)**:"),
    ("Third", "Risk from Above URS:", "Based on the given user requirements, generate a **Risk Assessment** following the **FMEA (Failure Modes and Effects Analysis) model**.\n\n#### **Instructions:**\n1. Use a **5x5 risk matrix** for scoring:  - **Probability of Occurrence (P)**: Scale 1-5 (1 = Low, 5 = High).  - **Severity (S)**: Scale 1-5 (1 = Low, 5 = High).  - **Detectability (D)**: Scale 1-5 (1 = Easy to detect, 5 = Hard to detect).  2. Each **identified risk** should include:\n   \n   - **Risk Description**: A concise description of the risk.\n   - **Probable Cause**: The probable cause of the risk.\n   - **Probability of Occurrence (P)**.\n   - **Severity (S)**.\n   - **Detectability (D)**.\n   - **Risk Priority Number (RPN)** = P × S × D.\n   - **Recommended Mitigation**: A strategy to mitigate the risk.\n3. **Ensure consistency**: The same URS input should always generate the same risks and RPN scores.\n4. **Output Format (Strictly in JSON):**\n\n```json\n[\n  {\n    \"requirement\": \"<URS requirement>\",\n    \"risk_id\": \"RISK-001\",\n    \"riskScenario\": \"<Concise risk description>\",\n    \"probableCauseOfRisk\": \"<Probable cause>\",\n    \"probabilityOfOccurance\": <1-5>,\n    \"severity\": <1-5>,\n    \"detectability\": <1-5>,\n    \"rpn\": <P*S*D>,\n    \"proposedMitigation\": \"<Mitigation strategy>\"\n  },\n  {\n    \"requirement\": \"<URS requirement>\",\n    \"risk_id\": \"RISK-002\",\n    \"riskScenario\": \"<Concise risk description>\",\n    \"probableCauseOfRisk\": \"<Probable cause>\",\n    \"probabilityOfOccurance\": <1-5>,\n    \"severity\": <1-5>,\n    \"detectability\": <1-5>,\n    \"rpn\": <P*S*D>,\n    \"proposedMitigation\": \"<Mitigation strategy>\"\n  }\n]\n```\n\n#### **URS List:**\n\n\n   - A **Category** aligned with the URS category.\n4. **Ensure consistency**: The same URS input should always generate the same number of specifications.\n5. **Output Format (Strictly in JSON)**:"),
    ("Fourth", "Test Case from Above URS:", "Based on the given user requirements, generate **one or more test cases** for each requirement. Each test case should be classified as either **Installation Qualification (IQ)** or **Operational Qualification (OQ)**.\n\n#### **Instructions:**\n1. **Each test case must include the following fields:**\n   - **Requirement**: The original requirement description.\n   - **Test Case Type**: Either `IQ` (Installation Qualification) or `OQ` (Operational Qualification).\n   - **Test Case ID**: Format - `IQ-001`, `OQ-001`, `IQ-002`, `OQ-002`, etc.\n   - **Objective**: The objective of the test case.\n   - **Test Description**: A concise description of the test case.\n   - **Pre-requisites**: `NA` if not applicable.\n   - **Acceptance Criteria**: `NA` if not applicable.\n   - **Expected Result**: A concise expected outcome of the test case.\n   - **Checklist**: One or more test steps with concise `instruction` and `expected result`.\n\n2. **Output Format (Strictly in JSON):**\n\n```json\n[\n  {\n    \"requirement\": \"<URS requirement>\",\n    \"testcaseType\": \"<IQ | OQ>\",\n    \"testcaseID\": \"IQ-001\",\n    \"objective\": \"<Objective of test case>\",\n    \"description\": \"<Concise test case description>\",\n    \"preRequisites\": \"<NA | Required setup>\",\n    \"acceptanceCriteria\": \"<NA | Acceptance criteria>\",\n    \"expectedResult\": \"<Expected outcome>\",\n    \"checklist\": [\n      {\n        \"checklistName\": \"<Step 1>\",\n        \"expectedResult\": \"<Expected outcome of step 1>\"\n      },\n      {\n        \"checklistName\": \"<Step 2>\",\n        \"expectedResult\": \"<Expected outcome of step 2>\"\n      }\n    ]\n  },\n  {\n    \"requirement\": \"<URS requirement>\",\n    \"testcaseType\": \"<IQ | OQ>\",\n    \"testcaseID\": \"OQ-001\",\n    \"objective\": \"<Objective of test case>\",\n    \"description\": \"<Concise test case description>\",\n    \"preRequisites\": \"<NA | Required setup>\",\n    \"acceptanceCriteria\": \"<NA | Acceptance criteria>\",\n    \"expectedResult\": \"<Expected outcome>\",\n    \"checklist\": [\n      {\n        \"checklistName\": \"<Step 1>\",\n        \"expectedResult\": \"<Expected outcome of step 1>\"\n      }\n    ]\n  }\n]\n```\n\n#### **URS List:**\n\n   - A **Category** aligned with the URS category.\n4. **Ensure consistency**: The same URS input should always generate the same number of specifications.\n5. **Output Format (Strictly in JSON)**:"),
]

# Use a session for efficiency
with requests.Session() as session:
    first_response_data = None  # To store first response

    for index, (file_name, heading, prompt_detail) in enumerate(prompts, start=1):
        # Construct request body
        if file_name == "First":
            input_text = extracted_text  # Initial input from PDF
        else:
            input_text = first_response_data  # Use First response

        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                f"### 1.{index}. {heading}\n\n"
                                f"#### **Key Task:** {prompt_detail}\n\n"
                                + json.dumps(input_text, indent=4)  # Pass extracted text or previous response
                            )
                        }
                    ]
                }
            ]
        }

        # Send request
        response = session.post(API_URL, json=request_body)

        # Parse response
        try:
            response_json = response.json()
            output_file_path = os.path.join(output_pdf_path, f"{file_name}.json")

            # Save response as JSON
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(response_json, f, indent=4, ensure_ascii=False)

            print(f"Response saved to: {output_file_path}")

            # Store first response for subsequent requests
            if file_name == "First":
                first_response_data = response_json  # Store First.json content
        except Exception as e:
            print(f"Error saving response for {file_name}: {e}")
