import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

prompt = """
Create an educational 2D animation explaining Binary Search.

Show a sorted array:
[2, 5, 8, 12, 16, 23, 38]

Clearly show:
- low pointer
- high pointer
- mid pointer
- compare the target 23 with the middle value 12
- eliminate the left half
- move toward the next search range

Clean computer-science educational animation.
Dark background, clear labels, simple diagrams.
No humans, no cinematic scene, no unnecessary decoration.
The animation should visually demonstrate the algorithm step by step.
"""

print("Starting Veo generation...")
print("This may take some time.")

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

while not operation.done:
    print("Veo is generating...")
    time.sleep(10)
    operation = client.operations.get(operation)

print("Generation finished.")

if not operation.response:
    raise RuntimeError("Veo returned no response.")

generated_video = operation.response.generated_videos[0]

output = Path("binary_search_veo_test.mp4")

client.files.download(
    file=generated_video.video,
    destination=str(output),
)

print()
print("====================================")
print("VEO TEST SUCCESS")
print("====================================")
print(f"Video: {output.resolve()}")