from textblob import TextBlob

# Define 22 questions
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
    "Do you have loan?",
    "Do you have relationship issue?",
    "Do you feel anxious or on edge frequently?",
    "Do you cry more often than usual?",
    "Do you avoid social situations or people?",
    "Do you feel restless or agitated?",
    "Have you been feeling excessively angry or irritable?",
    "Do you think life is not worth living?",
    "Do you feel disconnected from reality?",
    "Do you feel you lack purpose or meaning in life?"
]

from textblob import TextBlob

def analyze_responses(responses):
    """
    Analyze yes/no responses and return a stress risk level.
    """
    yes_count = sum(1 for response in responses if 'yes' in response.lower())
    no_count = sum(1 for response in responses if 'no' in response.lower())

    # Decision logic
    if yes_count >= 6:
        return "High Risk"
    elif 3 <= yes_count < 6:
        return "Moderate Risk"
    else:
        return "Low Risk"

