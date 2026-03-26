import os, requests, time
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.environ["VISION_ENDPOINT"].rstrip("/")
KEY      = os.environ["VISION_KEY"]

def extract_text_from_image(image_path: str) -> str:
    url = f"{ENDPOINT}/documentintelligence/documentModels/prebuilt-read:analyze?api-version=2024-11-30"
    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as f:
        image_data = f.read()

    response = requests.post(url, headers=headers, data=image_data)
    response.raise_for_status()

    # Document Intelligence는 비동기라 결과를 polling해야 해요
    result_url = response.headers["Operation-Location"]
    for _ in range(10):
        time.sleep(2)
        result = requests.get(result_url, headers={"Ocp-Apim-Subscription-Key": KEY}).json()
        if result.get("status") == "succeeded":
            lines = []
            for page in result["analyzeResult"]["pages"]:
                for line in page.get("lines", []):
                    lines.append(line["content"])
            return "\n".join(lines)

    return ""