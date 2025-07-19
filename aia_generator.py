import zipfile
from io import BytesIO
import re
import json

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
    project_properties = f"#Sat Jul 19 20:00:00 UTC 2025\n" \
                         f"sizing=Responsive\n" \
                         f"color.primary.dark=&HFF303F9F\n" \
                         f"color.primary=&HFF3F51B5\n" \
                         f"color.accent=&HFFFF4081\n" \
                         f"aname={project_name}\n" \
                         f"defaultfilescope=App\n" \
                         f"main=appinventor.ai_user.{project_name}.Screen1\n" \
                         f"source=../src\n" \
                         f"actionbar=True\n" \
                         f"useslocation=False\n" \
                         f"assets=../assets\n" \
                         f"build=../build\n" \
                         f"name={project_name}\n" \
                         f"showlistsasjson=True\n" \
                         f"theme=AppTheme.Light.DarkActionBar\n" \
                         f"versioncode=1\n" \
                         f"versionname=1.0\n"
    youngandroid_project_properties = f"#|$YOUNG_ANDROID_PROJECT_PROPERTIES$|#\n" \
        f"project={project_name}\n" \
        f"main=Screen1\n" \
        f"usesLocation=false\n" \
        f"assets=\n" \
        f"source=\n" \
        f"scm=\n" \
        f"extension=\n" \
        f"build=\n" \
        f"version=1\n"
    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('project.properties', project_properties)
        zf.writestr('youngandroidproject/project.properties', youngandroid_project_properties)
        zf.writestr(f'src/{project_name}/Screen1.scm', scm.encode('utf-8'))
        zf.writestr(f'src/{project_name}/Screen1.bky', bky.encode('utf-8'))
    mem_zip.seek(0)
    return mem_zip.read()

def generate_screen1_scm(project_name, pseudocode=None):
    import random
    
    # Parse pseudocode for components
    if pseudocode:
        parsed_components = parse_pseudocode(pseudocode)
    else:
        parsed_components = []
    
    # Clean up components - remove conflicting properties and add required fields
    cleaned_components = []
    for comp in parsed_components:
        # Remove Width if WidthPercent is set to avoid conflicts
        if "WidthPercent" in comp and "Width" in comp:
            del comp["Width"]
        # Add required fields for MIT App Inventor
        comp["$Version"] = "7"
        comp["Uuid"] = str(random.randint(1000000000, 9999999999))
        cleaned_components.append(comp)
    
    # Separate user-defined components from default ones
    user_component_names = [c["$Name"] for c in cleaned_components]
    
    # Add default StatusLabel if not present
    if "StatusLabel" not in user_component_names:
        status_label = {
            "$Name": "StatusLabel", 
            "$Type": "Label", 
            "$Version": "7",
            "Text": "No button clicked yet", 
            "Width": -2, 
            "FontSize": 18, 
            "TextAlignment": 1,
            "Uuid": "123456789"
        }
        cleaned_components.append(status_label)
    
    # Add default ResetButton if not present
    if "ResetButton" not in user_component_names:
        reset_button = {
            "$Name": "ResetButton", 
            "$Type": "Button", 
            "$Version": "7",
            "Text": "Reset", 
            "WidthPercent": 80, 
            "Height": 50, 
            "BackgroundColor": -16776961, 
            "TextColor": -1,
            "FontSize": 16,
            "Uuid": "987654321"
        }
        cleaned_components.append(reset_button)
    
    # Create the proper screen structure matching MIT App Inventor format exactly
    screen_data = {
        "authURL": ["ai2.appinventor.mit.edu"],
        "YaVersion": "232",
        "Source": "Form",
        "Properties": {
            "$Name": "Screen1",
            "$Type": "Form",
            "$Version": "31",
            "Title": "12 Button App",
            "Uuid": "0",
            "AppName": project_name,
            "AlignHorizontal": 3,
            "AlignVertical": 2,
            "BackgroundColor": -3355444,
            "$Components": cleaned_components
        }
    }
    
    # Format as single-line minified JSON (required by MIT App Inventor)
    json_block = json.dumps(screen_data, separators=(',', ':'), ensure_ascii=False)
    scm = "#|$JSON\n" + json_block + "|#"
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