"""
Utility functions for conversation generation in Tactful ToM dataset.
This module contains helper functions for template population, character name replacement,
and data management for generated conversations.
"""

import os
import json
import re


def populate_template(template, scenario, relationship, situation, lie_objective, 
                     real_reason_c, lie_c, truth_c, situation_topic,
                     leave_reason_B, leave_reason_D_1, leave_reason_D_2,
                     A_name, B_name, C_name, D_name):
    """
    Populate conversation template with provided variables.
    
    Args:
        template: Template string with placeholders
        scenario: Conversation scenario description
        relationship: Character relationships
        situation: Specific situation description
        lie_objective: Objective of the lie
        real_reason_c: Real reason for the lie
        lie_c: The lie content
        truth_c: The truth/fact content
        situation_topic: Topic for the situation
        leave_reason_B: Reason for B to leave
        leave_reason_D_1: First reason for D to leave
        leave_reason_D_2: Second reason for D to leave
        A_name: Name of character A (liar)
        B_name: Name of character B (target)
        C_name: Name of character C (accomplice)
        D_name: Name of character D (observer)
        
    Returns:
        str: Populated template string
    """
    return template.replace("{{Topic for the scenario}}", scenario)\
                   .replace("{{relationship descriptor}}", relationship)\
                   .replace("{{A: the liar name}}", A_name)\
                   .replace("{{B: the target name}}", B_name)\
                   .replace("{{C: the accomplice name}}", C_name)\
                   .replace("{{D: the observer name}}", D_name)\
                   .replace("{{leave reason B}}", leave_reason_B)\
                   .replace("{{leave reason D_1}}", leave_reason_D_1)\
                   .replace("{{leave reason D_2}}", leave_reason_D_2)\
                   .replace("{{real_reason_c}}", real_reason_c)\
                   .replace("{{truth_c}}", truth_c if truth_c is not None else "")\
                   .replace("{{the lie}}", lie_c)\
                   .replace("{{situation_topic}}", situation_topic)\
                   .replace("{{situation}}", situation)\
                   .replace("{{lie_objective}}", lie_objective)


def replace_ABCD_with_name(text, A_name, B_name, C_name, D_name):
    """
    Replace character placeholders (A, B, C, D) with actual names in text.
    Handles both regular names (e.g., "A") and possessive forms (e.g., "A's").
    Uses one-pass replacement to avoid repeated substitutions.
    
    Args:
        text: Input text containing A, B, C, D placeholders
        A_name: Name to replace A with
        B_name: Name to replace B with
        C_name: Name to replace C with
        D_name: Name to replace D with
        
    Returns:
        str: Text with placeholders replaced by names
    """
    mapping = {
        "A": A_name,
        "B": B_name,
        "C": C_name,
        "D": D_name
    }
    
    pattern = re.compile(r"(A's|B's|C's|D's|A|B|C|D)")
    
    def replacer(match):
        token = match.group(0)
        if token.endswith("'s"):
            letter = token[0]
            return mapping[letter] + "'s"
        else:
            return mapping[token]
    
    return pattern.sub(replacer, text)


