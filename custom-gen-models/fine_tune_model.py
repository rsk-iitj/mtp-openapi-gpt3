import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from datasets import load_dataset, Dataset
import pandas as pd


# Step 1: Load and Preprocess Dataset from CSV
def load_data_from_csv(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Convert to Hugging Face Dataset
    dataset = Dataset.from_pandas(df)

    # Ensure columns are named correctly for input and target text
    dataset = dataset.rename_column("input_text", "input_text")
    dataset = dataset.rename_column("target_text", "target_text")

    return dataset


# Step 2: Load Pretrained Model and Tokenizer
model_name = "t5-small"  # Use a lightweight model for efficiency
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


# Step 3: Tokenize Dataset
def tokenize(batch):
    # Tokenize input and target text
    input_encodings = tokenizer(batch["input_text"], padding="max_length", truncation=True, max_length=512)
    target_encodings = tokenizer(batch["target_text"], padding="max_length", truncation=True, max_length=128)

    # Set up labels for training, replacing padding token ID with -100
    labels = target_encodings["input_ids"]
    labels = [[(label if label != tokenizer.pad_token_id else -100) for label in label_list] for label_list in labels]
    input_encodings["labels"] = labels
    return input_encodings


# Load and preprocess dataset
file_path = "path/to/your/dataset.csv"  # Update this with your CSV file path
dataset = load_data_from_csv(file_path)
tokenized_dataset = dataset.map(tokenize, batched=True)

# Step 4: Set up Training Arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=5,  # Increase epochs if the dataset is small
    weight_decay=0.01,
    save_total_limit=3,
    logging_dir='./logs',
    logging_steps=10,
)

# Step 5: Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,  # Ideally use a separate validation dataset
)

# Step 6: Train the Model
trainer.train()

# Step 7: Save the Fine-tuned Model
trainer.save_model("./fine-tuned-t5")


# Step 8: Evaluation Function (Example for Testing)
def generate_test_plan_section(text):
    input_ids = tokenizer("generate: " + text, return_tensors="pt", max_length=512, truncation=True).input_ids
    outputs = model.generate(input_ids)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# Example usage
sample_text = "Your requirement text here..."
print("Generated Test Plan Section:", generate_test_plan_section(sample_text))
