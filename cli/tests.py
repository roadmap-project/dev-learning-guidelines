# Тесты ничего не знают про то как структурирована база знаний
# Не знают какие там сущности, а только то что нужно проверить
# Тесты получают достаточные для себя данные из model.py

import os

warnings = 0
errors = 0


def warning(mes):
    global warnings
    warnings += 1
    print(f"[*] Warning: {mes}")


def error(mes):
    global errors
    errors += 1
    print(f"[!] Error: {mes}")


def execution_result(fun):
    def wrapped(*args, **kwargs):
        print(f'Execution "{fun.__name__.replace("_", " ")}":')

        global warnings, errors
        exe_res = fun(*args, **kwargs)

        print(f' => Execution result: {warnings} warning(s), {errors} errors(s)\n')

        if errors > 0:
            exit(0)

        warnings, errors = 0, 0

        return exe_res

    return wrapped


@execution_result
def test_file_and_folder_in_same_node_existing(root: str):
    """
    :param root: str
    """
    def exclude(files):
        ignore = ['.ds_store']
        return list(filter(lambda x: x.lower() not in ignore, files))

    for path, folders, files in os.walk(root):
        if len(folders) > 0 and len(exclude(files)) > 0:
            error(f'files and folders in one node, path: {path, files}')


@execution_result
def test_quality(objs: list, params: list, func):
    """Compare list of objs's values by F: F(obj[param1]) == F(obj[param2])
    :param objs: [] of dict{p1: v1, p2: v2, ..etc}
    :param params: [] of str
    :param func: function
    """
    for obj in objs:
        candidates = list([func(obj[p]) for p in params])
        if not all(c == candidates[0] for c in candidates):
            warning(f'{candidates}, path: {obj["path"]}')


@execution_result
def test_uniqueness(objs: list, params: list):
    """Find uniqueness between objs by params
    :param objs:
    :param params:
    """
    uniques = dict()

    for param in params:
        uniques[param] = dict()

    for obj in objs:
        for param in params:
            candidate = obj[param]
            if candidate in uniques[param]:
                t = uniques[param][candidate]
                uniques[param][candidate] = (t[0] + 1, t[1])
            else:
                uniques[param][candidate] = (1, obj)

    for param in params:
        for item in uniques[param].values():
            amount = item[0]
            obj = item[1]

            if amount > 1:
                error(f'"{obj[param]}" for {amount} times, param: {param}, path: {obj["path"]}')


@execution_result
def test_concept_existing(objs: list, concepts: list):
    """
    :param objs: [] of dict {slug: str, used_concepts: [] of str}
    :param concepts: [] dict {slug: str}
    """
    for obj in objs:
        obj_concepts = obj['used_concepts']
        for obj_concept in obj_concepts:
            concept = next(filter(lambda x: x['slug'] == obj_concept, concepts), None)  # find concept
            if not concept:
                error(f'concept not found "{obj_concept}" for "{obj["slug"]}"')

# @print_execution_result
# def test_unused_concepts():
#     pass

# @print_execution_result
# def test_object_value_quality(objs, params, values):
#     if len(params) != len(values):
#         error('params length and values length must be equal')
#
#     for obj in objs:
#         for i, param in enumerate(params):
#             if obj[param] != obj[values[i]]:
#                 warning(f'{obj[param]} != {obj[values[i]]}, param: {param}, obj: {obj}')

# FOR REMOVING
# @execution_result
# def test_files_existing(objs):
#     """
#     :param objs: [] of dict {title, paths: [] of str
#     """
#     for obj in objs:
#         for path in obj['paths']:
#             if not os.path.isfile(path):
#                 warning(f'path does not exist "{path}", obj: {obj}')