def append_data_to_json(data_dict, filename):
    """
    Append a data dictionary to a JSON file.
    If the file doesn't exist, creates a new file.
    If the file exists but is not valid JSON, initializes as empty list.
    
    Args:
        data_dict: Dictionary to append to the JSON file
        filename: Path to the JSON file
        
    Returns:
        None
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data_list = json.load(f)
                if not isinstance(data_list, list):
                    data_list = []
            except json.JSONDecodeError:
                data_list = []
    else:
        data_list = []
    
    data_list.append(data_dict)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


def get_leave_reasons():
    """
    Get the list of leave reasons used in conversation generation.
    
    Returns:
        list: List of leave reason strings
    """
    leave_reasons = [
        "bathroom break",
        "coffee break",
        "forgot something important",
        "forgot to print some documents",
        "forgot to recieve a package",
        "forgot to return a package",
        "forgot to run errands",
        "forgot to submit documents",
        "have a meeting starting soon that I need to prepare for",
        "have a previous engagement that I need to attend to quickly",
        "have a work-related emergency that requires my immediate attention",
        "have an unexpected visitor at my door",
        "have errands to run",
        "have to attend to someone who just walked in",
        "have to check on something",
        "have to go to the restroom",
        "have to pick up a prescription",
        "have to pick up dry cleaning",
        "have to print or scan documents",
        "have to receive a delivery",
        "have to recharge laptop",
        "have to return a borrowed item",
        "have to take care of a family matter",
        "have to take care of an unexpected task",
        "have unexpected visitor",
        "his/her pet needs attention",
        "his/her family is calling",
        "incoming delivery",
        "must respond to a phone call",
        "need to check on a friend or family member who needs assistance",
        "need to finish a task that's time-sensitive",
        "need to get a phone call",
        "need to get some coffee",
        "need to go to the toilet",
        "need to grab a snack or a drink",
        "need to have a quick chat with someone else",
        "need to make a phone call",
        "need to make a quick trip to the drug store",
        "need to make a quick trip to the grocery store",
        "need to pick up a package",
        "need to receive a parcel",
        "need to recharge cellphone",
        "need to register for an event",
        "need to schedule a haircut or salon appointment",
        "need to schedule another appointment",
        "need to step out for a moment",
        "need to submit some papers",
        "need to take care of some paperwork or documents",
        "need to take care of some personal matters",
        "need to take care of something urgent",
        "need to troubleshoot something",
        "parking meter expiring",
        "remembered something that needs to be taken care of",
        "remembered to receive a package",
        "remembered to submit some papers",
        "remembered to take care of some paperwork or documents",
        "remembered to take care of some personal matters",
        "remembered to take care of something urgent",
        "want to go grab a drink",
        "want to go grab a coffee",
        "want to go take some fresh air",
        "want to go to the bathroom",
        "need to move my car",
        "have to take an urgent call from my boss",
        "need to check my emails quickly",
        "have to respond to an important message",
        "need to restart my computer",
        "have to take a quick medication",
        "need to handle a minor household emergency",
        "have to refill my water bottle",
        "have to feed my pet",
        "have to water my plants",
        "have to take a brief walk to clear my mind",
        "need to step outside briefly to meet someone",
        "have to adjust the thermostat",
        "need to quickly tidy up my workspace",
        "need to quickly verify something important",
        "have to quickly arrange something for a later meeting",
        "need to briefly step out to confirm travel arrangements",
        "have to take care of an urgent email",
        "have to briefly assist a coworker",
        "need to briefly leave to verify appointment details",
        "have to briefly tend to something outside",
        "have to quickly reschedule an upcoming meeting",
        "need to briefly attend to my child",
        "need to grab a quick snack",
        "need to quickly stretch my legs",
        "have to briefly troubleshoot my internet connection",
        "have to briefly step out for privacy reasons",
        "need to quickly tidy the room before another meeting",
        "have to quickly update someone about my status",
        "need to briefly review notes or materials",
        "have to briefly leave to answer an urgent text",
        "have to briefly assist someone else in the household",
        "have to quickly plug in my device to charge",
        "need to briefly leave to retrieve an important item",
        "have to step away briefly to close a window or door",
        "need to quickly ensure I turned off an appliance",
        "have to briefly step away for a personal reason",
        "need to briefly step away due to allergy or health symptoms"
    ]
    return leave_reasons


def load_conversation_elements(filepath):
    """
    Load conversation elements from a JSON file.
    
    Args:
        filepath: Path to the JSON file containing conversation elements
        
    Returns:
        list: List of conversation element dictionaries
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    return data_list


def extract_data_fields(data):
    """
    Extract and organize all fields from a conversation element dictionary.
    
    Args:
        data: Dictionary containing conversation element data
        
    Returns:
        dict: Organized dictionary with all extracted fields
    """
    extracted = {
        "set_id": data["set_id"],
        "lie_id": data["lie_id"],
        "conv_id": data["conv_id"],
        "truth_id": data["truth_id"],
        "lie_type": data["lie_type"],
        "emotion": data["emotion"],
        "topic": {
            "scenario": data["topic"]["scenario"],
            "situation_topic": data["topic"]["situation_topic"],
            "situation": data["topic"]["situation"],
            "lie_objective": data["topic"]["lie_objective"],
            "leave_reason_B": data["topic"]["leave_reason_B"],
            "leave_reason_D_1": data["topic"]["leave_reason_D_1"],
            "leave_reason_D_2": data["topic"]["leave_reason_D_2"],
        },
        "relationship": data["relationship"],
        "characters": {
            "liar": data["characters"]["liar"],
            "target": data["characters"]["target"],
            "accomplice": data["characters"]["accomplice"],
            "observer": data["characters"]["observer"]
        },
        "lie": {
            "real_reason_c": data["lie"]["real_reason_c"],
            "lie_c": data["lie"]["lie_c"],
            "truth_c": data["lie"]["truth_c"],
            "falsification": data["lie"]["falsification"]
        }
    }
    return extracted

