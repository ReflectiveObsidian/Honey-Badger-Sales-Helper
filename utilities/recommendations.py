# Takes in emotion and personality data and returns a recommendation

emotion_recommendations = {
    "admiration": "Focus on what can be achieved with the product",
    "amusement": "Focus on fun aspects of product",
    "anger": "Recommend something else or apologise & hang up",
    "annoyance": "Recommend something else or apologise & hang up",
    "approval": "Focus on advantages against competition",
    "caring": "Focus on benefits of product",
    "confusion": "Elaborate clearly or recommend something else",
    "curiosity": "Focus on what can be achieved with the product",
    "desire": "Focus on how product can meet their needs",
    "disappointment": "Recommend something else",
    "disapproval": "Recommend something else or apologise & hang up",
    "disgust": "Recommend something else or apologise & hang up",
    "embarrassment": "Recommend something else",
    "excitement": "Focus on fun aspects of product",
    "fear": "Recommend something else",
    "gratitude": "Discuss pricing & worth of product",
    "grief": "Apologize and hang up",
    "joy": "Focus on fun aspects of product",
    "love": "Discuss pricing & worth of product",
    "nervousness": "Build a relationship with the customer & elaborate clearly",
    "neutral": "Ask them to respecify their needs",
    "optimism": "Focus on advantages against competition",
    "pride": "Recommend a higher tier of product",
    "realization": "Elaborate on product's unique features",
    "relief": "Focus on how product can meet their needs",
    "remorse": "Apologize and hang up",
    "sadness": "Apologize and hang up",
    "surprise": "Focus on niche purposes of product"
}

personality_recommendations = {
    "INTJ": "Product's effectiveness, Product reliability, Big picture, No emotional appeal",
    "INTP": "Product's innovation, Logical reasonings, Intellectual discussions, No pressure to buy",
    "ENTJ": "Product's competitive advantage & efficiency, Present assertively, Explain product's potential results + ROI",
    "ENTP": "Product's innovation + creative applications, Product's adaptibility, Be energetic",
    "INFJ": "Product's alignment with personal values + mission, benefits to society, Empathize & build personal connection",
    "INFP": "Product's fulfillment of dreams & aspirations, Appeal emotionally by telling stories, No technicalities, No pressure to buy",
    "ENFJ": "Product's benefit to relationship & community, Be warm and enthusiastic, Practicality",
    "ENFP": "Product's innovation and creative potential, Be energetic, Appeal to Values and Fun",
    "ISTJ": "Product's reliability and efficiency + Proven results with data, Be organized and professional",
    "ISFJ": "Product's practical benefits, Build personal connection, Be organized, clear and detailed",
    "ESTJ": "Product's efficiency + effectiveness, Proven results with data, Be direct and confident",
    "ESFJ": "Product's social and practical benefits, Be warm and genuine, Be organized, clear and detailed",
    "ISTP": "Product's practical benefits, Offer free trials, Be concise and direct",
    "ISFP": "Product's alignment with personal values + aesthetics, Build personal connection, Offer free trial",
    "ESTP": "Product's practical benefits + exciting features, Be energetic, concise and direct",
    "ESFP": "Product's enjoyability and social benefits, Be warm and enthusiastic, Offer free trial"
}


def get_recommendation(emotion: str, personality: str):
    if emotion not in emotion_recommendations:
        emotion_recommendation = "No recommendation available for this emotion: " + emotion
    else:
        emotion_recommendation = emotion_recommendations[emotion]
    
    if personality not in personality_recommendations:
        personality_recommendation = "No recommendation available for this personality: " + personality
    else:
        personality_recommendation = personality_recommendations[personality]
    
    return emotion_recommendation + "\n" + personality_recommendation