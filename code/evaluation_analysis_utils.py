import json
from setup_TactfulToM import load_TactfulToM_dataset
from evaluate_non_freeform import question_categories, filter_entry, _clean

def wrong_answer_mcq(file_name, condition):
    wrong_mcqs = []
    with open(f"../results/clean/{file_name}.json") as f:
        original_result = json.load(f)
    dataset = load_TactfulToM_dataset("../dataset/Tactful_conv_question.json")
    for i, question_set in enumerate(original_result):
        for category in question_categories:
            for j, cat_result in enumerate(question_set[category]):
                for k, entry in enumerate(cat_result):
                    if not filter_entry(entry, condition) or entry["question_type"]=="freeform":
                        continue
                    if entry["question_type"] == "mcq" and entry["clean_result"]!=0:
                        question = dataset.iloc[i][category][j]
                        if "wrong_answer" in question.keys():
                            wrong_answer_list = question["wrong_answer"]
                        elif "wrong_answers" in question.keys():
                            wrong_answer_list = question["wrong_answers"]
                        else:
                            print("No wrong answers in the following question.")
                            print(question)
                            wrong_answer_list = []
                        if not type(wrong_answer_list) == list:
                            wrong_answer_list = [wrong_answer_list]
                        while type(wrong_answer_list[0]) == list:
                            wrong_answer_list = wrong_answer_list[0]
                        options = [question["correct_answer"]] + wrong_answer_list
                        wrong_mcqs.append({
                            "question": question["question"],
                            "llm_answer": entry["clean_result"],
                            "options": options,
                            "category": category
                        })
    with open(f"../cases/wrong_mcq.json", "w") as f:
        json.dump(wrong_mcqs, f, indent=3)