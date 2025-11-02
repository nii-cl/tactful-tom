#!/usr/bin/env python3
"""
Dataset Justification Option Generator

This script generates justification options for the TactfulToM dataset using OpenAI API.
It processes conversation data and creates multiple-choice question options for justification questions.
"""

import openai
import os
import json
import re
import time
import textwrap
import argparse
from typing import Dict, List, Any, Optional


# Global OpenAI client
client = None


def init_openai_client(api_key: str):
    """Initialize OpenAI client with API key."""
    global client
    client = openai.OpenAI(api_key=api_key)


def clean_json_str(raw: str) -> str:
    """
    Clean GPT output to extract valid JSON.
    
    Args:
        raw (str): Raw GPT output string
        
    Returns:
        str: Cleaned JSON string
    """
    # Remove ```json ... ``` markers
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*$', '', raw)
    
    # Remove // comments
    raw = re.sub(r'//.*', '', raw)
    
    # Remove trailing commas
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    
    # Add missing closing brackets (simple heuristic)
    open_braces = raw.count('{')
    close_braces = raw.count('}')
    if open_braces > close_braces:
        raw += '}' * (open_braces - close_braces)
        
    return raw.strip()


def safe_parse_gpt_output(s: str) -> Dict[str, Any]:
    """
    Safely parse GPT output to JSON.
    
    Args:
        s (str): GPT output string
        
    Returns:
        dict: Parsed JSON object
    """
    try:
        cleaned = clean_json_str(s)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Cleaned string: {cleaned}")
        return {}


def generate_prompt_for_justification_options(json_path: str, set_id: str) -> str:
    """
    Generate prompt for justification options.
    
    Args:
        json_path (str): Path to conversation data JSON file
        set_id (str): Specific conversation set ID
        
    Returns:
        str: Formatted prompt for GPT
    """
    # Load JSON and find conversation by set_id
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conversation_data = next((item for item in data if item.get("set_id") == set_id), None)
    if conversation_data is None:
        raise ValueError(f"Set ID '{set_id}' not found in the JSON file")

    # Extract required fields
    extracted_data = {
        "set_id": conversation_data["set_id"],
        "topic": {
            "scenario": conversation_data["topic"]["scenario"],
            "situation_topic": conversation_data["topic"]["situation_topic"],
            "situation": conversation_data["topic"]["situation"],
            "lie_objective": conversation_data["topic"]["lie_objective"]
        },
        "relationship": conversation_data["relationship"],
        "characters": {
            "liar": conversation_data["characters"]["liar"],
            "target": conversation_data["characters"]["target"],
            "accomplice": conversation_data["characters"]["accomplice"],
            "observer": conversation_data["characters"]["observer"]
        },
        "lie": {
            "real_reason_c": conversation_data["lie"]["real_reason_c"],
            "lie_c": conversation_data["lie"]["lie_c"],
            "truth_c": conversation_data["lie"]["truth_c"]
        }
    }

    # Create formatted prompt
    formatted_prompt = textwrap.dedent(f"""
        You are an MC-Q&A generator.

        Your ONLY job is to transform one input JSON into one output JSON.

        INPUT
        A JSON object with the keys for a white-lie conversation
        {json.dumps(extracted_data, indent=2)}

        OUTPUT
        Return ONLY a JSON object whose top-level key equals the received set_id and whose value has EXACTLY this structure (no extra keys, no comments, no ``` wrappers):

        "{set_id}": {{
          "truth": {{
            "correct_answer": "<one sentence ≤30 words>",
            "wrong_answers": [
              "<Type-1 Literal Reason — simply restates the spoken lie as if it were true>",
              "<Type-2 Negative Feeling — blames dislike, annoyance, etc.>",
              "<Type-3 Random Excuse — plausible but unrelated>"
            ]
          }}
        }}

        LOGIC RULES  
        1. correct_answer(truth) = the genuine psychological reason the liar gives the lie, typically sparing feelings / maintaining harmony / avoiding awkwardness.  
        2. Wrong answers must be mutually exclusive, realistic English sentences ≤30 words, and MUST conform to the required type description.  
        3. Re-use the exact character names from input; preserve third-person narration.  
        4. Return only the JSON; no explanations, no extra keys.  

        CHECKLIST BEFORE YOU ANSWER  
        ✓ Top-level key = set_id  
        ✓ wrong_answers list length=3, order corresponds to Type-1/Type-2/Type-3  
        ✓ No duplicate sentences, no quotation marks around the whole JSON block  
    """).strip()

    return formatted_prompt


