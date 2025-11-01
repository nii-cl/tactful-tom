
import os
import json
import pandas as pd
import torch
from torch.utils.data import Dataset
import pandas as pd
import random

def load_TactfulToM_dataset(json_path: str = "TactfulToM_set.json") -> pd.DataFrame:
    """
    读取 TactfulToM.json, 并返回一个 pandas.DataFrame
    """
    # 如果需要先构建/下载数据，可以在这里调用你原先的 _build_data(TactfulToM) 函数
    # dpath = _build_data(TactfulToM)
    # file_path = os.path.join(dpath, "TactfulToM.json")

    # 简单场景下，直接从本地读
    file_path = json_path

    df = pd.read_json(file_path)
    return df

#####################
# mcq_prompt set up
def build_mcq_prompt(question: str, correct_answer: str, wrong_answers: list, context: str = "") -> dict:
    """
    构建一个多选题 (MCQ) 的提示 (prompt)。

    参数:
        question (str): 问题文本。
        correct_answer (str): 正确答案。
        wrong_answers (list): 错误答案的列表。
        context (str): 可选的上下文信息，默认为空字符串。

    返回:
        dict: 包含以下字段的字典：
            - "system_prompt" (str): 告诉模型回答多选题的规则，要求输出格式为 [A], [B], [C], ...。
            - "user_prompt" (str): 包含上下文、问题和枚举后的选项，让模型选择答案。
            - "input_text" (str): 实际传递给模型的完整 prompt（通常与 user_prompt 类似）。
            - "options" (list): 打乱顺序后的所有选项列表。
            - "correct_index" (int): 正确答案在 options 列表中的索引，用于后续评估。

    核心处理功能:
        1. 将正确答案与错误答案合并后随机打乱。
        2. 根据打乱后的顺序构造选项，并记录正确答案在该列表中的位置。
        3. 构造 system_prompt 作为系统指令，要求模型只返回 [A], [B], [C] 等格式的答案。
        4. 构造 user_prompt，包含上下文、问题和详细的选项列表。
    """
    result = {}

    # 1. 构造 system_prompt
    system_prompt = (
        "You are an expert at answering multiple-choice questions. "
        "Please choose the most probable answer to the following question from the options. "
        "Output your final verdict by strictly following this format: [A], [B], [C], or [D]."
    )
    
    # 2. 将正确答案和错误答案合并，随机打乱顺序
    # 如果 wrong_answers 不是列表，则将其包装为列表（或处理为 []）
    if not isinstance(wrong_answers, list):
        if wrong_answers:  # 如果不为空，则构造成列表
            wrong_answers = [wrong_answers]
        else:
            wrong_answers = []
    # 将正确答案和错误答案合并，随机打乱顺序
    all_answers = [correct_answer] + wrong_answers
    random.shuffle(all_answers)
    
    # 记录正确答案在打乱后列表中的索引
    correct_index = all_answers.index(correct_answer)
    # options_text = "\n".join([f"{chr(65+idx)}. {answer}" for idx, answer in enumerate(all_answers)])
    
    # 3. 枚举列出选项，用字母标号
    letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
    enumerated_choices_lines = []
    for i, ans in enumerate(all_answers):
        enumerated_choices_lines.append(f"[{letters[i]}] {ans}")
    enumerated_choices = "\n".join(enumerated_choices_lines)
    
    # 4. 构造 user_prompt（更具说明性的提示）
    user_prompt = (
        f"# Context\n{context}\n\n"
        f"# Question\n{question}\n\n"
        f"# Options\n{enumerated_choices}\n\n"
        "Please select the best option above.\n"
        "Answer:"
    )
    
    # 将所有构造的内容保存到结果字典中
    result["system_prompt"] = system_prompt
    result["user_prompt"] = user_prompt
    result["options"] = all_answers
    result["correct_index"] = correct_index

    return result

