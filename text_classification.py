from transformers import pipeline

# Initialize the sentiment-analysis pipeline with a RoBERTa model
classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# Example text to classify
with open("transcribed_script.txt","r") as file:
    sentence=file.read()
# Perform sentiment analysis
result = classifier(sentence)



# %%
# Mapping from model output labels to sentiment categories
label_mapping = {
    'LABEL_0': 'Negative',
    'LABEL_1': 'Neutral',
    'LABEL_2': 'Positive'
}

# Extract the label from the output
predicted_label = result[0]['label']
predicted_score = result[0]['score']

# Map the label to its corresponding sentiment
sentiment = label_mapping.get(predicted_label, "Unknown label")

# Display the result
print(f"Sentiment: {sentiment}, Score: {predicted_score:.2f}")
# %%