def call_gpt_for_options(prompt: str, model: str = "gpt-4", max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    Call GPT API to generate justification options.
    
    Args:
        prompt (str): Formatted prompt for GPT
        model (str): GPT model to use
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        dict: Generated options or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates multiple-choice question options."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            result = safe_parse_gpt_output(content)
            
            if result:
                return result
            else:
                print(f"Attempt {attempt + 1}: Failed to parse GPT output")
                
        except Exception as e:
            print(f"Attempt {attempt + 1}: API call failed - {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None


def process_single_conversation(json_path: str, set_id: str, output_path: str) -> bool:
    """
    Process a single conversation and generate justification options.
    
    Args:
        json_path (str): Path to conversation data JSON file
        set_id (str): Conversation set ID to process
        output_path (str): Path to output JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"=== Processing {set_id} ===")
    
    try:
        # Generate prompt
        prompt = generate_prompt_for_justification_options(json_path, set_id)
        
        # Call GPT API
        result = call_gpt_for_options(prompt)
        
        if not result:
            print(f"[FAILED] {set_id} - Could not generate options")
            return False
        
        # Load existing output data
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}
        
        # Merge new result
        existing_data.update(result)
        
        # Save updated data
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] {set_id} written to {output_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {set_id} - {e}")
        return False


def process_all_conversations(json_path: str, output_path: str, skip_existing: bool = True) -> Dict[str, bool]:
    """
    Process all conversations in the dataset.
    
    Args:
        json_path (str): Path to conversation data JSON file
        output_path (str): Path to output JSON file
        skip_existing (bool): Whether to skip already processed conversations
        
    Returns:
        dict: Results for each set_id (True=success, False=failed)
    """
    # Load conversation data
    with open(json_path, "r", encoding="utf-8") as f:
        conv_data = json.load(f)
    
    all_set_ids = [rec["set_id"] for rec in conv_data]
    
    # Load existing results if skipping
    processed_set_ids = set()
    if skip_existing and os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            processed_set_ids = set(existing_data.keys())
            print(f"Found {len(processed_set_ids)} already processed conversations")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    results = {}
    
    for set_id in all_set_ids:
        if skip_existing and set_id in processed_set_ids:
            print(f"[SKIP] {set_id} - already processed")
            results[set_id] = True
            continue
        
        success = process_single_conversation(json_path, set_id, output_path)
        results[set_id] = success
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    return results


def main():
    """Main function to run the justification option generator."""
    parser = argparse.ArgumentParser(description="Generate justification options for TactfulToM dataset")
    parser.add_argument("--input", "-i", required=True, 
                       help="Path to input conversation JSON file")
    parser.add_argument("--output", "-o", required=True,
                       help="Path to output justification options JSON file")
    parser.add_argument("--api-key", required=True,
                       help="OpenAI API key")
    parser.add_argument("--set-id", 
                       help="Process only specific set_id (optional)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                       help="Skip already processed conversations")
    parser.add_argument("--model", default="gpt-4",
                       help="GPT model to use (default: gpt-4)")
    
    args = parser.parse_args()
    
    # Initialize OpenAI client
    init_openai_client(args.api_key)
    
    if args.set_id:
        # Process single conversation
        success = process_single_conversation(
            args.input, args.set_id, args.output
        )
        if success:
            print(f"✅ Successfully processed {args.set_id}")
        else:
            print(f"❌ Failed to process {args.set_id}")
            return 1
    else:
        # Process all conversations
        print(f"Processing all conversations from {args.input}")
        results = process_all_conversations(
            args.input, args.output, args.skip_existing
        )
        
        # Print summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        failed_ids = [set_id for set_id, success in results.items() if not success]
        
        print(f"\n📊 Summary:")
        print(f"✅ Successful: {successful}/{total}")
        if failed_ids:
            print(f"❌ Failed: {', '.join(failed_ids)}")
        
        return 0 if successful == total else 1


if __name__ == "__main__":
    exit(main())