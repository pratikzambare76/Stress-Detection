from textblob import TextBlob

# Define 20 questions
questions = [
    "Do you often feel hopeless?",
    "Have you lost interest in things you used to enjoy?",
    "Do you have trouble sleeping or sleeping too much?",
    "Do you feel tired or have little energy most days?",
    "Do you feel worthless or guilty most of the time?",
    "Have you experienced significant weight loss or gain recently?",
    "Do you have trouble concentrating on tasks?",
    "Do you have thoughts of harming yourself?",
    "Do you feel like you're a burden to others?",
    "Do you have trouble making decisions?",
    "Do you feel anxious or on edge frequently?",
    "Do you cry more often than usual?",
    "Do you avoid social situations or people?",
    "Do you feel restless or agitated?",
    "Have you been feeling excessively angry or irritable?",
    "Do you think life is not worth living?",
    "Have you experienced drastic mood swings?",
    "Do you feel disconnected from reality?",
    "Do you feel persistent sadness or emptiness?",
    "Do you feel you lack purpose or meaning in life?"
]

# Function to analyze response
def analyze_responses(responses):
    scores = []
    for response in responses:
        blob = TextBlob(response)
        scores.append(blob.sentiment.polarity)  # Sentiment polarity ranges from -1 (negative) to 1 (positive)
    avg_score = sum(scores) / len(scores)

    # Determine tendency based on average sentiment score
    if avg_score < -0.2:  # Threshold for negative sentiment indicating potential suicide tendency
        return "High Risk"
    elif -0.2 <= avg_score <= 0.2:
        return "Moderate Risk"
    else:
        return "Low Risk"