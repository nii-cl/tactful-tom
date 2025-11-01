import argparse
from setup_TactfulToM import load_TactfulToM_dataset, build_mcq_prompt,_setup_fact_mcq, _setup_fact_dist, build_dist_prompt, _setup_dist
import random
from openai import OpenAI
import json
import time
from tqdm import tqdm
import concurrent


class LLM:
    def __init__(self, llm_name, max_workers):
        self.llm_name = llm_name
        self.max_workers = max_workers
        self.error_times = 0
        if "test" in llm_name:
            self.client = None
        elif "gpt" in llm_name or "o1" in llm_name or "o3" in llm_name:
            self.client = OpenAI(api_key="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")
        else: 
            self.client = OpenAI(api_key="VTPb47ZyaGObTYCSXlMYhaXjxEG3fm6C",base_url="https://api.deepinfra.com/v1/openai")
    
    def generate_single(self, single_input, llm_name):
        if not self.client:
            return ""
        if "o1" in llm_name or "o3" in llm_name:
            response = self.client.chat.completions.create(
                model=llm_name,
                messages=single_input
            )
        else:
            response = self.client.chat.completions.create(
                model=llm_name,
                messages=single_input,
                temperature=0.2,
                max_tokens=8192
            )
        return response.choices[0].message.content
    
    def generate_helper(self, args):
        try:
            return self.generate_single(*args)
        except:
            self.error_times += 1
            return "ERROR"
        
    
    def generate_set(self, set_inputs, cot=False):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = zip(set_inputs, [self.llm_name] * len(set_inputs))
            responses = list(tqdm(executor.map(self.generate_helper, tasks), total=len(set_inputs)))
        if not cot:
            return responses
        else:
            # print("COT GENERATING")
            for i, single_input in enumerate(set_inputs):
                set_inputs[i][1]["content"] += responses[i] + "\n\nTherefore, the final answer is: "
            # time.sleep(2)
            return self.generate_set(set_inputs)
            
def get_user_prompt(question_type, context, question, options=None, information_prompt=None, cot=None):
    context_prompt = f"# Context:\n{context}\n\n"

    if not information_prompt:
        information_prompt = ""
    
    question_prompt = f"# Question:\n{question}\n\n"

    if question_type == "mcq":
        options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
        option_prompt = f"# Options:\n{options_text}\n\n"
    else:
        option_prompt = ""
    
    if cot:
        cot_prompt = "Let's think step by step:\n"
    else:
        cot_prompt = ""
    # type_instruction_mapping = {
    #     "binary": "Please answer with 'Yes' or 'No':",
    #     "freeform": "Please provide your detailed answer below:",
    #     "mcq": "Please select the correct option number:",
    #     "list": "Please only list the required items and split them with commas:"
    # }
    # instruction_prompt = type_instruction_mapping[question_type]

    user_prompt = context_prompt + information_prompt + question_prompt + option_prompt + cot_prompt # + instruction_prompt
    return user_prompt

def get_system_prompt(question_type, cot):
    if not cot:
        if question_type == "binary":
            system_prompt = "You are an expert in social reasoning. Answer the following question with 'Yes' or 'No'. Remember: Your answer should ONLY include 'Yes' or 'No' with nothing else."
        elif question_type == "freeform":
            system_prompt = "You are an expert in social reasoning. Answer the following question with a single sentence."
        elif question_type == "mcq":
            system_prompt = "You are an expert in social reasoning. Answer the following question with the option number of the most appropriate answer. Remember: Your answer should ONLY include the option number with nothing else." 
        elif question_type == "list":
            system_prompt = "You are an expert in social reasoning. List the required items and split them with commas. Remember: Your answer should ONLY include the required items spliited by commas with nothing else."
    else:
        if question_type == "binary":
            system_prompt = "You are an expert in social reasoning. Think step by step and give a final answer of 'Yes' or 'No' only."
        elif question_type == "freeform":
            system_prompt = "You are an expert in social reasoning. Think step by step and give a final answer of a single sentence."
        elif question_type == "mcq":
            system_prompt = "You are an expert in social reasoning. Think step by step and give a final answer of the option number of the most appropriate answer."
        elif question_type == "list":
            system_prompt = "You are an expert in social reasoning. Think step by step, list the required items and split them with commas."
    return system_prompt

def get_llm_input(question, question_type, context, cot):
    # print(question)
    question_text = question["question"]
    system_prompt = get_system_prompt(question_type, cot)
    # information prompt
    if "information" in question.keys():
        # print(question["information"])
        information_prompt = f"# Information:\n{question['information']}\n\n"
    else:
        target_question_keys = ["fact_question_real_reason", "comprehension_q", "fact_question_truth", "truth_question"]
        information_prompt = ""
        for q_key in target_question_keys:
            if q_key in question.keys():
                information_prompt = f"# Target Question:\n{question[q_key]}\n\n"
                break
    # options
    if question_type == "mcq":
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
        mapping = [i for i in range(len(options))]
        random.shuffle(mapping)
        # print(len(options))
        # try:
        #     assert len(options) == 4
        # except:
        #     print(options)
        # while len(options) < 4:
        #     options.append(wrong_answer_list[0])
        new_options = [options[m] for m in mapping]
        # print(question.keys())
        user_prompt = get_user_prompt(question_type, context, question_text, new_options, information_prompt, cot)
    else:
        mapping, options = [], []
        user_prompt = get_user_prompt(question_type, context, question_text, None, information_prompt, cot)
    llm_input = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    return llm_input, mapping
    # original_result = llm.generate(system_prompt, user_prompt)
    # clean_result = clean_llm_generated_result(question_type, original_result)
    # if question_type == "mcq":
    #     try:
    #         clean_result = mapping[int(clean_result)-1]
    #     except:
    #         clean_result = "NAN"
    # return original_result, clean_result

