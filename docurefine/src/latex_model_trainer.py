import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from datasets import load_dataset

def prepare_dataset(dataset):
    tokenizer = T5Tokenizer.from_pretrained("t5-base")

    def tokenize_function(examples):
        inputs = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(examples["latex"], padding="max_length", truncation=True, max_length=512)
        return {
            "input_ids": inputs.input_ids,
            "attention_mask": inputs.attention_mask,
            "labels": labels.input_ids,
        }

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    return tokenized_datasets

def train_latex_model(dataset_path, output_dir):
    # Load and prepare the dataset
    dataset = load_dataset("json", data_files=dataset_path)
    tokenized_datasets = prepare_dataset(dataset["train"])

    # Initialize the model and tokenizer
    model = T5ForConditionalGeneration.from_pretrained("t5-base")
    tokenizer = T5Tokenizer.from_pretrained("t5-base")

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    # Train the model
    trainer.train()

    # Save the model and tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

if __name__ == "__main__":
    dataset_path = "path/to/your/latex_dataset.json"
    output_dir = "./models/latex_converter"
    train_latex_model(dataset_path, output_dir)