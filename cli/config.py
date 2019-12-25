import os
import pathlib

project_dir = pathlib.Path(os.getcwd())
db_dir = os.path.join(project_dir, 'database')
content_dir = os.path.join(db_dir, 'content')
roadmaps_dir = os.path.join(db_dir, 'roadmaps')
concepts_dir = os.path.join(db_dir, 'concepts')
templates_dir = os.path.join(db_dir, 'templates')

gh_db_url = 'https://github.com/roadmap-project/dev-learning-guidelines/tree/master/database/'

default_step = {
    'note': '',
    'required_concepts': [],
    'allow_multiple_choice': True,
}

concept_info = {
    'description': {
        'start': '<!--description content start-->',
        'end': '<!--description content end-->'
    },
    'knowledge': {
        'start': '<!--knowledge content start-->',
        'end': '<!--knowledge content end-->'
    },
    'competencies': {
        'start': '<!--competencies content start-->',
        'end': '<!--competencies content end-->'
    }
}