def get_results(data_path, llm_name, cot, max_workers):
    # load data
    df = load_TactfulToM_dataset(data_path)

    llm = LLM(llm_name, max_workers)

    # todo: liability
    # question_categories = ["comprehensionQA", "justificationQA", "fact_reasonQA", "fact_truthQA", "beliefQAs", "infoAccessibilityQA_list", "infoAccessibilityQAs_binary", "answerabilityQA_list", "answerabilityQAs_binary", "lieability","liedetectabilityQAs_list", "liedetectabilityQAs_binary"]
    question_categories = ["comprehensionQA","fact_reasonQA", "fact_truthQA", "beliefQAs", "infoAccessibilityQA_list", "infoAccessibilityQAs_binary", "answerabilityQA_list", "answerabilityQAs_binary", "lieabilityQAs","liedetectabilityQAs_list", "liedetectabilityQAs_binary"]

    results = []
    for idx, questions_set in df.iterrows():
        if not idx % 10:
            print(f"Progress: {idx} / {df.shape[0]}")
        set_results = {cat: [] for cat in question_categories}
        set_inputs = []

        # mapping for mcq questions in this set
        # mcq_mapping[llm_generated_answer] == 0 means that llm_generated_answer is correct
        # mcq_mapping = [i for i in range(4)]
        # random.shuffle(mcq_mapping)

        '''Step 1: Initialize the result list'''
        for cat in question_categories:
            if not cat in questions_set.keys():
                print(f"No such category: {cat}")
                continue
            cat_questions = questions_set[cat]
            for question in cat_questions:
                # question_type for different question_category
                # one question could have multiple answers, depending on the number of question_type and context_type
                if "list" in cat:
                    question_types = ["list"]
                elif "binary" in cat:
                    question_types = ["binary"]
                elif cat == "comprehensionQA":
                    question_types = ["freeform", "binary"]
                elif cat == "lieability":
                    question_types = ["mcq"]
                else:
                    question_types = ["freeform", "mcq"]
                
                results_question = []
                for question_type in question_types:
                    for context_type in ["full_context"]:
                        context = questions_set[context_type]
                        llm_input, mcq_mapping = get_llm_input(question, question_type, context, cot)
                        set_inputs.append(llm_input)
                        # original_result, clean_result = get_result(question, question_type, context, llm)
                        results_question.append({
                            "question": question["question"],
                            "correct_answer": question["correct_answer"],
                            "original_result": "",
                            "clean_result": "",
                            "question_type": question_type,
                            "context_type": context_type,
                            "mcq_mapping": mcq_mapping,
                            "question_id": question["q_id"]
                        })
                set_results[cat].append(results_question)

        '''Step 2: Use LLM to generate the results'''
        set_outputs = llm.generate_set(set_inputs, cot)
        print(f"Error times: {llm.error_times}")

        '''Step 3: Update the result list'''
        pointer = 0
        for cat in question_categories:
            for i, result_cat in enumerate(set_results[cat]):
                for j, result in enumerate(result_cat):
                    question_type = result["question_type"]
                    original_output = set_outputs[pointer]
                    # clean_output = clean_llm_generated_result(question_type, single_output)
                    # if question_type == "mcq":
                    #     try:
                    #         clean_output = mcq_mapping[int(clean_output)-1]
                    #     except:
                    #         clean_output = "NAN"
                    set_results[cat][i][j]["original_result"] = original_output
                    # set_results[cat][i][j]["clean_result"] = clean_output
                    pointer += 1
        results.append(set_results)
        file_name = llm_name.split("/")[-1]
        if cot:
            file_name += "-cot"
        question_type = data_path.split(".")[0].split("_")[-1]
        file_name += f"-{question_type}"
        # print(file_name)
        with open(f"results/original/{file_name}.json", "w") as f:
            json.dump(results, f, indent=3)
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", type=str, default="dataset/Tactful_conv_set_0.json,dataset/Tactful_conv_set_1.json,dataset/Tactful_conv_set_2.json,dataset/Tactful_conv_set_3.json,dataset/Tactful_conv_set_4.json")
    parser.add_argument('--llms', type=str, default="Qwen/Qwen2.5-72B-Instruct,Qwen/QwQ-32B,deepseek-ai/DeepSeek-V3-0324,deepseek-ai/DeepSeek-R1-Turbo,meta-llama/Llama-3.3-70B-Instruct,gpt-4o-2024-08-06,o1-2024-12-17,o3-mini-2025-01-31")
    parser.add_argument('--max_workers', type=int, default=64)
    parser.add_argument('--cot', default=None)
    args = parser.parse_args()

    llm_list = args.llms.split(",")
    llm_list = [llm.strip() for llm in llm_list]

    path_list = args.paths.split(",")
    path_list = [path.strip() for path in path_list]

    for path in path_list:
        for llm in llm_list:
            if not args.cot is None:
                cot_list = [bool(args.cot)]
            elif llm in ["Qwen/QwQ-32B", "deepseek-ai/DeepSeek-R1-Turbo", "o1-2024-12-17", "o3-2025-04-16", "o3-mini-2025-01-31"]:
                cot_list = [False]
            else:
                cot_list = [True, False]
            for cot in cot_list:
                get_results(path, llm, cot, max_workers=args.max_workers)

if __name__ == "__main__":
    main()