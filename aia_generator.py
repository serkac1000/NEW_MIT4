import zipfile
from io import BytesIO
import re

def parse_pseudocode(pseudocode: str):
    """
    Parse pseudocode for Add Button/Label and Set <Component>.Text to ...
    Returns a list of component dicts for the .scm JSON.
    """
    components = []
    name_to_component = {}
    for line in pseudocode.splitlines():
        line = line.strip()
        # Add Button
        m = re.match(r'Add Button \(Name: ([A-Za-z0-9_]+)\)', line)
        if m:
            name = m.group(1)
            comp = {"$Name": name, "$Type": "Button", "Text": name, "WidthPercent": 80, "Height": 50, "BackgroundColor": -16776961, "TextColor": -1, "FontSize": 16}
            components.append(comp)
            name_to_component[name] = comp
            continue
        # Add Label
        m = re.match(r'Add Label \(Name: ([A-Za-z0-9_]+)\)', line)
        if m:
            name = m.group(1)
            comp = {"$Name": name, "$Type": "Label", "Text": name, "Width": -2, "FontSize": 18, "TextAlignment": 1}
            components.append(comp)
            name_to_component[name] = comp
            continue
        # Set <Component>.Text to ...
        m = re.match(r'Set ([A-Za-z0-9_]+)\.Text to "([^"]*)"', line)
        if m:
            name = m.group(1)
            text = m.group(2)
            if name in name_to_component:
                name_to_component[name]["Text"] = text
            continue
        # Set <Component>.Width to ...
        m = re.match(r'Set ([A-Za-z0-9_]+)\.Width to (.+)', line)
        if m:
            name = m.group(1)
            width = m.group(2)
            if name in name_to_component:
                if 'percent' in width.lower():
                    try:
                        val = int(re.search(r'(\d+)', width).group(1))
                        name_to_component[name]["WidthPercent"] = val
                    except:
                        pass
                else:
                    try:
                        val = int(re.search(r'(\d+)', width).group(1))
                        name_to_component[name]["Width"] = val
                    except:
                        pass
            continue
        # Set <Component>.Height to ...
        m = re.match(r'Set ([A-Za-z0-9_]+)\.Height to (.+)', line)
        if m:
            name = m.group(1)
            height = m.group(2)
            try:
                val = int(re.search(r'(\d+)', height).group(1))
                name_to_component[name]["Height"] = val
            except:
                pass
            continue
    return components

def generate_aia_from_pseudocode(pseudocode: str) -> bytes:
    """
    Generate a .aia file for MIT App Inventor based on parsed pseudocode.
    """
    project_name = "ButtonApp"
    scm = generate_screen1_scm(project_name, pseudocode)
    bky = generate_screen1_bky(project_name)
    project_properties = f"appName={project_name}\n" \
                         "assets=\n" \
                         "build=\n" \
                         "extension=\n" \
                         "icon=\n" \
                         "main=Screen1\n" \
                         "name={project_name}\n" \
                         "scm=\n" \
                         "source=\n" \
                         "version=1\n"
    youngandroid_project_properties = "#|$YOUNG_ANDROID_PROJECT_PROPERTIES$|#\n" \
        "project=ButtonApp\n" \
        "main=Screen1\n" \
        "usesLocation=false\n" \
        "assets=\n" \
        "source=\n" \
        "scm=\n" \
        "extension=\n" \
        "build=\n" \
        "version=1\n"
    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('project.properties', project_properties)
        zf.writestr('youngandroidproject/project.properties', youngandroid_project_properties)
        zf.writestr(f'src/{project_name}/Screen1.scm', scm.encode('utf-8'))
        zf.writestr(f'src/{project_name}/Screen1.bky', bky.encode('utf-8'))
    mem_zip.seek(0)
    return mem_zip.read()

def generate_screen1_scm(project_name, pseudocode=None):
    # Parse pseudocode for components
    if pseudocode:
        components = parse_pseudocode(pseudocode)
    else:
        components = []
    # Place all buttons/labels in a VerticalArrangement
    va = {
        "$Name": "ButtonContainer",
        "$Type": "VerticalArrangement",
        "Width": -2,
        "Height": -2,
        "AlignHorizontal": 3,
        "AlignVertical": 2,
        "Components": components
    }
    # Add a default StatusLabel and ResetButton if not present
    names = [c["$Name"] for c in components]
    if "StatusLabel" not in names:
        status_label = {"$Name": "StatusLabel", "$Type": "Label", "Text": "No button clicked yet", "Width": -2, "FontSize": 18, "TextAlignment": 1}
    else:
        status_label = None
    if "ResetButton" not in names:
        reset_button = {"$Name": "ResetButton", "$Type": "Button", "Text": "Reset", "WidthPercent": 80, "Height": 50, "BackgroundColor": -65536, "TextColor": -1}
    else:
        reset_button = None
    all_components = [va]
    if status_label:
        all_components.append(status_label)
    if reset_button:
        all_components.append(reset_button)
    json_block = '{\n  "$Name": "Screen1",\n  "$Type": "Form",\n  "$Version": 27,\n  "Uuid": 123456,\n  "Title": "12 Button App",\n  "AlignHorizontal": 3,\n  "AlignVertical": 2,\n  "BackgroundColor": -3355444,\n  "AppName": "' + project_name + '",\n  "Components": [\n'
    for i, comp in enumerate(all_components):
        json_block += '    ' + json.dumps(comp, ensure_ascii=False)
        if i < len(all_components) - 1:
            json_block += ',\n'
        else:
            json_block += '\n'
    json_block += '  ]\n}'
    scm = "#|$JSON\n" + json_block + "|#"
    scm = scm.strip('\r\n')
    if not scm.endswith('|#'):
        scm += '\n|#'
    elif not scm.endswith('\n|#'):
        scm = scm[:-2] + '\n|#'
    return scm

def generate_screen1_bky(project_name):
    return '{\n  "blocks": []\n}'

def find_unknown_components(pseudocode: str, known_components=None):
    if known_components is None:
        known_components = {"Button", "Label", "VerticalArrangement", "Notifier", "Screen", "ResetButton", "StatusLabel", "ButtonContainer"}
    unknown = set()
    lines = pseudocode.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("For ") or line.startswith("Define Global") or line.startswith("Set Global"):
            continue
        m = re.match(r'(Add|Set|When)\s+([A-Za-z0-9_]+)', line)
        if m:
            comp = m.group(2)
            if not comp or len(comp) == 1 or comp == "Global" or comp == "Button_i":
                continue
            base = re.sub(r'\d+$', '', comp)
            if base not in known_components:
                unknown.add(base)
    return unknown

import json 