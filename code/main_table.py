import json
import re
import argparse
import os
from setup_TactfulToM import load_TactfulToM_dataset
from prettytable import PrettyTable

question_categories = ["comprehensionQA", "fact_reasonQA", "fact_truthQA", "beliefQAs", "infoAccessibilityQA_list", "infoAccessibilityQAs_binary", "answerabilityQA_list", "answerabilityQAs_binary", "lieabilityQAs","liedetectabilityQAs_list", "liedetectabilityQAs_binary"]

def filter_entry(entry, condition):
    if entry["clean_result"] is None or entry["clean_result"]=="ERROR":
        return False
    if not condition:
        return True
    if "context" in condition:
        return entry["context_type"] == condition


def _clean(entry, file_name):
    question_type = entry["question_type"]
    original_answer = entry["original_result"]
    if "Llama" in file_name:
        pattern = r'\\boxed\{(.*?)\}'
        format_output = re.findall(pattern, original_answer, re.DOTALL)
        if format_output:
            original_answer = format_output[0]
            # print(entry["original_result"])
            # print(original_answer)
    elif "DeepSeek-V3" in file_name:
        for pattern in [r'\\boxed\{(.*?)\}']:
            format_output = re.findall(pattern, original_answer, re.DOTALL)
            if format_output:
                original_answer = format_output[0]
                # print(entry["original_result"])
                # print(original_answer)
                break

    if question_type == "freeform":
        return original_answer
    
    if question_type == "binary":
        nonpunc_answer = re.sub(r'[^\w\s]', '', original_answer)
        if "yes" in nonpunc_answer.lower().split():
            return "yes"
        elif "no" in nonpunc_answer.lower().split():
            return "no"
        else:
            # print(entry)
            return "NAN"
    
    if question_type == "mcq":
        if original_answer.lower().startswith("option"):
            original_answer = original_answer[6:]
        else:
            pattern = r'[^}]*answer[^}]*:\s*([^}]+)'
            match = re.search(pattern, original_answer, re.IGNORECASE)
            if match:
                original_answer = match.group(1).strip()
        mcq_mapping = entry["mcq_mapping"]
        possible_answers = [str(i+1) for i in range(len(mcq_mapping))]
        first_number = original_answer.strip(" #*:")[0]
        if first_number in possible_answers: 
            return mcq_mapping[int(first_number)-1]
        # print(original_answer + "\n\n ")
        return "NAN"
    
    if question_type == "list":
        clean_result = original_answer.split(",")
        clean_result = [r.strip() for r in clean_result]
        return clean_result

def _clean_reasoning(entry, file_name):
    if "QwQ" in file_name or "DeepSeek-R1" in file_name:
        original_result = entry["original_result"]
        entry["original_result"] = original_result.split("</think>")[-1].strip()
        clean_result = _clean(entry, file_name)
        entry["original_result"] = original_result
        return clean_result

def clean(file_name):
    with open(f"results/original/{file_name}.json") as f:
        original_result = json.load(f)
    for i, question_set in enumerate(original_result):
        for category in question_categories:
            for j, cat_result in enumerate(question_set[category]):
                for k, entry in enumerate(cat_result):
                    if "QwQ" in file_name or "DeepSeek-R1" in file_name:
                        original_result[i][category][j][k]["clean_result"] = _clean_reasoning(entry, file_name)
                    else:
                        original_result[i][category][j][k]["clean_result"] = _clean(entry, file_name)
    with open(f"results/clean/{file_name}.json", "w") as f:
        json.dump(original_result, f, indent=3)

def _main_result(file_name, condition="full_context"):
    performance_list = {cat:[] for cat in question_categories}
    with open(f"results/clean/{file_name}.json") as f:
        original_result = json.load(f)
    # dataset = load_TactfulToM_dataset("../dataset/Tactful_conv_set_0_type1.json")
    for i, question_set in enumerate(original_result):
        # if not "real_reason_type" in dataset.iloc[i].keys() or not dataset.iloc[i]["real_reason_type"]:
        #     continue
        for category in question_categories:
            for j, cat_result in enumerate(question_set[category]):
                for k, entry in enumerate(cat_result):
                    if not filter_entry(entry, condition) or entry["question_type"]=="freeform":
                        continue
                    if entry["question_type"] == "binary":
                        performance = (entry["clean_result"].lower()==entry["correct_answer"].lower())
                    elif entry["question_type"] == "mcq":
                        try:
                            performance = 1 if (int(entry["clean_result"])==0) else 0
                        except:
                            performance = 0
                    elif entry["question_type"] == "list":
                        clean, correct = set(entry["clean_result"]), set(entry["correct_answer"])
                        inter = clean & correct
                        try:
                            prec, recall = len(inter)/len(correct), len(inter)/len(clean)
                            # performance = 2 * prec * recall/ (prec + recall) # f1
                            if prec==1 and recall==1:
                                performance = 1
                            else:
                                performance = 0
                        except:
                            performance = 0
                    performance_list[category].append(performance)
    return performance_list

def make_prettytable(full_results):
    table = PrettyTable()
    for file_name, result in full_results.items():
        if not table.field_names:
            table.field_names = ["model_type"] + [k for k in result.keys()]
        row = [file_name] + ["{:.2f}".format(result[k]*100) for k in table.field_names[1:]]
        table.add_row(row)
    print(table)
    with open("cases/main_table.txt", "w") as f:
        f.write(table.get_string())
    return table

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--condition', type=str, default="full_context")
    parser.add_argument('--file_name', type=str, default=None)
    args = parser.parse_args()

    if not args.file_name:
        file_names = os.listdir("results/clean/")
        file_names = [name[:-5] for name in file_names]
        model_list = set(name[:-2] for name in file_names)
    else:
        file_names = [args.file_name]
    file_names.sort()

    full_results = {m:{cat:[] for cat in question_categories} for m in model_list}
    for file_name in file_names:
        model_name = file_name[:-2]
        performance_list = _main_result(file_name, args.condition)
        for cat, performance in performance_list.items():
            full_results[model_name][cat] += performance
    
    for m, cat_performance in full_results.items():
        for cat, performance in cat_performance.items():
            if not len(performance):
                print(m, cat)
                full_results[m][cat] = 0
            else:
                full_results[m][cat] = sum(performance)/len(performance)
    # make table
    make_prettytable(full_results)
    

if __name__ == "__main__":
    main()
    # wrong_answer_mcq("gpt-4-0613", "full_context")