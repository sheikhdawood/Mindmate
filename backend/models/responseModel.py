from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch
import re

class ResponseModel:
    def __init__(self):
        self.model_name = "facebook/blenderbot-400M-distill"
        self.tokenizer = BlenderbotTokenizer.from_pretrained(self.model_name)
        self.model = BlenderbotForConditionalGeneration.from_pretrained(self.model_name)

    def detect_crisis(self, text: str) -> bool:
        """Detects words or patterns indicating severe distress or suicidal intent."""
        crisis_keywords = [
            "suicide", "kill myself", "end my life", "worthless", 
            "hopeless", "want to die", "self harm", "cut myself"
        ]
        pattern = re.compile("|".join(crisis_keywords), re.IGNORECASE)
        return bool(pattern.search(text))

    def coping_suggestions(self, emotion: str) -> str:
        """Provides self-help and motivational suggestions based on emotion."""
        suggestions = {
            "sadness": [
                "Try a short journaling session about what's been heavy on your heart.",
                "Spend a few minutes focusing on your breath — in slowly, out slowly.",
                "Remind yourself that it's okay to feel low sometimes; it always passes."
            ],
            "anger": [
                "Take a deep breath in for 4 seconds, hold for 4, exhale for 4 — repeat.",
                "Go for a short walk to clear your mind before responding to others.",
                "Try writing down what made you upset, then note one positive action."
            ],
            "joy": [
                "Write down three things you're grateful for right now.",
                "Share your good mood — send a kind message to a friend.",
                "Pause to savor the feeling — it's important to celebrate good moments."
            ],
            "optimism": [
                "Keep focusing on the bright side, but allow yourself rest too.",
                "Note one goal you can take action on today.",
                "Gratitude journaling amplifies optimism — give it a try tonight."
            ],
            "default": [
                "Take a few slow, deep breaths and observe how you feel.",
                "A 5-minute mindfulness pause can reset your mood.",
                "Small steps today can bring big changes tomorrow."
            ]
        }
        return "\n".join(suggestions.get(emotion, suggestions["default"]))

    def generate_reply(self, user_input, emotion):
        """Generate chatbot response with emotion tone, self-help, and crisis safety."""
        
        # Crisis detection
        if self.detect_crisis(user_input):
            crisis_message = (
                "It sounds like you're in a very difficult moment right now. 💛\n"
                "You are not alone — please reach out to someone right away.\n\n"
                "📞 **India:** AASRA Helpline — 91-9820466726\n"
                "📞 **USA:** National Suicide Prevention Lifeline — 988\n"
                "📞 **UK:** Samaritans — 116 123\n\n"
                "If you're in immediate danger, please contact your local emergency services."
            )
            return crisis_message

        # Emotion-based tone
        if emotion == "sadness":
            prefix = "You are a gentle listener offering comfort and reassurance: "
        elif emotion == "anger":
            prefix = "You are calm and understanding. Help the user regain peace: "
        elif emotion == "joy":
            prefix = "You are cheerful and kind. Celebrate their happiness: "
        elif emotion == "optimism":
            prefix = "You are encouraging and positive. Reinforce their hopeful outlook: "
        else:
            prefix = "You are supportive and mindful. Offer empathy and understanding: "
        
        # Generate empathetic message
        input_text = prefix + user_input
        inputs = self.tokenizer([input_text], return_tensors="pt")

        reply_ids = self.model.generate(
            **inputs,
            max_length=150,
            num_beams=5,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=self.tokenizer.eos_token_id
        )

        bot_reply = self.tokenizer.decode(reply_ids[0], skip_special_tokens=True).strip()
        
        # Add coping suggestions
        extra_help = self.coping_suggestions(emotion)
        
        return f"{bot_reply}\n\n💡 *Coping Tip:*\n{extra_help}"
