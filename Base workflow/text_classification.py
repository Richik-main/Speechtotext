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
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

# Step 1: Load and process the image
image_path = "/Users/richikghosh/Documents/GitHub/Speechtotext/dog.jpeg"
image = Image.open(image_path)
#%%
# Step 2: Initialize the CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

#%%

# Define candidate labels
labels = ["a cat", "a dog", "a car", "a tree", "a yeti"]
# Step 3: Encode the image and some candidate texts
inputs = processor(text=labels, images=image, return_tensors="pt", padding=True)
outputs = model(**inputs)

# Step 4: Get the logits (higher is better) for each text
logits_per_image = outputs.logits_per_image
best_match_index = logits_per_image.argmax()  # Get the index of the highest score
predicted_label = labels[best_match_index]  # Find the corresponding label


#%%
# Step 5: Determine the classification
print(f"The image is classified as: {predicted_label}")

# %%
