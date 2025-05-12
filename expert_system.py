import json


class GPUPredictor:
    def __init__(self, db_path="gpus.json"):
        with open(db_path, "r", encoding="utf-8") as f:
            self.cards = json.load(f)

        # Веса для каждого признака
        self.weights = {
            "manufacturer": 3.0,
            "architecture": 2.5,
            "performance": 2.0,
            "tdp": 1.0,
            "power": 1.0,
        }

    def score_match(self, input_data, card_data):
        score = 0.0
        for key in self.weights:
            if key in input_data and input_data[key] is not None:
                if str(input_data[key]).lower() == str(card_data[key]).lower():
                    score += self.weights[key]
        return score

    def predict(self, input_data, top_n=10):
        scored_cards = []
        for card in self.cards:
            score = self.score_match(input_data, card)
            if score > 0:
                scored_cards.append((card["card"], score))

        # Сортируем по убыванию очков
        scored_cards.sort(key=lambda x: x[1], reverse=True)
        return scored_cards[:top_n]


if __name__ == "__main__":
    predictor = GPUPredictor()

    sample_input = {
        "manufacturer": "NVIDIA",
        "tdp": None,
        "power": "250",
        "architecture": "Volta",
        "performance": "High",
    }

    results = predictor.predict(sample_input)
    print("Top 10 Matching GPUs:")
    for name, score in results:
        print(f"{name} - Score: {score:.1f}")
