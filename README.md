# TactfulToM: Evaluating Theory of Mind Understanding of White Lies in Large Language Models

[![Paper](https://img.shields.io/badge/Paper-arXiv-red.svg)](https://aclanthology.org/2025.emnlp-main.1272/)
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow.svg)](https://github.com/nii-cl/tactful-tom)

## TL;DR

We introduce **TactfulToM**, a novel benchmark evaluating LLMs' Theory of Mind ability to understand and reason about white lies in real-life conversations, uncovering their limited understanding of white lies and the motivations behind them.

## Abstract

While recent studies explore Large Language Models' (LLMs) performance on Theory of Mind (ToM) reasoning tasks, research on ToM abilities that require more nuanced social context is limited, such as white lies. We introduce **TactfulToM**, a novel English benchmark designed to evaluate LLMs' ability to understand white lies within real-life conversations and reason about prosocial motivations behind them, particularly when they are used to spare others' feelings and maintain social harmony. Our benchmark is generated through a multi-stage human-in-the-loop pipeline where LLMs expand manually designed seed stories into conversations to maintain the information asymmetry between participants necessary for authentic white lies. We show that TactfulToM is challenging for state-of-the-art models, which perform substantially below humans, revealing shortcomings in their ability to fully comprehend the ToM reasoning that enables true understanding of white lies.

## 🎯 Overview

![TactfulToM Overview](figures/page_one_figure.png)

### Key Features

- 🗣️ **Real-life Conversations**: Natural, multi-turn dialogues with authentic white lies
- 🎭 **Information Asymmetry**: Carefully designed scenarios where different participants have access to different information
- 🧠 **Multi-level ToM Reasoning**: Questions spanning white lie understanding, white lie reasoning, and belief tracking
- 📊 **Diverse Categories**: Two main types of white lies:
  - **Altruistic White Lies**: Lies told purely for the benefit of others, where the liar may incur some personal cost or disadvantage
  - **Pareto White Lies**: Lies that create a mutually beneficial outcome, serving both the interests of the person being lied to and the liar themselves
- ✅ **Human-in-the-Loop**: Generated through a rigorous multi-stage pipeline with human validation

## 📁 Repository Structure

```
tactful-tom-main/
├── code/
│   ├── evaluate_freeform.py              # Evaluation for short-answer questions
│   ├── evaluate_non_freeform.py          # Evaluation for multiple-choice questions
│   ├── question_generation.ipynb         # Question generation pipeline
│   ├── question_generation_utils.py      # Question generation utilities
│   ├── justification_option_generator.py # Generate justification options
│   ├── replace_c_with_q_content.py       # Data cleaning utility
│   └── utils.py                          # General utilities
├── dataset/
│   ├── elements/                         # Raw conversation elements
│   ├── justification_options/            # Generated options
│   └── final_set/                        # Complete dataset
├── figures/                              # Result visualizations
├── environment.yml                       # Conda environment
└── README.md                            # This file
```

## 📊 Dataset

### Statistics

- **Total Conversations**: 100 unique scenarios
- **Total Questions**: 6,000+ multi-choice and short-answer questions
- **Question Types**:
  - Comprehension (detecting the lie)
  - Justification (understanding motivations)
  - Fact Tracking, Information Accessibility, and Answerability (who knows what)
  - Belief States (first-order and second-order ToM)
  - Lie Detection Ability (who can detect the lie based on each character's belief)
  - Lie Ability (who can lie based on each character's belief)

### Dataset Structure

```
dataset/
├── elements/               # Raw conversation elements by category
│   ├── Tactful_conv_element_0.json  # Pareto white lies
│   ├── Tactful_conv_element_1.json  # Altruistic - childhood imagination
│   ├── Tactful_conv_element_2.json  # Altruistic - emotional soothing
│   ├── Tactful_conv_element_3.json  # Altruistic - avoiding distress
│   └── Tactful_conv_element_4.json  # Altruistic - social harmony
├── justification_options/  # Generated justification options
│   └── justification_option_*.json
└── final_set/             # Completed dataset with all questions
    └── Tactful_conv_set_*.json
```

### Data Format

Each conversation includes:

```json
{
  "set_id": "unique_identifier",
  "characters": {
    "liar": "Character who tells the white lie",
    "target": "Character being protected by the lie",
    "accomplice": "Character who helps maintain the lie (if any)",
    "observer": "Neutral observer character"
  },
  "lie": {
    "real_reason_q": "The true prosocial motivation",
    "lie_q": "What was said (the white lie)",
    "truth_q": "The actual truth being concealed"
  },
  "full_context": "Complete conversation transcript",
  "comprehensionQA": [...],
  "justificationQA": [...],
  "beliefQAs": [...],
  // ... more question types
}
```

## 🚀 Installation


### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/tactful-tom.git
cd tactful-tom

# Create a virtual environment
conda env create -f environment.yml
conda activate tactful-tom

# Or use pip
pip install -r requirements.txt
```

## 💻 Usage

### Running Evaluation

```python
# Evaluate on non-freeform (multiple choice) questions
python code/evaluate_non_freeform.py \
    --model gpt-4 \
    --dataset_path dataset/final_set/Tactful_conv_set_0.json \
    --output_dir results/

# Evaluate on freeform (short answer) questions
python code/evaluate_freeform.py \
    --model gpt-4 \
    --dataset_path dataset/final_set/Tactful_conv_set_0.json \
    --output_dir results/
```

### Question Generation

If you want to generate questions for new conversations:

```python


# Load your conversation data
selected_set = {...}  # Your conversation data

# Generate different question types
comprehension_qas = generate_comprehensionQA(selected_set)
justification_qas = generate_justificationQA(selected_set)
fact_qas = generate_fact_QA(selected_set)
belief_qas_1st = generate_1stbeliefQAs(selected_set)
belief_qas_2nd = generate_2ndbeliefQAs(selected_set)
```

### Generating Justification Options

For creating justification options using GPT-4:

```python
from code.justification_option_generator import (
    init_openai_client,
    process_single_conversation
)

# Initialize OpenAI client
init_openai_client("your-api-key")

# Process a conversation
success = process_single_conversation(
    json_path="dataset/elements/Tactful_conv_element_0.json",
    set_id="0-1-0-0",
    output_path="output.json"
)
```

## 🤝 Contributing

We welcome contributions! Please email us if you want to contribute to extend the dataset.

## 📄 Citation

If you use TactfulToM in your research, please cite our paper:

```bibtex
@inproceedings{liu-etal-2025-tactfultom,
    title = "{T}actful{T}o{M}: Do {LLM}s have the Theory of Mind ability to understand White Lies?",
    author = "Liu, Yiwei  and
      Pretty, Emma Jane  and
      Huang, Jiahao  and
      Sugawara, Saku",
    editor = "Christodoulopoulos, Christos  and
      Chakraborty, Tanmoy  and
      Rose, Carolyn  and
      Peng, Violet",
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-main.1272/",
    pages = "25054--25072",
    ISBN = "979-8-89176-332-6",
    abstract = "While recent studies explore Large Language Models' (LLMs) performance on Theory of Mind (ToM) reasoning tasks, research on ToM abilities that require more nuanced social context is limited, such as white lies. We introduce TactfulToM, a novel English benchmark designed to evaluate LLMs' ability to understand white lies within real-life conversations and reason about prosocial motivations behind them, particularly when they are used to spare others' feelings and maintain social harmony. Our benchmark is generated through a multi-stage human-in-the-loop pipeline where LLMs expand manually designed seed stories into conversations to maintain the information asymmetry between participants necessary for authentic white lies. We show that TactfulToM is challenging for state-of-the-art models, which perform substantially below humans, revealing shortcomings in their ability to fully comprehend the ToM reasoning that enables true understanding of white lies."
}
```

## ⚠️ Important Notes

**Intended Use**: This dataset is for research and evaluation purposes only.

**Disclaimer**: Conversations were generated by GPT-4 and validated by humans. We are not claiming machines have minds or emotions—they need social reasoning capabilities to better understand human communication. While we've ensured content quality, generative models may produce unexpected outputs in freeform contexts.

**Ethical Considerations**: Our evaluation reveals that LLMs underperform compared to humans in white lie understanding. This raises important questions: should LLMs understand white lies to interpret behavior, or also generate them? We encourage responsible use and careful consideration of whether aligning LLMs with human social behaviors, including prosocial deception, is desirable for human-AI interaction.

---

