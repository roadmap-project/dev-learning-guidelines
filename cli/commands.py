import os
import json

import cli.config as conf
import cli.model as model
import cli.tests as tests
import cli.utils as utils


def add():
    directory = conf.roadmaps_dir

    # TODO constraint: 'Y,y,n,N' only
    print(f'Use the default directory (database/roadmaps)? (y/n) => ')
    use_default_directory = input().lower()

    if use_default_directory == 'n':
        # TODO constraint: directory should be without any files
        print('Input path to parent directory for roadmap => ')
        directory = input()

    # TODO constraint: should be unique
    print('Input title for new roadmap => ')
    roadmap_title = input()

    print('Input your GitHub username => ')
    author_username = input()

    add_roadmap(
        directory=directory,
        roadmap_title=roadmap_title,
        author_username=author_username
    )


def add_roadmap(directory, roadmap_title, author_username):
    roadmap_title_in_snake_case = utils.to_snake_case(roadmap_title)
    directory = os.path.join(directory, roadmap_title_in_snake_case)

    author_username = author_username.replace(' ', '').lower()

    os.makedirs(directory)

    with open(os.path.join(conf.templates_dir, 'config.json'), 'r') as fr:
        config = json.load(fr)
        config['title'] = roadmap_title
        config['authors'] = [author_username]

        with open(os.path.join(directory, 'config.json'), 'w') as fw:
            json.dump(config, fw)

    with open(os.path.join(conf.templates_dir, 'overview.md'), 'r') as fr:
        fr.readline()  # missing header line
        overview_title = '# ' + roadmap_title
        overview = overview_title + fr.read()

        with open(os.path.join(directory, 'overview.md'), 'w') as fw:
            fw.write(overview)


def build():
    roadmaps_data, concepts_data = test()

    generate_out_data(roadmaps_data, concepts_data)
    generate_vis_data(roadmaps_data, concepts_data)

    print('BUILT SUCCESSFUL')


def generate_out_data(roadmaps_data, concepts_data):
    data = {
        'concepts': [],
        'roadmaps': [],
    }

    for concept_data in concepts_data:
        concept = {
            'url': concept_data['url'],
            'path': concept_data['path'],
            'slug': concept_data['slug'],
            'title': concept_data['title'],
            'content': concept_data['content'],
        }

        for info in conf.concept_info.keys():
            concept[info] = concept_data[info]

        data['concepts'].append(concept)

    for roadmap_data in roadmaps_data:
        roadmap_path = os.path.join(conf.db_dir, roadmap_data['path'])
        overview_filepath = os.path.join(roadmap_path, 'overview.md')
        with open(overview_filepath, 'r') as f:
            overview_content = f.read()

        roadmap_url = roadmap_data['url']
        roadmap_path = roadmap_data['path']
        roadmap_slug = roadmap_data['slug']
        roadmap_steps = roadmap_data['config']['steps']
        roadmap_steps = model.build_steps(roadmap_steps)
        roadmap_title = roadmap_data['config']['title']
        roadmap_authors = roadmap_data['config']['authors']

        data['roadmaps'].append({
            'url': roadmap_url,
            'path': roadmap_path,
            'slug': roadmap_slug,
            'steps': roadmap_steps,
            'title': roadmap_title,
            'authors': roadmap_authors,
            'overview': overview_content
        })

    with open(os.path.join(conf.content_dir, 'out.json'), 'w') as f:
        json.dump(data, f)


def generate_vis_data(roadmaps_data, concepts_data):
    data = {
        'treeview': [],
        'roadmaps': [],
        'nodes': [],
        'links': []
    }

    tree, cur_id, nodes = model.collect_tree(concepts_data)

    links = []
    roadmaps = []

    for roadmap_data in roadmaps_data:
        cur_id += 1
        concepts = []

        for c in roadmap_data['used_concepts']:
            for n in nodes:
                if c == n['slug']:
                    concepts.append(n['id'])
                    links.append({
                        'sid': cur_id,
                        'tid': n['id']
                    })

        roadmaps.append({
            'id': cur_id,
            'concepts': concepts,
            'slug': roadmap_data['slug'],
            'name': roadmap_data['config_title']
        })

    for n in nodes:
        if n['parents']:
            links.append({
                'sid': n['parents'][-1],
                'tid': n['id']
            })

    data['roadmaps'] = roadmaps
    data['treeview'] = tree
    data['nodes'] = nodes
    data['links'] = links

    with open(os.path.join(conf.content_dir, 'vis.json'), 'w') as f:
        json.dump(data, f)


def test():
    print('____GENERAL TESTS_____')

    tests.test_file_and_folder_in_same_node_existing(conf.db_dir)

    print('____CONCEPTS TESTS_____')

    concepts = model.collect_concepts(conf.concepts_dir)

    # Check uniqueness for concepts slug/title
    tests.test_uniqueness(concepts, ['slug', 'title'])

    # Check quality between concept's title and slug in snake-case
    tests.test_quality(concepts, ['slug', 'title'], utils.to_snake_case)

    # Check concept content scheme
    tests.test_concept_content_scheme(concepts)

    concepts = model.collect_concepts_info(concepts)

    print('____ROADMAPS TESTS_____')

    roadmaps = model.collect_roadmaps(conf.roadmaps_dir)

    # Check concepts from roadmap config existing
    tests.test_concept_existing(roadmaps, concepts)

    roadmaps = model.collect_dependencies(roadmaps, concepts)

    # Check uniqueness for roadmaps slug/overview_title/config_title
    tests.test_uniqueness(roadmaps, ['slug', 'overview_title', 'config_title'])

    # Check quality between roadmap's slug/overview_title/config_title in snake-case
    tests.test_quality(roadmaps, ['slug', 'overview_title', 'config_title'], utils.to_snake_case)

    return roadmaps, concepts
