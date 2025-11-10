from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class EmotionModel:
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-emotion"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ['anger', 'joy', 'optimism', 'sadness']

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        label_id = torch.argmax(probs, dim=1).item()
        return self.labels[label_id]
