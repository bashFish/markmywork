
import pandas as pd
import glob
import docx
import pickle
import csv
import tqdm
import re


def parse_essay_file(filepath):

    doc = docx.Document(filepath)
    count = 0
    essay = ''
    count_paragraphs = 0
    for p in doc.paragraphs:
        if len(p.text) < 3:
            continue
        count += len(p.text)
        count_paragraphs += 1
        essay += p.text.strip().strip('\n')+'\n'
    return (filepath, count_paragraphs, count, essay)

def parse_essays(fp_root='data/input_files/essays/*'):

    all_essays_filepaths = glob.glob(fp_root)
    all_parsed_essays = []
    for fp in all_essays_filepaths:
        (filepath, count_paragraphs, count, essay) = parse_essay_file(fp)
        #if count <= 3400: #its letter count, not token! darn.
        #    continue
        all_parsed_essays.append((fp, count, count_paragraphs, essay))
    return all_parsed_essays

def parse_question_explanations(fp='data/input_files/question_explanations.csv'):

    question_explanations = pd.read_csv(fp, sep=';', quoting=csv.QUOTE_NONE)

    return question_explanations

def parse_annotations(fp='data/input_files/marked_essays_v1.csv'):

    marked_essays = pd.read_csv(fp)
    questions = list(marked_essays.keys()[1:])

    x = marked_essays#[:]
    x = x[x.notnull().all(axis=1)]
    for k in x.keys():
        #x = x[x[k].astype(str).str.is_numeric()]
        x = x[pd.to_numeric(x[k], errors='coerce').notnull()]
    filtered_marked_essays = x
    filtered_marked_essays

    return marked_essays, filtered_marked_essays, questions


def assemble_prompts(all_parsed_essays, filtered_marked_essays, questions_explanation):

    all_prompts = []
    for i,essay_array in tqdm.tqdm(enumerate(all_parsed_essays)):

        essay_id = int(re.findall(r'\d+', essay_array[0])[-1])
        cur_row = filtered_marked_essays[filtered_marked_essays['essay id'] == essay_id]
        if len(cur_row) != 1:
            continue

        for j,k in questions_explanation.iterrows():
            question = k.question
            explanation = k.explanation
            prompt = assemble_prompt_v2(essay_array[3][:-1], #implicit newline
                                    question.strip(),
                                    explanation.strip())

            all_prompts.append((i, j, prompt, int(cur_row.iloc[0,j+1])))
    return all_prompts


def save_results(fp, all_parsed_essays, all_questions, all_answers):

    pickle.dump(all_parsed_essays,open(f"{fp}/essays_dump.pckl","wb"))
    pickle.dump(all_questions,open(f"{fp}/questions_dump.pckl","wb"))
    pickle.dump(all_answers,open(f"{fp}/answer_dump.pckl","wb"))

def load_results(fp):

    all_parsed_essays = pickle.load(open(f"{fp}/essays_dump.pckl","rb"))
    all_questions =pickle.load(open(f"{fp}/questions_dump.pckl","rb"))
    all_answers = pickle.load(open(f"{fp}/answer_dump.pckl","rb"))

    return all_parsed_essays, all_questions, all_answers

prompt_tpl = 'Given is a student essay and a question to the essay. Please rate the Question with a number between 0 and 3, where 0 is "not at all satisfied" and 3 is "very satisfied.".\n\n'
prompt_tpl += 'Essay: """\n{essay}"""\n'
prompt_tpl += 'Question: """\n{question}"""\n'
prompt_tpl += 'Answer:'
PROMPT_TPLS = [prompt_tpl]

prompt_tpl = 'Given is a student essay and a question to the essay. Please rate the Question with a number between 0 and 3, where 0 is "not at all satisfied" and 3 is "very satisfied.".\n\n'
prompt_tpl += 'Essay: """\n{essay}"""\n'
prompt_tpl += 'Question: """\n{explanation}\n{question}"""\n'
prompt_tpl += 'Answer:'
PROMPT_TPLS.append(prompt_tpl)

prompt_tpl = 'Essay:\n{essay}\n\n###\n\n'
prompt_tpl += 'Question:\n{explanation}\n{question}\n\n###\n\n'
prompt_tpl += 'Answer:'
PROMPT_TPLS.append(prompt_tpl)


def assemble_prompt_v2(essay, question, explanation, template=PROMPT_TPLS[2]):

    return template.format(essay=essay,question=question,explanation=explanation)


def assemble_prompt(essay, question, template=PROMPT_TPLS[0]):

    return template.format(essay=essay,question=question)
