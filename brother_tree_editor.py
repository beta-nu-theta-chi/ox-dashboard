import re
import os
import subprocess

SERVICE_ACCOUNT_NAME = 'oxdashboard-svc'

DOT_FILE_NAME = 'brotherhood.gz'

BIG_BROTHER_REPO_DIR = os.path.join('..', 'big-brother-tree')
DOT_FILE_PATH = os.path.join(BIG_BROTHER_REPO_DIR, DOT_FILE_NAME)

def candidate_class_entry(semester_season, semester_year, candidate_names):
    entry = ' rank = same; "{} {}"; '.format(semester_season, semester_year)

    for name in candidate_names:
        entry += '"{}"; '.format(name)

    return '\t{' + entry + '}\n'

def dot_relations(relations):
    dot_relations = []

    for big, little in relations.items():
        dot_relations.append('\t"{}" -> "{}";\n'.format(big, little))

    return dot_relations

def big_last_name_key(dot_relation):
    """Creates a key from the dot relation that allows sorting by big last name.

    Break ties with the first name

    """

    match = re.search(r'\"([^ ]+) ([^\"]+)\"', dot_relation)

    first_name = match.group(1)
    last_name = match.group(2)

    return (last_name + " " + first_name).lower()

def add_big_little_relations(dot_path, semester_season, semester_year, relations):
    lines = []
    with open(dot_path, "r") as dot_fd:
        lines = dot_fd.readlines()

    # The following loop assumes the dot file is properly formatted, if not,
    # this function will error out because the index vars will not be defined
    # I don't feel like adding error handling for this scenario as the
    # use case is basically non-existent.  If the dot file in the
    # big brother tree repo changes  in a way in which this script no longer works,
    # then someone will need to update this script, so this "feature" makes
    # the need for that painfully obvious

    # find the indices of each place information needs to be added
    for index, line in enumerate(lines):
        if "Put pledge classes here" in line:
            semester_index = index + 1
        elif "Section 3" in line:
            class_entry_insertion_index = index - 1
            relations_start_index = index + 2
        elif line.startswith("}"):
            relations_end_index = index - 1

    pre_relations = lines[:relations_start_index]
    relations_list = lines[relations_start_index:relations_end_index]
    post_relations = lines[relations_end_index:]

    # add the semester
    pre_relations[semester_index] = lines[semester_index][:-2] + ' -> "{} {}";\n'.format(semester_season, semester_year)

    # add the class entry
    pre_relations.insert(
        class_entry_insertion_index,
        candidate_class_entry(
            semester_season,
            semester_year,
            list(relations.values())))

    # add the relations
    relations_list += dot_relations(relations)
    relations_list.sort(key=big_last_name_key)

    with open(dot_path, "w") as dot_fd:
        dot_fd.writelines(pre_relations + relations_list + post_relations)

def relations_to_markdown_table(relations):
    return "| Big | Little |\n|:--:|:--:|\n{}".format(
        str(relations).replace(":", " |")
                    .replace(", ", " |\n| ")
                    .replace("{", "| ")
                    .replace("}", " |")
                    .replace("'", "")
    )

def setup_branch(new_branch_name):
    subprocess.check_call(['git', 'checkout', 'master'], cwd=BIG_BROTHER_REPO_DIR)
    subprocess.check_call(['git', 'pull'], cwd=BIG_BROTHER_REPO_DIR)
    subprocess.check_call(['git', 'checkout', '-b', new_branch_name, 'master'], cwd=BIG_BROTHER_REPO_DIR)

def generate_tree(file_format):
    subprocess.check_call(
        [
            'dot',
            '-T{}'.format(file_format),
            DOT_FILE_NAME,
            '-obrotherhood.{}'.format(file_format)
        ],
        cwd=BIG_BROTHER_REPO_DIR)

def save_changes_to_github(commit_message, new_branch_name):
    subprocess.check_call(['git', 'add', '*'], cwd=BIG_BROTHER_REPO_DIR)
    subprocess.check_call(['git', 'commit', '-m', commit_message], cwd=BIG_BROTHER_REPO_DIR)
    subprocess.check_call(['git', 'push', '-u', 'origin', new_branch_name], cwd=BIG_BROTHER_REPO_DIR)

def create_pull_request(commit_message, new_branch_name, relations):
    subprocess.check_call(
    [
        'gh',
        'pr',
        'create',
        '--title', commit_message,
        '--base', 'master',
        '--head', new_branch_name,
        '--body', '{}, adding the following Big-Little Relationships:\n\n{}'.format(
            commit_message,
            relations_to_markdown_table(relations)),
    ],
    cwd=BIG_BROTHER_REPO_DIR)

def update_brother_tree_with_git(semester_season, semester_year, relations):
    new_branch_name = '{}/{}{}'.format(SERVICE_ACCOUNT_NAME, semester_season, semester_year)
    commit_message = 'Updated Big Brother Tree for {} {}'.format(semester_season, semester_year)
    relations_markdown_table = relations_to_markdown_table(relations)

    # TODO: may want to add some error handling if any of this errors out
    setup_branch(new_branch_name)

    add_big_little_relations(DOT_FILE_PATH, semester_season, semester_year, relations)

    generate_tree('pdf')
    generate_tree('svg')

    save_changes_to_github(commit_message, new_branch_name)

    create_pull_request(commit_message, new_branch_name, relations)

semester_season = 'Fall'
semester_year = '2020'
relations = {
    "Ethan Wood": "Josh Meyer",
    "Bradley Kolar": "Aaron Underwood",
    "Ben Smith": "Param Mohapatra",
    "Andrei Tiu": "Nick Ott"
}

update_brother_tree_with_git(semester_season, semester_year, relations)
