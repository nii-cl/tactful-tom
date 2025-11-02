#!/usr/bin/env python3
"""
Replace _c content with _q content in generated questions

Problem:
- Questions were generated using _c (context) field content
- Should have used _q (question) field content
- Need to find and replace _c content with _q content in the generated questions

This script:
1. Reads the source data (elements or justification_options)
2. For each item, finds where _c content appears in questions
3. Replaces it with the corresponding _q content
"""

import json
import re
from typing import Dict, Any, List, Tuple
from pathlib import Path


def load_json(path: str) -> List[Dict]:
    """Load JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: List[Dict]):
    """Save JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_replacement_pairs(item: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Extract (_c content, _q content) pairs from an item.
    
    Returns:
        List of (old_content, new_content) tuples
    """
    if "lie" not in item or not isinstance(item["lie"], dict):
        return []
    
    lie_dict = item["lie"]
    pairs = []
    
    for field_base in ["real_reason", "lie", "truth"]:
        c_field = f"{field_base}_c"
        q_field = f"{field_base}_q"
        
        c_content = lie_dict.get(c_field, "").strip()
        q_content = lie_dict.get(q_field, "").strip()
        
        # Only create pair if both exist and are different
        if c_content and q_content and c_content != q_content:
            pairs.append((c_content, q_content))
    
    return pairs


def replace_in_string(text: str, old: str, new: str) -> Tuple[str, bool]:
    """
    Replace old content with new content in text.
    Returns (new_text, was_modified)
    """
    if not text or not old:
        return text, False
    
    # Try exact match first
    if old in text:
        return text.replace(old, new), True
    
    # Try case-insensitive match
    pattern = re.escape(old)
    if re.search(pattern, text, re.IGNORECASE):
        new_text = re.sub(pattern, new, text, flags=re.IGNORECASE)
        return new_text, True
    
    return text, False


def replace_in_value(value: Any, replacement_pairs: List[Tuple[str, str]]) -> Tuple[Any, int]:
    """
    Recursively replace content in a value.
    Returns (new_value, num_replacements)
    """
    num_replacements = 0
    
    if isinstance(value, str):
        for old_content, new_content in replacement_pairs:
            value, was_modified = replace_in_string(value, old_content, new_content)
            if was_modified:
                num_replacements += 1
        return value, num_replacements
    
    elif isinstance(value, dict):
        new_dict = {}
        for k, v in value.items():
            new_dict[k], count = replace_in_value(v, replacement_pairs)
            num_replacements += count
        return new_dict, num_replacements
    
    elif isinstance(value, list):
        new_list = []
        for item in value:
            new_item, count = replace_in_value(item, replacement_pairs)
            new_list.append(new_item)
            num_replacements += count
        return new_list, num_replacements
    
    else:
        return value, 0


def analyze_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze what would be replaced in an item.
    
    Returns analysis results including:
    - replacement_pairs: list of (old, new) pairs
    - fields_with_matches: fields that contain _c content
    """
    set_id = item.get("set_id", "unknown")
    replacement_pairs = get_replacement_pairs(item)
    
    if not replacement_pairs:
        return {
            "set_id": set_id,
            "has_replacements": False,
            "num_pairs": 0,
            "replacement_pairs": []
        }
    
    # Find which fields contain the _c content
    fields_with_matches = []
    
    for field_name, field_value in item.items():
        if field_name in ["lie", "set_id", "characters"]:
            continue
        
        # Check if this field contains any _c content
        for old_content, new_content in replacement_pairs:
            if isinstance(field_value, (str, dict, list)):
                str_repr = json.dumps(field_value, ensure_ascii=False) if not isinstance(field_value, str) else field_value
                if old_content in str_repr:
                    fields_with_matches.append({
                        "field": field_name,
                        "old_content": old_content[:50] + "..." if len(old_content) > 50 else old_content,
                        "new_content": new_content[:50] + "..." if len(new_content) > 50 else new_content
                    })
    
    return {
        "set_id": set_id,
        "has_replacements": len(fields_with_matches) > 0,
        "num_pairs": len(replacement_pairs),
        "replacement_pairs": replacement_pairs,
        "fields_with_matches": fields_with_matches
    }


def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a file to see what would be replaced.
    """
    print(f"\n=== Analyzing {file_path} ===")
    
    data = load_json(file_path)
    
    total_items = len(data)
    items_with_replacements = 0
    total_matches = 0
    
    detailed_results = []
    
    for item in data:
        analysis = analyze_item(item)
        if analysis["has_replacements"]:
            items_with_replacements += 1
            total_matches += len(analysis["fields_with_matches"])
            detailed_results.append(analysis)
    
    print(f"Total items: {total_items}")
    print(f"Items with _c content in questions: {items_with_replacements}")
    print(f"Total field matches found: {total_matches}")
    
    if detailed_results and items_with_replacements <= 5:
        print("\nDetailed matches:")
        for result in detailed_results:
            print(f"\n  Set {result['set_id']}:")
            for match in result["fields_with_matches"]:
                print(f"    Field: {match['field']}")
                print(f"      Old: {match['old_content']}")
                print(f"      New: {match['new_content']}")
    
    return {
        "file_path": file_path,
        "total_items": total_items,
        "items_with_replacements": items_with_replacements,
        "total_matches": total_matches,
        "detailed_results": detailed_results
    }


def replace_in_file(input_path: str, output_path: str = None, backup: bool = True, verbose: bool = True) -> bool:
    """
    Replace _c content with _q content in a file.
    
    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file (default: same as input)
        backup: Whether to create backup before modifying
        verbose: Whether to print detailed replacement information
    """
    if output_path is None:
        output_path = input_path
    
    print(f"\n{'='*80}")
    print(f"Processing: {input_path}")
    print(f"{'='*80}")
    
    # Load data
    try:
        data = load_json(input_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False
    
    # Create backup
    if backup and input_path == output_path:
        backup_path = input_path + ".backup"
        try:
            save_json(backup_path, data)
            print(f"✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    # Process each item
    total_replacements = 0
    modified_items = 0
    all_replacements = []  # Store all replacement details
    
    for item in data:
        replacement_pairs = get_replacement_pairs(item)
        if not replacement_pairs:
            continue
        
        set_id = item.get("set_id", "unknown")
        item_replacements = 0
        item_details = []
        
        # Replace in all fields except 'lie', 'set_id', 'characters'
        for field_name in list(item.keys()):
            if field_name in ["lie", "set_id", "characters"]:
                continue
            
            old_value = item[field_name]
            new_value, count = replace_in_value(old_value, replacement_pairs)
            
            if count > 0:
                item[field_name] = new_value
                item_replacements += count
                
                # Track which fields were modified
                if verbose:
                    for old_content, new_content in replacement_pairs:
                        # Check if this pair was actually used in this field
                        if isinstance(old_value, str) and old_content in old_value:
                            item_details.append({
                                'field': field_name,
                                'old': old_content,
                                'new': new_content
                            })
                        elif isinstance(old_value, (dict, list)):
                            str_repr = json.dumps(old_value, ensure_ascii=False)
                            if old_content in str_repr:
                                item_details.append({
                                    'field': field_name,
                                    'old': old_content,
                                    'new': new_content
                                })
        
        if item_replacements > 0:
            modified_items += 1
            total_replacements += item_replacements
            all_replacements.append({
                'set_id': set_id,
                'count': item_replacements,
                'details': item_details
            })
            
            if verbose:
                print(f"\n📝 Set {set_id}: {item_replacements} replacement(s)")
                for detail in item_details:
                    print(f"   Field: {detail['field']}")
                    print(f"   Old: '{detail['old'][:80]}{'...' if len(detail['old']) > 80 else ''}'")
                    print(f"   New: '{detail['new'][:80]}{'...' if len(detail['new']) > 80 else ''}'")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total items processed: {len(data)}")
    print(f"Items modified: {modified_items}")
    print(f"Total replacements: {total_replacements}")
    
    if modified_items > 0:
        print(f"\nModified items:")
        for repl in all_replacements:
            print(f"  • {repl['set_id']}: {repl['count']} replacement(s)")
    
    # Save
    try:
        save_json(output_path, data)
        print(f"\n✅ Successfully saved to: {output_path}")
        if backup and input_path == output_path:
            print(f"💾 Backup available at: {output_path}.backup")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


def main():
    """Main function with CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Replace _c content with _q content in generated questions"
    )
    parser.add_argument("--input", "-i", required=True,
                       help="Input JSON file")
    parser.add_argument("--output", "-o",
                       help="Output JSON file (default: same as input)")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze without modifying")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup before modifying")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Quiet mode: minimal output")
    
    args = parser.parse_args()
    
    if args.analyze_only:
        analyze_file(args.input)
    else:
        replace_in_file(
            args.input, 
            args.output, 
            backup=not args.no_backup,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    main()

