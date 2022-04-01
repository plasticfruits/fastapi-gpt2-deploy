# text preprocessing modules
from string import punctuation
import re  # regular expression
import os
import uvicorn
from fastapi import FastAPI

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import AutoModel, AutoTokenizer

# from dependencies import *


app = FastAPI(
    title="'How To' Answer Generator",
    description="A simple API using GPT-2 fine-tuned model for answering 'How to' questions",
    version="0.1",
)

# load the sentiment model
model = AutoModel.from_pretrained("plasticfruits/gpt2-finetuned-how-to-qa")
tokenizer = AutoTokenizer.from_pretrained("plasticfruits/gpt2-finetuned-how-to-qa")


def clean_response(user_prompt, response):
    """
    """
    response = re.sub("(?<=\.)[^.]*$", "", response)  # finish at last sentence dot
    response = (
        response.replace("[WP]", "").replace(user_prompt, "").replace("[RESPONSE]", "")
    )
    response = response.lstrip()
    return response


@app.get("/answers")
def generate_response(user_prompt: str):
    """
    """
    prompt = f"<|startoftext|>[WP] {user_prompt} [RESPONSE]"
    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    sample_outputs = model.generate(
        generated,
        do_sample=True,
        top_k=50,
        max_length=300,
        top_p=0.95,
        num_return_sequences=1,
    )
    data = []
    for i, sample_output in enumerate(sample_outputs):
        response = clean_response(
            user_prompt, tokenizer.decode(sample_output, skip_special_tokens=True)
        )
        response_dict = {"key": i, "response": response}
        data.append(response_dict)
    # output = tokenizer.decode(sample_outputs, skip_special_tokens=True)
    # output = tokenizer.decode(sample_output, skip_special_tokens=True)
    return {"data": data[0]["response"]}