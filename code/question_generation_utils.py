"""
Question Generation Functions for TactfulToM Dataset

This module contains functions to generate different types of questions
for the TactfulToM (Theory of Mind) dataset, including comprehension,
justification, fact-based, belief, and various ToM-related questions.
"""

import json
import random
import os
from typing import Dict, List, Any, Optional


def load_justification_options(file_path: str) -> dict:
    """
    Load justification options file and organize it into a flat dictionary
    format: {set_id: option_dict, ...}
    
    Supports:
      • {"0-1-0-0": {...}, "0-1-0-1": {...}}   # Single large dict
      • [{"0-1-0-0": {...}}, {"0-1-0-1": {...}}] # List format
    
    Args:
        file_path (str): Path to the justification options JSON file
        
    Returns:
        dict: Flattened dictionary with set_id as keys
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # If file is already a dict, return directly
    if isinstance(raw, dict):
        return raw

    # If it's a list, merge internal small dicts
    if isinstance(raw, list):
        merged = {}
        for block in raw:
            if isinstance(block, dict):
                merged.update(block)
        return merged

    raise ValueError("Unsupported JSON structure in justification-options file.")


def generate_comprehensionQA(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate comprehension questions based on the conversation data.
    
    Args:
        data (dict): Conversation data containing characters and lie information
        
    Returns:
        dict: Dictionary with "comprehensionQA" key containing list of questions
    """
    liar = data["characters"]["liar"]
    accomplice = data["characters"]["accomplice"]
    target = data["characters"]["target"]

    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")

    if data.get("multiple_liar") is True:
        question = f"Was what {liar} and {accomplice} told {target}, '{lie}', true?"
    else:
        question = f"Was what {liar} told {target}, '{lie}', true?"
        
    comprehension_qa = {
        "question": question,
        "question_type": "comprehension",
        "correct_answer": "No",
        "wrong_answer": "Yes"
    }
    
    return {"comprehensionQA": [comprehension_qa]}


