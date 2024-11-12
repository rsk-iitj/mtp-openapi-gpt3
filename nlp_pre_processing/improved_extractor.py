import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, load_metric


# Load and preprocess the dataset
def prepare_data():
    # Assume the dataset is in CSV format with "text" and "label" columns
    dataset = load_dataset('csv', data_files={'train': 'train.csv', 'test': 'test.csv'})

    # Define a tokenizer for preprocessing
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Tokenize and encode the dataset
    def tokenize(batch):
        return tokenizer(batch['text'], padding=True, truncation=True, max_length=512)

    tokenized_datasets = dataset.map(tokenize, batched=True)
    return tokenized_datasets


# Load the dataset
dataset = prepare_data()

# Load a pre-trained BERT model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',  # output directory
    num_train_epochs=3,  # number of training epochs
    per_device_train_batch_size=8,  # batch size for training
    per_device_eval_batch_size=8,  # batch size for evaluation
    warmup_steps=500,  # number of warmup steps for learning rate scheduler
    weight_decay=0.01,  # strength of weight decay
    logging_dir='./logs',  # directory for storing logs
    evaluation_strategy="epoch"  # evaluate at the end of each epoch
)

# Define a metric for evaluation
accuracy = load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.argmax(logits, dim=-1)
    return accuracy.compute(predictions=predictions, references=labels)


# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['test'],
    compute_metrics=compute_metrics
)

# Train the model
trainer.train()

# Evaluate the model
eval_results = trainer.evaluate()
print("Evaluation Results:", eval_results)

# Save the fine-tuned model
model.save_pretrained("requirement_extraction_model")
tokenizer.save_pretrained("requirement_extraction_tokenizer")
