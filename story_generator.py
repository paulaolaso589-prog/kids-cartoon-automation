"""Generate a reproducible, structured children's story episode.

Uses only Python's standard library; no paid AI API required.
"""
import argparse
import json
import random
from datetime import date
from pathlib import Path

CHARACTERS = [
    {"name": "Pip", "description": "a curious little orange fox"},
    {"name": "Mimi", "description": "a thoughtful little blue rabbit"},
]

ADVENTURES = [
    ("The Missing Rainbow", "the colors in their garden seem to have faded", "colors", "they plant bright flowers and discover the colors were hidden by morning mist"),
    ("The Little Lost Star", "a glowing paper star has blown away", "teamwork", "they follow its sparkling trail and return it to the lantern festival"),
    ("The Quiet Forest", "their bird friends have stopped singing", "listening", "they listen carefully and find the birds resting after a long journey"),
    ("The Bridge of Leaves", "a tiny stream blocks their path", "problem-solving", "they gather fallen leaves and safe stepping stones to make a crossing"),
    ("The Cloud That Needed a Friend", "a small cloud feels lonely", "kindness", "they invite the cloud to join their picnic and share stories"),
    ("The Garden Surprise", "their seedlings have not grown yet", "patience", "they water the garden and learn that growing takes time"),
]


def generate(episode_number: int) -> dict:
    if episode_number < 1:
        raise ValueError("Episode number must be positive")
    # Deterministic by episode number, with a finite set of story templates.
    rng = random.Random(episode_number)
    title, problem, lesson, resolution = ADVENTURES[(episode_number - 1) % len(ADVENTURES)]
    location = rng.choice(["sunny meadow", "whispering forest", "flower-filled garden"])
    lines = [
        f"On a beautiful morning in the {location}, Pip the fox and Mimi the rabbit set out for an adventure.",
        f"Something unusual happened: {problem}.",
        '"What should we do?" asked Pip. "Let us think together," said Mimi.',
        f"They took their time, helped each other, and soon {resolution}.",
        f'"We did it together!" cheered Pip. Mimi smiled. "Today we learned about {lesson}."',
        "The friends waved goodbye, excited for their next adventure.",
    ]
    return {
        "episode_number": episode_number,
        "title": title,
        "language": "en-US",
        "audience": "children ages 4-7",
        "made_for_kids": True,
        "characters": CHARACTERS,
        "lesson": lesson,
        "scenes": [{"scene_number": i, "narration": line} for i, line in enumerate(lines, 1)],
        "disclaimer": "Template-generated story; review for originality and suitability before publishing.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", type=int, default=1)
    parser.add_argument("--output", default="output/episode.json")
    args = parser.parse_args()
    result = generate(args.episode)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {path}: {result['title']}")


if __name__ == "__main__":
    main()
