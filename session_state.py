_current_project_id = None

def set_current_project(project_id):
    global _current_project_id
    _current_project_id = project_id

def get_current_project():
    return _current_project_id