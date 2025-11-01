from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import json
import os
from tqdm import tqdm

import numpy as np

import re

question_categories = ["comprehensionQA", "justificationQA", "fact_reasonQA", "fact_truthQA", "beliefQAs", "infoAccessibilityQA_list", "infoAccessibilityQAs_binary", "answerabilityQA_list", "answerabilityQAs_binary", "lieabilityQAs","liedetectabilityQAs_list", "liedetectabilityQAs_binary"]

def simple_tokenize(text):
    """Tokenize text using simple whitespace and punctuation split."""
    # Lowercase and split on non-word characters
    return re.findall(r'\w+', text.lower())

def token_f1_score(s1, s2, tokenizer=word_tokenize):
    """
    Computes the token-level F1 score between two sentences.

    Args:
        s1 (str): The first sentence (reference/gold).
        s2 (str): The second sentence (prediction).
        tokenizer (function): Function to tokenize sentences (default: simple whitespace/word split).

    Returns:
        float: F1 score (0 to 1).
    """
    tokens1 = tokenizer(s1)
    tokens2 = tokenizer(s2)

    set1 = set(tokens1)
    set2 = set(tokens2)

    if not set1 and not set2:
        return 1.0  # Both empty
    if not set1 or not set2:
        return 0.0  # One is empty

    # Intersection = common tokens
    common = set1 & set2
    precision = len(common) / len(set2)
    recall    = len(common) / len(set1)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def sentence_cosine_similarity(sent1, sent2, model):
    embeddings = model.encode([sent1, sent2])
    sim = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )
    return sim[0][0].item()

def get_similarity_score(type_num="0"):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    dataset_name = f"dataset/final_set/Tactful_conv_set_{type_num}.json"
    result_file_names = os.listdir("results/original/")
    type_files = []
    for name in result_file_names:
        if name.endswith(f"{type_num}.json"):
            type_files.append(name)
    # type_files = [os.path.join("results/original/", name) for name in type_files]

    with open(dataset_name) as f:
        original_dataset = json.load(f)
    for name in tqdm(type_files):
        result_file = os.path.join("results/original/", name)
        with open(result_file) as f:
            result = json.load(f)
        
        # print(len(result), len(original_dataset))
        for i, question_set in enumerate(tqdm(result)):
            for category in question_categories:
                for j, cat_result in enumerate(question_set[category]):
                    for k, entry in enumerate(cat_result):
                        if not entry["question_type"]=="freeform":
                            continue
                        answer = result[i][category][j][k]["original_result"].split("</think>")[-1]
                        original = original_dataset[i][category][j]
                        if type(original["wrong_answer"]) == str:
                            options = [original["correct_answer"]] + [original["wrong_answer"]]
                        else:
                            options = [original["correct_answer"]] + original["wrong_answer"]
                            
                        result[i][category][j][k]["token_f1"] = [token_f1_score(answer, option) for option in options]
                        result[i][category][j][k]["cos_similarity"] = [sentence_cosine_similarity(answer, option, model) for option in options]
        to_file = os.path.join("results/original/", name[:-5]+"_sim.json")
        with open(result_file, "w") as f:
            json.dump(result, f, indent=3)

if __name__ == "__main__":
    for type_num in ["0", "1", "2", "3", "4"]:
        get_similarity_score(type_num)