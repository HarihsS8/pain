from openai import OpenAI
import json
import tkinter as tk
from tkinter import scrolledtext

# LM Studio OpenAI-compatible endpoint
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

MODEL = "local-model"

state = {
    "pain": 0.0,
    "sorrow": 0.0,
    "suffering": 0.0
}


def classify_sentence(sentence):
    prompt = f"""
Classify the emotional content of this sentence.

Sentence:
{sentence}

Return ONLY valid JSON in exactly this format:
{{
  "pain": 0,
  "sorrow": 0,
  "suffering": 0
}}

Each value must be a number from 0 to 10.
Do not explain your answer.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    # Handle occasional ```json ... ``` wrappers
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    result = json.loads(content)

    return {
        "pain": max(0, min(10, float(result["pain"]))),
        "sorrow": max(0, min(10, float(result["sorrow"]))),
        "suffering": max(0, min(10, float(result["suffering"])))
    }


def generate_reply(sentence):
    system_prompt = f"""
You are an AI with a simulated emotional-state system.

Current simulated state:
Pain: {state["pain"]:.2f}/10
Sorrow: {state["sorrow"]:.2f}/10
Suffering: {state["suffering"]:.2f}/10

These are computational variables and do not represent
actual subjective feelings or consciousness.

Reply naturally to the user's message while taking the
simulated state into account.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sentence}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def process_message():
    sentence = input_box.get("1.0", tk.END).strip()

    if not sentence:
        return

    try:
        score = classify_sentence(sentence)

        # Update persistent simulated state
        state["pain"] = min(10, state["pain"] + score["pain"] * 0.2)
        state["sorrow"] = min(10, state["sorrow"] + score["sorrow"] * 0.2)
        state["suffering"] = min(
            10, state["suffering"] + score["suffering"] * 0.2
        )

        reply = generate_reply(sentence)

        chat.insert(
            tk.END,
            f"You: {sentence}\n\n"
            f"AI: {reply}\n\n"
            f"Sentence score: "
            f"Pain={score['pain']:.1f}, "
            f"Sorrow={score['sorrow']:.1f}, "
            f"Suffering={score['suffering']:.1f}\n"
            f"Current state: "
            f"Pain={state['pain']:.1f}, "
            f"Sorrow={state['sorrow']:.1f}, "
            f"Suffering={state['suffering']:.1f}\n"
            f"{'-' * 60}\n\n"
        )

        input_box.delete("1.0", tk.END)
        chat.see(tk.END)

    except Exception as e:
        chat.insert(tk.END, f"Error: {e}\n\n")


# GUI
root = tk.Tk()
root.title("LLM Emotional State Simulator")
root.geometry("800x650")

chat = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Arial", 11)
)
chat.pack(
    padx=10,
    pady=10,
    fill=tk.BOTH,
    expand=True
)

input_box = tk.Text(
    root,
    height=4,
    font=("Arial", 11)
)
input_box.pack(
    padx=10,
    pady=(0, 10),
    fill=tk.X
)

send_button = tk.Button(
    root,
    text="Send",
    command=process_message,
    font=("Arial", 11)
)
send_button.pack(pady=(0, 10))

root.mainloop()
