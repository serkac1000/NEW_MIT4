from flask import Flask, render_template, request, send_file
import os
from io import BytesIO
from zipfile import ZipFile
from aia_generator import generate_aia_from_pseudocode, find_unknown_components, generate_screen1_scm
import traceback

app = Flask(__name__)

def append_log(log, msg):
    if log:
        log += '\n'
    log += msg
    return log

@app.route('/', methods=['GET', 'POST'])
def index():
    preview_scm = None
    debug_log = ''
    if request.method == 'POST':
        pseudocode = request.form.get('pseudocode', '')
        use_extensions = bool(request.form.get('use_extensions'))
        debug_log = append_log(debug_log, 'Received pseudocode input.')
        try:
            unknown_components = find_unknown_components(pseudocode)
            debug_log = append_log(debug_log, f'Unknown components: {unknown_components}')
            if 'preview_scm' in request.form:
                preview_scm = generate_screen1_scm("ButtonApp", pseudocode)
                debug_log = append_log(debug_log, 'Generated SCM preview.')
                return render_template(
                    'index.html',
                    unknown_components=unknown_components,
                    pseudocode=pseudocode,
                    use_extensions=use_extensions,
                    preview_scm=preview_scm,
                    debug_log=debug_log
                )
            if unknown_components:
                debug_log = append_log(debug_log, 'Warning: Unknown components detected.')
                return render_template(
                    'index.html',
                    unknown_components=unknown_components,
                    pseudocode=pseudocode,
                    use_extensions=use_extensions,
                    debug_log=debug_log
                )
            aia_bytes = generate_aia_from_pseudocode(pseudocode)
            debug_log = append_log(debug_log, 'AIA file generated successfully.')
            return send_file(
                BytesIO(aia_bytes),
                mimetype='application/zip',
                as_attachment=True,
                download_name='mit_app_inventor_project.aia'
            )
        except Exception as e:
            debug_log = append_log(debug_log, 'Error: ' + str(e))
            debug_log = append_log(debug_log, traceback.format_exc())
            return render_template(
                'index.html',
                unknown_components=[],
                pseudocode=pseudocode,
                use_extensions=use_extensions,
                debug_log=debug_log
            )
    return render_template('index.html', debug_log=debug_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 