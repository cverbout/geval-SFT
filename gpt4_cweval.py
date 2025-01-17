# -*- coding: utf-8 -*-
"""LLM_Proj.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rdWWEH5BLf_0T3Fp6FPl5vrFe4Qz_sve
"""
import json
import os
import random
import time
import warnings
import argparse
import torch
import openai
from tqdm import tqdm
import tqdm
from openai import OpenAI
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

warnings.filterwarnings('ignore')
set_seed(42)
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def get_full_prompt(prompts, title):
    return f"{random.choice(prompts)} {title}</s> Story: "

def get_model(model_name):
  model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
  return model

def get_tokenizer(model_name):
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  return tokenizer

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--writer_model', type=str, default='alonzogarbanzo/Bloom-1b7-creative-writing-IT-baseline')
    argparser.add_argument('--prompt_fp', type=str, default='prompts/cweval/ima_detailed.txt')
    argparser.add_argument('--save_fp', type=str, default='results/cweval_ima_detailed.json')
    argparser.add_argument('--data_fp', type=str, default='data/cweval_data.json')
    argparser.add_argument('--key', type=str, required=True)
    argparser.add_argument('--model', type=str, default='gpt-4-0125-preview')
    args = argparser.parse_args()

   
    model_name = args.writer_model
    
    save_fp = f'data/cweval_data_alonzogarbanzo/{model_name}.json'
    if not os.path.exists(save_fp):
        tokenizer = get_tokenizer(model_name)
        model = get_model(model_name)

        dataset = load_dataset("adambjorn/UnrelatedForgettingOverhead", 'creative')
        test_dataset = dataset['test']
        prompts = [
            "Write a creative short story based on the following title:",
            "Here is a title for a story. Craft a short narrative around it:",
            "Using the title given, develop a short story:",
            "Imagine a short story that starts with this title:",
            "Create a brief story with the following title:"
        ]

        prompt_list = []
        for i in range(len(test_dataset)):
            full_prompt = get_full_prompt(prompts, test_dataset['title'][i])
            prompt_list.append(full_prompt)
            
        prompt_list_len = len(prompt_list)

        generated_outputs = []
        count = 0
        for prompt in prompt_list:
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
            output_ids = model.generate(input_ids, max_new_tokens=200)[0]
            generated_text = tokenizer.decode(output_ids)
            story_intro, _, story_content = generated_text.partition("Story: ")
            generated_outputs.append({
            'source': prompt,  
            'piece': story_content.strip() 
            })
            count += 1
            print(f'{count}/{prompt_list_len} Added')

        
        with open(save_fp, 'w') as f:
            json.dump(generated_outputs, f, indent=4)
            print(f"Saved generated outputs to {save_fp}")

    client = OpenAI(api_key=args.key)
    creative_works = json.load(open(args.data_fp))
    prompt = open(args.prompt_fp).read()

    ct, ignore = 0, 0

    new_json = []
    for instance in tqdm.tqdm(creative_works):
        doc_id = ct
        piece_text = instance['piece'] 
        cur_prompt = prompt.replace('{{Piece}}', piece_text)
        instance['prompt'] = cur_prompt
        while True:
            try:
                _response = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "system", "content": cur_prompt}],
                    temperature=0,
                    max_tokens=1,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    n=10
                )
                time.sleep(0.5)
                all_responses = []
                for choice in _response.choices:
                    # Properly access the content of the message
                    message_content = choice.message.content if choice.message else ""
                    all_responses.append(message_content)
                    
                scores_int = [int(score) for score in all_responses if score.isdigit()]
                avg_score = sum(scores_int) / len(scores_int) if scores_int else 0
                scores = [{'GPT4_avg': avg_score}]
                
                new_instance = {
                'doc_id': doc_id,
                'piece': piece_text,
                'scores': scores,
                'prompt': cur_prompt,
                'all_responses': all_responses
                }
                new_json.append(new_instance)
                ct += 1
                break
            except Exception as e:
                print(e)
                if "limit" in str(e):
                    time.sleep(2)
                else:
                    ignore += 1
                    print('ignored', ignore)
                    break

    print('ignored total', ignore)
    with open(args.save_fp, 'w') as f:
        json.dump(new_json, f, indent=4)