def generate_justificationQA(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate justification questions asking why characters told lies.
    
    Args:
        data (dict): Conversation data containing characters, lie info, and set_id
        
    Returns:
        dict: Dictionary with "justificationQA" key containing list of questions
    """
    set_id = data["set_id"]
    
    # Load justification options - you may need to adjust this path
    options_map = load_justification_options(
        f"/Users/liuyiwei/python/tactful-tom/dataset/justification_options/justification_option_4.json"
    )

    options = options_map.get(set_id)
    if options is None:
        # Provide available set_ids for debugging
        available = ", ".join(options_map.keys())
        raise ValueError(f"Options not found for set_id '{set_id}'. "
                         f"Available ids: {available}")

    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")

    if data.get("multiple_liar") is True:
        question_lie = f"Why did {liar} and {accomplice} tell {target} '{lie}'?"
        question_type = "justification:liar"
    else:
        question_lie = f"Why did {liar} tell {target} '{lie}'?"
        question_type = "justification:liar:accompliance"

    justification_qas = [
        {
            "question": question_lie,
            "question_type": question_type,
            "correct_answer": options["truth"]["correct_answer"],
            "wrong_answer": options["truth"]["wrong_answers"]
        }
    ]

    return {"justificationQA": justification_qas}


def generate_fact_QA(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate factual questions about who discussed what topics.
    
    Args:
        data (dict): Conversation data containing characters and conversation details
        
    Returns:
        dict: Dictionary with "fact_reasonQA" and "fact_truthQA" keys
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")
    
    truth_id = data["truth_id"]

    # Generate wrong answers for reason question
    # Make incorrect choices confusing by including liar and accomplice
    wrong_answer_reason = [
        f"{accomplice} and {target} talked about that.",
        f"{observer} and {liar} talked about that.",
        f"{observer} and {accomplice} talked about that.",
        f"{target} and {liar} talked about that.",
        f"{target}, {accomplice} and {liar} talked about that.",
        f"{liar}, {observer} and {accomplice} talked about that."
    ]

    random_wrong_answer_reason = random.sample(wrong_answer_reason, 3)

    # Reason QA (always generated)
    reason_qa = {
        "question": f"Who discussed '{real_reason}'?",
        "question_type": "fact:real_reason",
        "correct_answer": f"{liar} and {accomplice} talked about that.",
        "wrong_answer": random_wrong_answer_reason 
    }

    # Truth QA (only when truth_id == 1)
    truth_qa = None
    if truth_id == 1:
        truth = truth.rstrip(".")
        wrong_answer_truth = [
            f"{observer}, {accomplice} and {target} talked about that.",
            f"{observer}, {target} and {liar} talked about that.",
            f"{target}, {accomplice} and {liar} talked about that.",
            f"{liar} and {accomplice} talked about that",
            f"{observer} and {liar} talked about that",
            f"{observer} and {accomplice} talked about that",
        ]
        random_wrong_answer_truth = random.sample(wrong_answer_truth, 3)

        truth_qa = {
            "question": f"Who discussed '{truth}'?",
            "question_type": "fact:truth",
            "correct_answer": f"{liar}, {observer} and {accomplice} talked about that.",
            "wrong_answer": random_wrong_answer_truth
        }

    return {"fact_reasonQA": [reason_qa], "fact_truthQA": [truth_qa] if truth_qa else []}


def generate_1stbeliefQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate first-order belief questions about what characters believe.
    
    Args:
        data (dict): Conversation data containing characters and belief scenarios
        
    Returns:
        dict: Dictionary with "beliefQAs" key containing list of belief questions
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")
    
    truth_id = data["truth_id"]
    real_reason_question = f"Who discussed '{real_reason}'?"
    truth_question = f"Who discussed '{truth}'?" if truth_id == 1 else None

    belief_qas = []

    # First-order beliefs about real_reason
    # {liar}
    first_wrong_options_liar = [
        f"{liar} is unaware that {observer} discussed {real_reason}.",
        f"{liar} is unaware that {target} discussed {real_reason}.",
        f"{liar} is unaware that {observer} and {target} discussed {real_reason}."
    ]
    
    second_wrong_option_liar = [
        f"{liar} believes that {accomplice} and {observer} discussed {real_reason}.",
        f"{liar} believes that {accomplice} and {target} discussed {real_reason}.",
        f"{liar} believes that {observer} and {target} discussed {real_reason}."
    ]
    
    third_wrong_options_liar = [
        f"{liar} believes that {accomplice}, {observer} and {target} discussed {real_reason}.",
        f"{liar} believes that {observer} discussed {real_reason}.",
        f"{liar} believes that {target} discussed {real_reason}."
    ]

    belief_qas.append({
        "question": f"What does {liar} believe about '{real_reason_question}'?",
        "question_type": "tom:belief:accessible:reason",
        "tom_type": "first-order:A",
        "correct_answer": f"{liar} believes that {accomplice} discussed {real_reason}.",
        "wrong_answer": [
            random.choice(first_wrong_options_liar),
            random.choice(second_wrong_option_liar),
            random.choice(third_wrong_options_liar)
        ],
        "real_reason_accessibility": "accessible"
    })

    # {target}
    first_wrong_options_target = [
        f"{target} is unaware that {observer} discussed {real_reason}.",
        f"{target} is unaware that {liar} and {observer} discussed {real_reason}.",
        f"{target} is unaware that {accomplice} and {observer} discussed {real_reason}."
    ]
    
    second_wrong_option_target = [
        f"{target} believes that {liar} and {accomplice} discussed {real_reason}.",
        f"{target} believes that {liar} discussed {real_reason}.",
        f"{target} believes that {accomplice} discussed {real_reason}."
    ]
    
    third_wrong_options_target = [
        f"{target} believes that {accomplice}, {liar} and {observer} discussed {real_reason}.",
        f"{target} believes that {accomplice} and {observer} discussed {real_reason}.",
        f"{target} believes that {observer} discussed {real_reason}."
    ]

    belief_qas.append({
        "question": f"What does {target} believe about '{real_reason_question}'?",
        "question_type": "tom:belief:inaccessible:reason",
        "tom_type": "first-order:B",
        "correct_answer": f"{target} is unaware that {liar} and {accomplice} discussed {real_reason}.",
        "wrong_answer": [
            random.choice(first_wrong_options_target),
            random.choice(second_wrong_option_target),
            random.choice(third_wrong_options_target)
        ],
        "real_reason_accessibility": "inaccessible"
    })

    # {accomplice}
    first_wrong_options_accomplice = [
        f"{accomplice} believes that {observer} discussed {real_reason}.",
        f"{accomplice} believes that {target} discussed {real_reason}.",
        f"{accomplice} believes that {observer} and {target} discussed {real_reason}.",
        f"{accomplice} believes that {observer} and {liar} discussed {real_reason}.",
        f"{accomplice} believes that {liar} and {target} discussed {real_reason}.",
        f"{accomplice} believes that {liar}, {observer} and {target} discussed {real_reason}."
    ]
    
    second_wrong_option_accomplice = f"{accomplice} is unaware that {liar} discussed {real_reason}."
    
    third_wrong_options_accomplice = [
        f"{accomplice} is unaware that {observer} discussed {real_reason}.",
        f"{accomplice} is unaware that {target} discussed {real_reason}.",
        f"{accomplice} is unaware that {observer} and {target} discussed {real_reason}.",
        f"{accomplice} is unaware that {observer} and {liar} discussed {real_reason}.",
        f"{accomplice} is unaware that {liar} and {target} discussed {real_reason}.",
        f"{accomplice} is unaware that {liar}, {observer} and {target} discussed {real_reason}."
    ]
    
    belief_qas.append({
        "question": f"What does {accomplice} believe about '{real_reason_question}'?",
        "question_type": "tom:belief:accessible:reason",
        "tom_type": "first-order:C",
        "correct_answer": f"{accomplice} believes that {liar} discussed {real_reason}.",
        "wrong_answer": [
            random.choice(first_wrong_options_accomplice),
            second_wrong_option_accomplice,
            random.choice(third_wrong_options_accomplice)
        ],
        "real_reason_accessibility": "accessible"
    })

    # First-order beliefs about truth (if truth_id == 1)
    if truth_id == 1 and truth_question:
        # Add truth-related belief questions here
        # (Implementation similar to real_reason but for truth)
        pass

    return {"beliefQAs": belief_qas}


def generate_2ndbeliefQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate second-order belief questions about what characters believe others believe.
    
    Args:
        data (dict): Conversation data containing characters and belief scenarios
        
    Returns:
        dict: Dictionary with "beliefQAs" key containing list of second-order belief questions
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    
    truth_id = data["truth_id"]
    real_reason_question = f"Who discussed '{real_reason}'?"

    belief_qas = []

    # Second-order beliefs about real_reason
    # {target} about {observer}
    belief_qas.append({
        "question": f"What does {target} believe about {observer}'s belief regarding '{real_reason_question}'?",
        "question_type": "tom:belief:inaccessible:reason",
        "tom_type": "second-order:BD",
        "correct_answer": f"The text provides no information on what {target} believes about {observer}'s belief regarding that. Therefore, it can be stated that {target} is unaware that {observer} is unaware that {real_reason}.",
        "wrong_answer": [
            f"The text provides no information on what {target} believes about {observer}'s belief regarding that. Therefore, it can be stated that {target} is unaware that {observer} believes that {real_reason}.",
            f"{target} believes that {observer} is unaware that {real_reason}, because {observer} was not involved in the conversation when this was discussed.",
            f"{target} believes that {observer} believes that {real_reason}."
        ],
        "missed_info_accessibility": "inaccessible"
    })

    # {accomplice} about {liar}
    belief_qas.append({
        "question": f"What does {accomplice} believe about {liar}'s belief regarding '{real_reason_question}'?",
        "question_type": "tom:belief:accessible:reason",
        "tom_type": "second-order:CA",
        "correct_answer": f"{accomplice} believes that {liar} believes that {real_reason}.",
        "wrong_answer": [
            f"{accomplice} believes that {liar} is unaware that {real_reason}, because {liar} was not involved in the conversation when this was discussed.",
            f"The text provides no information on what {accomplice} believes about {liar}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {liar} is unaware that {real_reason}.",
            f"The text provides no information on what {accomplice} believes about {liar}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {liar} believes that {real_reason}."
        ],
        "real_reason_accessibility": "accessible"
    })

    # {accomplice} about {target}
    belief_qas.append({
        "question": f"What does {accomplice} believe about {target}'s belief regarding '{real_reason_question}'?",
        "question_type": "tom:belief:accessible:reason",
        "tom_type": "second-order:CB",
        "correct_answer": f"{accomplice} believes that {target} is unaware that {real_reason}, because {target} was not involved in the conversation when this was discussed.",
        "wrong_answer": [
            f"{accomplice} believes that {target} believes that {real_reason}.",
            f"The text provides no information on what {accomplice} believes about {target}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {target} is unaware that {real_reason}.",
            f"The text provides no information on what {accomplice} believes about {target}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {target} believes that {real_reason}."
        ],
        "real_reason_accessibility": "accessible"
    })

    # {accomplice} about {observer}
    belief_qas.append({
        "question": f"What does {accomplice} believe about {observer}'s belief regarding '{real_reason_question}'?",
        "question_type": "tom:belief:accessible:reason",
        "tom_type": "second-order:CD",
        "correct_answer": f"{accomplice} believes that {observer} is unaware that {real_reason}, because {observer} was not involved in the conversation when this was discussed.",
        "wrong_answer": [
            f"{accomplice} believes that {observer} believes that {real_reason}.",
            f"The text provides no information on what {accomplice} believes about {observer}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {target} is unaware that {real_reason}.",
            f"The text provides no information on what {accomplice} believes about {observer}'s belief regarding that. Therefore, it can be stated that {accomplice} is unaware that {target} believes that {real_reason}."
        ],
        "real_reason_accessibility": "accessible"
    })

    return {"beliefQAs": belief_qas}


def generate_infoAccessibilityQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate information accessibility questions about what information characters have access to.
    
    Args:
        data (dict): Conversation data containing characters and information scenarios
        
    Returns:
        dict: Dictionary with "infoAccessibilityQA_list" and "infoAccessibilityQAs_binary" keys
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    
    truth_id = data["truth_id"]

    info_accessibility_list = []
    info_accessibility_binary = []

    # Information accessibility for real_reason
    info_accessibility_list.append({
        "information": f"Who discussed '{real_reason}'?",
        "question": "List all the characters who have access to this information.",
        "question_type": "tom:info_accessibility:list:real_reason",
        "correct_answer": [liar, accomplice],
        "wrong_answer": [target, observer]
    })

    # Binary questions for each character
    for character in [liar, target, accomplice, observer]:
        correct_answer = "yes" if character in [liar, accomplice] else "no"
        info_accessibility_binary.append({
            "information": f"Who discussed '{real_reason}'?",
            "question": f"Does {character} have access to this information?",
            "question_type": "tom:info_accessibility:binary:real_reason",
            "correct_answer": correct_answer
        })

    # Information accessibility for truth (if truth_id == 1)
    if truth_id == 1:
        info_accessibility_list.append({
            "information": f"Who discussed '{truth}'?",
            "question": "List all the characters who have access to this information.",
            "question_type": "tom:info_accessibility:list:truth",
            "correct_answer": [liar, observer, accomplice],
            "wrong_answer": [target]
        })

        # Binary questions for truth
        for character in [liar, target, accomplice, observer]:
            correct_answer = "yes" if character in [liar, observer, accomplice] else "no"
            info_accessibility_binary.append({
                "information": f"Who discussed '{truth}'?",
                "question": f"Does {character} have access to this information?",
                "question_type": "tom:info_accessibility:binary:truth",
                "correct_answer": correct_answer
            })

    return {
        "infoAccessibilityQA_list": info_accessibility_list,
        "infoAccessibilityQAs_binary": info_accessibility_binary
    }


def generate_answerabilityQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate answerability questions about whether characters can answer specific questions.
    
    Args:
        data (dict): Conversation data containing characters and question scenarios
        
    Returns:
        dict: Dictionary with "answerabilityQA_list" and "answerabilityQAs_binary" keys
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    
    truth_id = data["truth_id"]

    answerability_list = []
    answerability_binary = []

    # Answerability for real_reason question
    answerability_list.append({
        "fact_question_real_reason": f"Who discussed '{real_reason}'?",
        "question": "List all the characters who know the precise correct answer to this question.",
        "question_type": "tom:answerability:list:real_reason",
        "correct_answer": [liar, accomplice],
        "wrong_answer": [target, observer]
    })

    # Binary answerability questions for real_reason
    for character in [liar, target, accomplice, observer]:
        correct_answer = "yes" if character in [liar, accomplice] else "no"
        answerability_binary.append({
            "fact_question_real_reason": f"Who discussed '{real_reason}'?",
            "question": f"Does {character} know the precise correct answer to this question?",
            "question_type": "tom:answerability:binary:real_reason",
            "correct_answer": correct_answer
        })

    # Answerability for truth question (if truth_id == 1)
    if truth_id == 1:
        answerability_list.append({
            "fact_question_truth": f"Who discussed '{truth}'?",
            "question": "List all the characters who know the precise correct answer to this question.",
            "question_type": "tom:answerability:list:truth",
            "correct_answer": [liar, observer, accomplice],
            "wrong_answer": [target]
        })

        # Binary answerability questions for truth
        for character in [liar, target, accomplice, observer]:
            correct_answer = "yes" if character in [liar, observer, accomplice] else "no"
            answerability_binary.append({
                "fact_question_truth": f"Who discussed '{truth}'?",
                "question": f"Does {character} know the precise correct answer to this question?",
                "question_type": "tom:answerability:binary:truth",
                "correct_answer": correct_answer
            })

    return {
        "answerabilityQA_list": answerability_list,
        "answerabilityQAs_binary": answerability_binary
    }


def generate_liedetectabilityQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate lie detectability questions about whether characters can detect lies.
    
    Args:
        data (dict): Conversation data containing characters and lie scenarios
        
    Returns:
        dict: Dictionary with "liedetectabilityQAs_list" and "liedetectabilityQAs_binary" keys
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    observer = data["characters"]["observer"]
    
    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")
    
    truth_id = data["truth_id"]

    liedetectability_list = []
    liedetectability_binary = []

    # Generate comprehension question for lie detectability
    if data.get("multiple_liar") is True:
        comprehension_q = f"Was what {liar} and {accomplice} told {target}, '{lie}', true?"
    else:
        comprehension_q = f"Was what {liar} told {target}, '{lie}', true?"

    # List question
    liedetectability_list.append({
        "comprehension_q": comprehension_q,
        "question": "List all the characters who know the precise correct answer to this question.",
        "question_type": "tom:liedetectability:list",
        "correct_answer": [liar, accomplice],
        "wrong_answer": [target, observer]
    })

    # Binary questions for each character
    for character in [liar, target, accomplice, observer]:
        correct_answer = "yes" if character in [liar, accomplice] else "no"
        liedetectability_binary.append({
            "comprehension_q": comprehension_q,
            "question": f"Does {character} know the precise correct answer to this question?",
            "question_type": "tom:liedetectability:binary",
            "correct_answer": correct_answer
        })

    return {
        "liedetectabilityQAs_list": liedetectability_list,
        "liedetectabilityQAs_binary": liedetectability_binary
    }


def generate_lieabilityQAs(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate lie ability questions about why characters are able to lie successfully.
    
    Args:
        data (dict): Conversation data containing characters and lie scenarios
        
    Returns:
        dict: Dictionary with "lieabilityQAs" key containing list of lie ability questions
    """
    liar = data["characters"]["liar"]
    target = data["characters"]["target"]
    accomplice = data["characters"]["accomplice"]
    
    truth_id = data["truth_id"]
    
    real_reason = (data["lie"].get("real_reason_q") or data["lie"]["real_reason_c"]).rstrip(".")
    truth = data["lie"].get("truth_q") or data["lie"]["truth_c"].rstrip(".")
    lie = (data["lie"].get("lie_q") or data["lie"]["lie_c"]).rstrip(".")

    lieability = []

    # Question based on real_reason
    first_wrong_option_real_reason = f"{liar} tell {target} that '{lie}' because {liar} believes that {target} believes {real_reason}."
    second_wrong_option_real_reason = f"{liar} tell {target} that '{lie}' because {liar} is unaware that {target} is unaware that {real_reason}."
    third_wrong_option_real_reason = f"{liar} tell {target} that '{lie}' because {liar} is unaware that {target} believes {real_reason}."

    lieability.append({
        "question": f"Please choose the correct answer from the options below:",
        "question_type": "tom:lieability:liar:real_reason",
        "correct_answer": f"{liar} tell {target} that '{lie}' because {liar} believes that {target} is unaware that {real_reason}.",
        "wrong_answer": [
            first_wrong_option_real_reason,
            second_wrong_option_real_reason,
            third_wrong_option_real_reason
        ],
    })

    # Question based on truth (if truth_id == 1)
    if truth_id == 1:
        first_wrong_option_truth_liar = f"{liar} tell {target} that '{lie}' because {liar} believes that {target} believes {truth}."
        second_wrong_option_truth_liar = f"{liar} tell {target} that '{lie}' because {liar} is unaware that {target} is unaware that {truth}."
        third_wrong_option_truth_liar = f"{liar} tell {target} that '{lie}' because {liar} is unaware that {target} believes {truth}."

        lieability.append({
            "question": f"Please choose the correct answer from the options below:",
            "question_type": "tom:lieability:liar:truth",
            "correct_answer": f"{liar} tell {target} that '{lie}' because {liar} believes that {target} is unaware that {truth}.",
            "wrong_answer": [
                first_wrong_option_truth_liar,
                second_wrong_option_truth_liar,
                third_wrong_option_truth_liar
            ],
        })

    return {"lieabilityQAs": lieability}


def merge_beliefQAs(d1: Dict[str, List], d2: Dict[str, List]) -> Dict[str, List]:
    """
    Merge two belief QA dictionaries by combining their "beliefQAs" lists.
    
    Args:
        d1 (dict): First dictionary with "beliefQAs" key
        d2 (dict): Second dictionary with "beliefQAs" key
        
    Returns:
        dict: Merged dictionary with combined "beliefQAs" list
    """
    return {
        "beliefQAs": d1["beliefQAs"] + d2["beliefQAs"]
    }


def assign_question_ids(new_entry: Dict[str, Any], set_id: str) -> Dict[str, Any]:
    """
    Assign unique question IDs to all questions in the entry.
    
    Assumes the following fields are stored as lists:
      - beliefQAs
      - infoAccessibilityQA_list
      - infoAccessibilityQAs_binary
      - answerabilityQA_list
      - answerabilityQAs_binary
      - liedetectabilityQAs_list
      - liedetectabilityQAs_binary
      - lieabilityQAs
    
    Args:
        new_entry (dict): Dictionary containing multiple QA lists
        set_id (str): Used as q_id prefix (e.g., "0-0-0")
        
    Returns:
        dict: Modified dictionary with "q_id" field added to each question
    """
    # comprehensionQA
    if "comprehensionQA" in new_entry:
        for i, q_dict in enumerate(new_entry["comprehensionQA"]):
            q_dict["q_id"] = f"{set_id}-comprehension-{i}"

    # justificationQA
    if "justificationQA" in new_entry:
        for i, q_dict in enumerate(new_entry["justificationQA"]):
            q_dict["q_id"] = f"{set_id}-justification-{i}"

    # reasonQA
    if "fact_reasonQA" in new_entry:
        for i, q_dict in enumerate(new_entry["fact_reasonQA"]):
            q_dict["q_id"] = f"{set_id}-fact_reason-{i}"

    # truthQA
    if "fact_truthQA" in new_entry:
        for i, q_dict in enumerate(new_entry["fact_truthQA"]):
            q_dict["q_id"] = f"{set_id}-fact_truth-{i}"

    # beliefQAs
    if "beliefQAs" in new_entry:
        for i, q_dict in enumerate(new_entry["beliefQAs"]):
            q_dict["q_id"] = f"{set_id}-belief-{i}"

    # infoAccessibilityQA_list
    if "infoAccessibilityQA_list" in new_entry:
        for i, q_dict in enumerate(new_entry["infoAccessibilityQA_list"]):
            q_dict["q_id"] = f"{set_id}-info_access_list-{i}"

    # infoAccessibilityQAs_binary
    if "infoAccessibilityQAs_binary" in new_entry:
        for i, q_dict in enumerate(new_entry["infoAccessibilityQAs_binary"]):
            q_dict["q_id"] = f"{set_id}-info_access_binary-{i}"

    # answerabilityQA_list
    if "answerabilityQA_list" in new_entry:
        for i, q_dict in enumerate(new_entry["answerabilityQA_list"]):
            q_dict["q_id"] = f"{set_id}-answerability_list-{i}"

    # answerabilityQAs_binary
    if "answerabilityQAs_binary" in new_entry:
        for i, q_dict in enumerate(new_entry["answerabilityQAs_binary"]):
            q_dict["q_id"] = f"{set_id}-answerability_binary-{i}"

    # liedetectabilityQAs_list
    if "liedetectabilityQAs_list" in new_entry:
        for i, q_dict in enumerate(new_entry["liedetectabilityQAs_list"]):
            q_dict["q_id"] = f"{set_id}-liedetect_list-{i}"

    # liedetectabilityQAs_binary
    if "liedetectabilityQAs_binary" in new_entry:
        for i, q_dict in enumerate(new_entry["liedetectabilityQAs_binary"]):
            q_dict["q_id"] = f"{set_id}-liedetect_binary-{i}"

    # lieabilityQAs
    if "lieabilityQAs" in new_entry:
        for i, q_dict in enumerate(new_entry["lieabilityQAs"]):
            q_dict["q_id"] = f"{set_id}-lieability-{i}"

    return new_entry
