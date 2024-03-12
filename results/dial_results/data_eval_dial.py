import json
import matplotlib.pyplot as plt
import numpy as np

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def get_file_names(category, model):
    return f"gpt4_{category}_detailed_{model}.json"

def process_data():
    categories = ["coh", "con", "rel"]
    it_models = [
        "Bloom-1b7",
        "Bloom-1b7-winograd-wsc-IT-baseline",
        "Bloom-1b7-ropes-Cont-IT-Step2",
        "Bloom-1b7-glue-mrpc-Cont-IT-Step3",
        "Bloom-1b7-dialogsum-Cont-IT-Step4",
        "Bloom-1b7-creative-writing-Cont-IT-Step5",
    ]
    baseline_models = [
        "Bloom-1b7-glue-mrpc-IT-baseline",
        "Bloom-1b7-ropes-IT-baseline",
        "Bloom-1b7-dialogsum-IT-baseline",
        "Bloom-1b7-creative-writing-IT-baseline",
    ]

    all_models = baseline_models + it_models
    results = {}

    for category in categories:
        for model in all_models:
            file_name = get_file_names(category, model)
            data = load_json(file_name)
            total_score = 0
            count = 0

            for item in data:
                for score in item["scores"]:
                    gpt4_avg = score.get("GPT4_avg", 0)
                    total_score += gpt4_avg if gpt4_avg > 0 else 1.0
                    count += 1

            average_score = total_score / count if count > 0 else 0
            results.setdefault(model, {})[category] = average_score

    baseline_results = {model: results[model] for model in baseline_models}
    it_results = {model: results[model] for model in it_models}

    return baseline_results, it_results

def save_data(baseline_data, it_data, baseline_file='baseline_eval_results.json', it_file='it_eval_results.json'):
    with open(baseline_file, 'w') as file:
        json.dump(baseline_data, file, indent=4)
    print(f"Baseline data saved to {baseline_file}")

    with open(it_file, 'w') as file:
        json.dump(it_data, file, indent=4)
    print(f"IT data saved to {it_file}")

category_colors = {
    "coh": "#6929c4",
    "con": "#002d9c",
    "rel": "#1192e8",
    "overall": "#005d5d"
}

def plot_category_averages(data):
    categories = ["coh", "con", "rel"]
    models = list(data.keys())

    for category in categories:
        plt.figure(figsize=(10, 6))
        scores = [data[model][category] for model in models]
        display_models = [model.replace("Bloom-1b7-", "") for model in models]
        plt.plot(display_models, scores, marker='o', linestyle='-', color=category_colors[category])
        plt.title(f'Average {category} Score by Model')
        plt.xlabel('Model')
        plt.ylabel('Average Score')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(1.0, 3.0)
        plt.tight_layout()
        plt.savefig(f'./graphs/{category}_averages.png')
        plt.close()
        print(f"Plot saved to {category}_averages.png")

def plot_overall_average(data):
    models = list(data.keys())
    overall_averages = [np.mean(list(data[model].values())) for model in models]
    display_models = [model.replace("Bloom-1b7-", "") for model in models]

    plt.figure(figsize=(10, 6))
    plt.plot(display_models, overall_averages, marker='o', linestyle='-', color=category_colors['overall'])
    plt.title('Overall Average Score by Model')
    plt.xlabel('Model')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(1.0, 3.0)
    plt.tight_layout()
    plt.savefig('./graphs/overall_average.png')
    plt.close()

    
def plot_scores_by_model(data):
    categories = ["coh", "con", "rel"]
    models = list(data.keys())

    plt.figure(figsize=(15, 8))
    x = np.arange(len(models))

    for category in categories:
        scores = [data[model][category] for model in models]
        plt.plot(x, scores, marker='o', linestyle='-', label=category, color=category_colors[category])

    overall_scores = [np.mean([data[model][category] for category in categories]) for model in models]
    plt.plot(x, overall_scores, marker='*', linestyle='-', label='Overall', color=category_colors['overall'], markersize=10)

    plt.title('Category and Overall Scores by Model')
    plt.xlabel('Model')
    plt.ylabel('Average Score')
    plt.xticks(x, [model.replace("Bloom-1b7-", "") for model in models], rotation=45, ha='right')
    plt.ylim(1.0, 3.0)
    plt.legend(title='Category/Overall')
    plt.tight_layout()
    plt.savefig('./graphs/category_scores_by_model.png')
    plt.close()
    
def plot_model_comparison(baseline_data, it_data):
    categories = ["coh", "con", "rel"]
    model_names = set(name.replace('-IT-baseline', '').replace('-Cont-IT-Step', '') for name in baseline_data.keys())

    for model_name in model_names:
        plt.figure(figsize=(18, 10))
        index = np.arange(len(categories) + 1)
        bar_width = 0.35

        baseline_scores = []
        it_scores = []

        for category in categories:
            baseline_score = np.mean([baseline_data[model][category] for model in baseline_data if model_name in model])
            it_score = np.mean([it_data[model][category] for model in it_data if model_name in model])
            baseline_scores.append(baseline_score)
            it_scores.append(it_score)

        baseline_overall = np.mean(baseline_scores)
        it_overall = np.mean(it_scores)
        baseline_scores.append(baseline_overall)
        it_scores.append(it_overall)

        for i, category in enumerate(categories + ['overall']):
            plt.bar(i, baseline_scores[i], bar_width, color=category_colors[category], label=f'{category} Baseline')
            plt.bar(i + bar_width, it_scores[i], bar_width, color=category_colors[category], alpha=0.5, label=f'{category} IT')

        plt.xlabel('Category')
        plt.ylabel('Scores')
        plt.title(f'Comparison of {model_name} Scores: Baseline vs IT')
        plt.xticks(index + bar_width / 2, categories + ['overall'])
        plt.ylim(1.0, 3.0)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'./graphs/{model_name}_comparison.png')
        plt.close()
        print(f"Plot saved for {model_name} comparison")






if __name__ == '__main__':
    print("Processing data...")
    baseline_data, it_data = process_data()

    print("Saving data...")
    save_data(baseline_data, it_data)

    print("Generating and saving plots for Baseline...")
    plot_category_averages(baseline_data)
    plot_overall_average(baseline_data)

    print("Generating and saving plots for IT...")
    plot_category_averages(it_data)
    plot_overall_average(it_data)
    plot_scores_by_model(it_data)

    plot_model_comparison(baseline_data, it_data)