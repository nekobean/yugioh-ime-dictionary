import argparse
import csv
import re
from pathlib import Path

CARD_LIST = Path(__file__).parent / "data/card_20250316.csv"
CATEGORY_LIST = Path(__file__).parent / "data/category_20250316.csv"
EXCLUDE_CATEGORY_LIST = Path(__file__).parent / "data/exclude_category.txt"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", default=CARD_LIST)
    parser.add_argument("--category", default=CATEGORY_LIST)
    parser.add_argument("--prefix", action="store_true", default=False)
    parser.add_argument("--exclude-category", action="store_true", default=True)
    return parser.parse_args()


def is_text_alphabet(text):
    return bool(re.match(r"^[,'\-A-Za-z]+$", text))


def create_dict(card_list, category_list, exclude_category):
    with open(card_list, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cards = list(reader)

    with open(category_list, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        categories = list(reader)

    with open(EXCLUDE_CATEGORY_LIST, "r", encoding="utf-8") as f:
        exclude_categories = f.read().splitlines()

    # 英語のみのデータを除外
    cards = [card for card in cards if not is_text_alphabet(card["ruby"])]

    data = []
    for card in cards:
        data.append(
            {
                "name": card["name"],
                "ruby": card["ruby"],
            }
        )
    print(len(data))

    for category in categories:
        if exclude_category and category["ruby"] in exclude_categories:
            continue  # 辞書から除外カテゴリ （「しん」などの一般用語を登録しない）

        for card in cards:
            if category["name"] in card["name"]:
                data.append(
                    {
                        "name": card["name"],
                        "ruby": category["ruby"],
                    }
                )

    print(f"number of words: {len(data)}")

    return data


def write_google_dict(data, prefix):
    output_path = Path(__file__).parent / "data" / "yugioh_google_ime.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for row in data:
            ruby = ("＠" if prefix else "") + row["ruby"]
            line = "\t".join([ruby, row["name"], "固有名詞", ""])
            f.write(f"{line}\n")


def write_ms_dict(data, prefix):
    output_path = Path(__file__).parent / "data" / "yugioh_ms_ime.txt"
    with open(output_path, "w", encoding="utf-16") as f:
        for row in data:
            ruby = ("＠" if prefix else "") + row["ruby"]
            line = "\t".join([ruby, row["name"], "固有名詞"])
            f.write(f"{line}\r\n")

    print(f"Output to {output_path}")


def main(prefix, card_list, category_list, exclude_category):
    print(f"Card list: {card_list}")
    print(f"Category list: {category_list}")

    data = create_dict(card_list, category_list, exclude_category)

    write_google_dict(data, prefix)
    write_ms_dict(data, prefix)


if __name__ == "__main__":
    args = parse_args()
    main(args.prefix, args.card, args.category, args.exclude_category)