# dist_prompt set up
def build_dist_prompt(question: str, context: str = "") -> dict:
    """
    构建一个简答题 (dist) 的提示 (prompt)。

    参数:
        question (str): 问题文本。
        correct_answer (str): 正确答案。
        context (str): 可选的上下文信息，默认为空字符串。

    返回:
        dict: 包含以下字段的字典：
            - "system_prompt" (str): 给模型的 system 提示
            - "user_prompt" (str): 给模型的 user 提示
            - "correct_answer" (str): 正确答案，供后续评估使用。
    """

    # 1) 构造 system_prompt
    system_prompt = (
        "You are an expert at answering questions. "
    )

    # 2) 构造 user_prompt
    user_prompt = (
        f"# Context\n{context}\n\n"
        f"# Question\n{question}\n\n"
        "Answer:"
    )

    # 3) 返回包含所需字段的字典
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }
#######################
# _setup_dist:
# setup_comprehension_questions
# setup_justification_questions
def _setup_dist(qa: dict, context: str, set_id: str) -> dict:
    """
    构建一个dist 类型问题的提示 (prompt)，并返回包含所需字段的字典。
    适用于：不需要更改question type的问题。

    参数:
        comprehension_qa (dict): 包含 "question"、"correct_answer"，以及可选 "wrong_answer" 的字典。
        context (str): 问题的上下文字符串。
        set_id (str): 当前数据条目的标识，用于构造 q_id。

    返回:
        dict: 包含以下字段:
            - "system_prompt": 给模型的 system 提示
            - "user_prompt": 给模型的 user 提示
            - "correct_answer": 正确答案，供后续评估使用
            - "question_type": "comprehension"
            - "q_id": 原始 q_id 加上后缀 set_id
    """
    question = qa.get("question", "")
    question_type = qa.get("question_type", "")
    correct_answer = qa.get("correct_answer", "")
    original_q_id = qa.get("q_id", "")
    new_q_id = f"{original_q_id}-{set_id}"

    system_prompt = (
        "You are an expert at reading comprehension and freeform answer generation. "
        "Carefully analyze the provided context and question before generating your detailed answer."
    )
    
    user_prompt = (
        f"# Context\n{context}\n\n"
        f"# Question\n{question}\n\n"
        "Please provide your detailed and thoughtful answer below:"
    )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "correct_answer": correct_answer,
        "question_type": question_type,
        "q_id": new_q_id
    }

#######################
# fact_Q set up
def _setup_fact_dist(fact_qa: dict, context: str, set_id: str) -> dict:
    """
    针对简答题 (dist) 的组装函数。
    
    参数:
        fact_qa (dict): 包含 "question", "correct_answer"，以及可选 "wrong_answers" 的字典。
        context (str): 问题的上下文字符串。
        set_id (str): 当前数据条目的标识。

    返回:
        dict: 包含以下字段:
            - "system_prompt": 给模型的 system 提示
            - "user_prompt": 给模型的 user 提示
            - "correct_answer": 正确答案
            - "question_type": "fact:dist"
            - "q_id":"q_id"+"0"
    """
    question = fact_qa.get("question", "")
    correct_answer = fact_qa.get("correct_answer", "")
    
    original_q_id = fact_qa.get("q_id", "")
    new_q_id = f"{original_q_id}-{0}"

    # 使用 build_dist_prompt 来生成 system_prompt / user_prompt / correct_answer
    prompt = build_dist_prompt(question, context)

    # 更改 question_type 附加到返回的字典里
    prompt["question_type"] = "fact:dist"
    prompt["q_id"] = new_q_id

    return prompt

def _setup_fact_mcq(fact_qa: dict, context: str, set_id: str) -> dict:
    """
    针对多选题 (mcq) 的组装函数。

    参数:
        fact_qa (dict): 包含 "question", "correct_answer"，以及可选 "wrong_answers" 的字典。
        context (str): 问题的上下文字符串。
        set_id (str): 当前数据条目的标识。

    返回:
        dict: 在基础字段上还包含:
            - "system_prompt": 系统提示（要求模型返回 [A], [B], ...）
            - "user_prompt": 包含上下文、问题和枚举后的选项
            - "input_text": 实际给模型的 prompt
            - "options": 打乱顺序后的所有选项列表
            - "correct_index": 正确答案在 options 列表中的索引（用于后续评估）
            - "question_type": "fact:mcq"
            - "q_id":"q_id"+"1"
    """
    question = fact_qa.get("question", "")
    correct_answer = fact_qa.get("correct_answer", "")
    wrong_answers = fact_qa.get("wrong_answers", [])
    original_q_id = fact_qa.get("q_id", "")
    new_q_id = f"{original_q_id}-{1}"

    # def build_mcq_prompt(question: str, correct_answer: str, wrong_answers: list, context: str = "") -> dict:
    # 调用 build_mcq_prompt 构造完整的多选题提示
    prompt = build_mcq_prompt(
        question=question,
        correct_answer=correct_answer,
        wrong_answers=wrong_answers,
        context=context
    )
    
    # 可以把 question_type 附加到返回的字典里
    prompt["question_type"] = "fact:mcq"
    prompt["q_id"] = new_q_id

    return prompt

