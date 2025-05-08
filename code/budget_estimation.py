from get_original_results import get_llm_input
from setup_TactfulToM import load_TactfulToM_dataset
import tiktoken
import random
from openai import OpenAI
import json
from tqdm import tqdm
import concurrent

question_categories = ["comprehensionQA", "justificationQA", "fact_reasonQA", "fact_truthQA", "beliefQAs", "infoAccessibilityQA_list", "infoAccessibilityQAs_binary", "answerabilityQA_list", "answerabilityQAs_binary", "lieability","liedetectabilityQAs_list", "liedetectabilityQAs_binary"]

class LLM:
    def __init__(self, llm_name, max_workers):
        self.llm_name = llm_name
        self.max_workers = max_workers
        if "test" in llm_name:
            self.client = None
        elif "gpt" in llm_name:
            self.client = OpenAI(api_key="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")
        else: 
            self.client = OpenAI(api_key="VTPb47ZyaGObTYCSXlMYhaXjxEG3fm6C",base_url="https://api.deepinfra.com/v1/openai")
    
    def generate_single(self, single_input, llm_name):
        if not self.client:
            return ""
        response = self.client.chat.completions.create(
            model=llm_name,
            messages=single_input,
            temperature=0.2,
            max_tokens=4096
        )
        return response.choices[0].message.content
    
    def generate_helper(self, args):
        return self.generate_single(*args)
    
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
            return self.generate_set(set_inputs)

def num_token_regular(sample):
    set_inputs = []
    for cat in question_categories:
        if not cat in sample.keys():
            print(f"No such category: {cat}")
            continue
        cat_questions = sample[cat]
        for question in cat_questions:
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
            
            for question_type in question_types:
                for context_type in ["full_context"]:
                    context = sample[context_type]
                    llm_input, mcq_mapping = get_llm_input(question, question_type, context, cot=False)
                    set_inputs.append(llm_input)
    enc = tiktoken.encoding_for_model("gpt-4-0613")
    input_tokens, output_tokens = 0, 0
    for single_input in set_inputs:
        input_tokens += len(enc.encode(single_input[0]["content"]+single_input[1]["content"]))
        output_tokens += 30
    return input_tokens, output_tokens

def num_token_cot(sample):
    set_inputs = []
    for cat in question_categories:
        if not cat in sample.keys():
            print(f"No such category: {cat}")
            continue
        cat_questions = sample[cat]
        for question in cat_questions:
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
            
            for question_type in question_types:
                for context_type in ["full_context"]:
                    context = sample[context_type]
                    llm_input, mcq_mapping = get_llm_input(question, question_type, context, cot=True)
                    set_inputs.append(llm_input)
    llm = LLM("gpt-4-0613", 64)
    set_output = llm.generate_set(set_inputs, False)
    enc = tiktoken.encoding_for_model("gpt-4-0613")
    input_tokens, output_tokens = 0, 0
    for i, single_input in enumerate(set_inputs):
        single_output = set_output[i]
        input_tokens += len(enc.encode(single_input[0]["content"]+single_input[1]["content"]))*2
        input_tokens += len(enc.encode(single_output))
        output_tokens += 30 + len(enc.encode(single_output))
    return input_tokens, output_tokens

def num_token_reasoning(sample):
    set_inputs = []
    for cat in question_categories:
        if not cat in sample.keys():
            print(f"No such category: {cat}")
            continue
        cat_questions = sample[cat]
        for question in cat_questions:
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
            
            for question_type in question_types:
                for context_type in ["full_context"]:
                    context = sample[context_type]
                    llm_input, mcq_mapping = get_llm_input(question, question_type, context, cot=True)
                    set_inputs.append(llm_input)
    llm = LLM("Qwen/QwQ-32B", 64)
    set_output = llm.generate_set(set_inputs, False)
    enc = tiktoken.encoding_for_model("gpt-4-0613")
    input_tokens, output_tokens = 0, 0
    for i, single_input in enumerate(set_inputs):
        single_output = set_output[i]
        input_tokens += len(enc.encode(single_input[0]["content"]+single_input[1]["content"]))
        output_tokens += len(enc.encode(single_output))
    return input_tokens, output_tokens

if __name__ == "__main__":
    sample = load_TactfulToM_dataset("../dataset/Tactful_conv_question.json").iloc[0]
    # print(f"#Regular Tokens (i,o): {num_token_regular(sample)}")
    # print(f"#CoT Tokens (i,o): {num_token_cot(sample)}")
    # print(f"#Reasoning Tokens (i,o): {num_token_reasoning(sample)}")
    # num_tokens = [(65694,1410),(138299,7193)]
    # gpt, qwen, deepseek, llama, claude = [30,60], [0.13,0.40], [0.40,0.89], [0.23,0.40], [3.30,16.50]

    # for input_price, output_price in [gpt, qwen, deepseek, llama, claude]:
    #     for num_input_token, num_output_token in num_tokens:
    #         print((input_price*num_input_token+output_price*num_output_token)*150/1_000_000)
    
    num_reasoning_tokens = [(66258, 41462)]
    o1, qwq, r1 = (15,60), (0.12,0.18), (0.55,2.19)
    for input_price, output_price in [o1, qwq, r1]:
        for num_input_token, num_output_token in num_reasoning_tokens:
            print((input_price*num_input_token+output_price*num_output_token)*150/1_000_000)

    

    