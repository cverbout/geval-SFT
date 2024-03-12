#!/bin/bash

# Check if an API key argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <API_KEY>"
    exit 1
fi

API_KEY=$1

# Define arrays of models
writer_models=(
    #"bigscience/bloom-1b7"
    #"alonzogarbanzo/Bloom-1b7-creative-writing-Cont-IT-Step5"
    #"alonzogarbanzo/Bloom-1b7-dialogsum-Cont-IT-Step4"
    #"alonzogarbanzo/Bloom-1b7-glue-mrpc-Cont-IT-Step3"
    #"alonzogarbanzo/Bloom-1b7-ropes-Cont-IT-Step2"
    #"alonzogarbanzo/Bloom-1b7-creative-writing"
    "alonzogarbanzo/Bloom-1b7-glue-mrpc-IT-baseline"
    "alonzogarbanzo/Bloom-1b7-winograd-wsc-IT-baseline"
    "alonzogarbanzo/Bloom-1b7-ropes-IT-baseline"
    "alonzogarbanzo/Bloom-1b7-dialogsum-IT-baseline"
    "alonzogarbanzo/Bloom-1b7-creative-writing-IT-baseline"
)
prompt_fps=(
    "./prompts/dialeval/coh_detailed.txt"
    "./prompts/dialeval/con_detailed.txt"
    "./prompts/dialeval/rel_detailed.txt"
)

# Loop through each combination of model and prompt file
for writer_model in "${writer_models[@]}"; do
    # Use sed to extract only the part after 'alonzogarbanzo/' for the file path
    model_name=$(echo "$writer_model" | sed 's|.*/||')  # This removes everything before the last slash
    for prompt_fp in "${prompt_fps[@]}"; do
        # Define the data file path specific to each model
        data_fp="./data/dialeval_data_alonzogarbanzo/${model_name}.json"
        # Create a unique save file path
        prompt_name=$(basename "$prompt_fp" .txt)
        save_fp="./results/gpt4_${prompt_name}_${model_name}.json"
        
        # Run the Python script with the current settings
        python ./gpt4_dialeval.py \
            --key $API_KEY \
            --writer_model $writer_model \
            --prompt_fp $prompt_fp \
            --save_fp $save_fp \
            --data_fp $data_fp

        echo "Completed processing for model $writer_model with prompt $prompt_fp"
        sleep 5  # Wait for 5 seconds before the next iteration
    done
done

echo "All models and prompts processed."