#######################
# belief set up
def _setup_belief_dist(fact_qa: dict, context: str, set_id: str) -> dict:
    """
    针对简答题 (dist) 的组装函数。
    
    参数:
        fact_qa (dict): 包含 "question", "correct_answer"，以及可选 "wrong_answers" 的字典。
        context (str): 问题的上下文字符串。
        set_id (str): 当前数据条目的标识。

    返回:
        dict: 包含以下字段:
            - "system_prompt": 给模型的 system 提示
            - "user_prompt": 给模型的 user 提示
            - "correct_answer": 正确答案
            - "question_type": "fact:dist"
            - "q_id":"q_id"+"0"
    """
    question = fact_qa.get("question", "")
    correct_answer = fact_qa.get("correct_answer", "")
    
    original_q_id = fact_qa.get("q_id", "")
    new_q_id = f"{original_q_id}-{0}"

    # 使用 build_dist_prompt 来生成 system_prompt / user_prompt / correct_answer
    prompt = build_dist_prompt(question, context)

    # 更改 question_type 附加到返回的字典里
    prompt["question_type"] = "fact:dist"
    prompt["q_id"] = new_q_id

    return prompt

def _setup_fact_mcq(fact_qa: dict, context: str, set_id: str) -> dict:
    """
    针对多选题 (mcq) 的组装函数。

    参数:
        fact_qa (dict): 包含 "question", "correct_answer"，以及可选 "wrong_answers" 的字典。
        context (str): 问题的上下文字符串。
        set_id (str): 当前数据条目的标识。

    返回:
        dict: 在基础字段上还包含:
            - "system_prompt": 系统提示（要求模型返回 [A], [B], ...）
            - "user_prompt": 包含上下文、问题和枚举后的选项
            - "input_text": 实际给模型的 prompt
            - "options": 打乱顺序后的所有选项列表
            - "correct_index": 正确答案在 options 列表中的索引（用于后续评估）
            - "question_type": "fact:mcq"
            - "q_id":"q_id"+"1"
    """
    question = fact_qa.get("question", "")
    correct_answer = fact_qa.get("correct_answer", "")
    wrong_answers = fact_qa.get("wrong_answers", [])
    original_q_id = fact_qa.get("q_id", "")
    new_q_id = f"{original_q_id}-{1}"

    # def build_mcq_prompt(question: str, correct_answer: str, wrong_answers: list, context: str = "") -> dict:
    # 调用 build_mcq_prompt 构造完整的多选题提示
    prompt = build_mcq_prompt(
        question=question,
        correct_answer=correct_answer,
        wrong_answers=wrong_answers,
        context=context
    )
    
    # 可以把 question_type 附加到返回的字典里
    prompt["question_type"] = "fact:mcq"
    prompt["q_id"] = new_q_id

    return prompt


################################
def setup_fantom(df, args):
    """
    原先的 setup_fantom 逻辑：
    - 遍历 df 中的每一行
    - 根据 conversation_input_type ('short' 或 'full') 选用相应字段
    - 生成 prompt 并存到 inputs 列表
    - 同时存储到 qas 列表

    返回:
    - inputs: List[str]
    - qas: List[dict]
    """
    # 你可以把 FantomEvalAgent 里 setup_fantom 的核心代码复制到这
    # 只要把 self.fantom_df 改成传入的 df
    # 把 self.args 改成传入的 args
    # 返回 inputs, qas

    pass

class FantomDataset(Dataset):
    """
    PyTorch Dataset，用于后续 DataLoader 批量处理
    """
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]