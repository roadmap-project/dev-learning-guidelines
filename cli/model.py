# Модель заготоваливает представления для других *.py модулей
# Модель единственная, кто знает какие сущности в базе знаний


import os
import json

from cli.config import *


def collect_concepts(root):
    concepts = []

    for path, folders, files in os.walk(root):
        for file in files:
            filepath = f'{path}/{file}'

            # '.'.join(file.split('.')[:-1])
            slug, _ = os.path.splitext(file)

            # hack for extracting concept name
            with open(filepath, 'r') as f:
                title = f.readline()
                name = title.split('#')[1].strip()

            filepath = os.path.relpath(filepath, db_dir)
            url = gh_db_url + filepath

            concepts.append({
                'url': url,
                'path': filepath,
                'slug': slug,
                'title': name
            })

    return concepts


def collect_roadmaps(root):
    roadmaps = []

    for path, folders, files in os.walk(root):
        if files:
            with open(f'{path}/config.json', 'r') as f:
                config = json.load(f)

            used_concepts = set()

            # collect used concepts in config
            for step in config['steps']:
                for section in step:
                    if 'options' in section:
                        options = section['options']
                        if 'required_concepts' in options:
                            for concept in options['required_concepts']:
                                used_concepts.add(concept)

                    for ref in section['refs']:
                        used_concepts.add(ref['concept'])

            with open(f'{path}/overview.md', 'r') as f:
                title = f.readline()
                overview_title = title.split('#')[1].strip()

            slug = os.path.basename(path)
            path = os.path.relpath(path, db_dir)
            config_title = config['title']
            url = gh_db_url + path

            roadmaps.append({
                'url': url,
                'path': path,
                'slug': slug,
                'config': config,
                'config_title': config_title,
                'used_concepts': used_concepts,
                'overview_title': overview_title,
            })

    return roadmaps


def collect_dependencies(roadmaps_data, concepts):
    dependencies = {}

    for roadmap_data in roadmaps_data:
        used_concepts = roadmap_data['used_concepts']

        for used_concept in used_concepts:
            concept = next(filter(lambda x: x['slug'] == used_concept, concepts), None)  # find concept
            if concept:
                dependencies[used_concept] = concept['path']

        roadmap_data['dependencies'] = dependencies
        dependencies = {}

    return roadmaps_data


def collect_tree(concepts_data):
    concepts = concepts_data

    def to_title(slug):
        for c in concepts:
            if c['slug'] == slug:
                return c['title']

    def to_tree(path, node_id, nodes: list, parents: list):
        d = {
            'id': node_id,
            'slug': os.path.basename(path),
            'parents': parents
        }

        if os.path.isdir(path):
            d['is_concept'] = False
            d['name'] = d['slug'].replace('_', ' ').capitalize()
            d['children'] = []

            child_parents = parents.copy()

            if d['id'] != 0:
                child_parents.append(d['id'])

            for x in os.listdir(path):
                sub_tree, node_id, nodes = to_tree(
                    path=os.path.join(path, x),
                    node_id=node_id + 1,
                    parents=child_parents,
                    nodes=nodes
                )

                d['children'].append(sub_tree)
        else:
            d['is_concept'] = True
            d['slug'], _ = os.path.splitext(d['slug'])
            d['name'] = to_title(d['slug'])

        if d['id'] != 0:
            nodes.append({
                'id': d['id'],
                'slug': d['slug'],
                'name': d['name'],
                'parents': d['parents'],
                'is_concept': d['is_concept']
            })

        return d, node_id, nodes

    root, max_id, nodes = to_tree(concepts_dir, 0, [], [])
    return root['children'], max_id, nodes


def build_steps(steps):
    try:
        for step in steps:
            for section in step:
                if 'options' in section:
                    options = section['options']
                    if 'allow_multiple_choice' not in options:
                        options['allow_multiple_choice'] = default_step['allow_multiple_choice']
                    if 'required_concepts' not in options:
                        options['required_concepts'] = default_step['required_concepts']
                else:
                    section['options'] = {
                        'allow_multiple_choice': default_step['allow_multiple_choice'],
                        'required_concepts': default_step['required_concepts']
                    }

                for ref in section['refs']:
                    if 'options' in ref:
                        options = ref['options']
                        if 'note' not in options:
                            options['note'] = default_step['note']
                    else:
                        ref['options'] = {
                            'note': default_step['note'],
                        }
    except Exception as e:
        print(f'Something went wrong during building steps: {e}')

    return steps


def collect_data():
    concepts = collect_concepts(concepts_dir)
    roadmaps = collect_roadmaps(roadmaps_dir)

    return {
        'concepts': concepts,
        'roadmaps': roadmaps,
    }
