import subprocess
import os
from log import log

def compile_cpp(domain_name, port, user_id, cpp_template_path, output_executable_path):
    log(f"Compilation started...", "INFO")
    try:
        with open(cpp_template_path, 'r', encoding="utf-8") as f:
            cpp_code_template = f.read()
    except FileNotFoundError:
        log(f"File not found {cpp_template_path}", "ERROR")
        return None

    # Заменяем плейсхолдер на фактический user_id
    cpp_code = cpp_code_template.replace("{{USER_ID}}", str(user_id)).replace("{{DOMAIN_NAME}}", domain_name).replace("{{PORT}}", port)

    # Создаем временный файл для C++ кода
    temp_cpp_file = "temp.cpp"  # Лучше использовать tempfile.NamedTemporaryFile
    with open(temp_cpp_file, 'w') as f:
        f.write(cpp_code)

    # Компиляция C++ кода
    compile_command = ["g++", temp_cpp_file, "-o", output_executable_path, "-lws2_32"] 
    compile_process = subprocess.run(compile_command, capture_output=True, text=True)

    if compile_process.returncode != 0:
        log(f"Compilation error:\n{compile_process.stderr}")
        #os.remove(temp_cpp_file) # Удаляем временный файл
        return None

    os.remove(temp_cpp_file) # Удаляем временный файл

from win32com.client import Dispatch

def prepare_lnk(domain_name, port, user_id, output_lnk_path):
    target_path="%SystemRoot%\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
    parameters = f"-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command \"(Invoke-WebRequest -Uri 'http://{domain_name}:{port}/api/lnk_executed?q={user_id}' -Method Post).Content\""
    description="Описание ярлыка"
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(output_lnk_path)
    shortcut.Targetpath = target_path
    shortcut.Arguments = parameters
    shortcut.WorkingDirectory = target_path.rsplit('\\', 1)[0]
    shortcut.Description = description
    icon_path="%SystemRoot%\\System32\\SHELL32.dll"
    icon_index=1
    expanded_icon_path = os.path.expandvars(icon_path)
    shortcut.IconLocation = f"{expanded_icon_path},{icon_index}"
    shortcut.save()


def prepare_html(domain_name, port, user_id, template_html_path, output_html_path):
    """
    Reads an HTML template, replaces placeholders DOMAIN_NAME, PORT, USER_ID
    with the specified values, and saves the modified content to a new file.

    Args:
        domain_name (str): The domain name to replace DOMAIN_NAME.
        port (str): The port to replace PORT.
        user_id (str): The user ID to replace USER_ID.
        template_html_path (str): Path to the input HTML template.
        output_html_path (str): Path to save the modified HTML file.
    """
    try:
        # Read the template HTML file
        with open(template_html_path, 'r', encoding='utf-8') as template_file:
            html_content = template_file.read()

        # Replace placeholders with the provided values
        html_content = html_content.replace("DOMAIN_NAME", domain_name)
        html_content = html_content.replace("PORT", str(port))
        html_content = html_content.replace("USER_ID", str(user_id))

        # Write the modified content to the output file
        with open(output_html_path, 'w', encoding='utf-8') as output_file:
            output_file.write(html_content)

        print(f"HTML file successfully created at {output_html_path}")

    except Exception as e:
        print(f"An error occurred: {e}")



def generate_payloads(domain_name, port, recipient, target_payload):
    if target_payload.name == "executable_file_runned":
        log(f"Using template {target_payload.template}", "INFO")
        
        compile_cpp(domain_name, port, recipient.id, target_payload.template, target_payload.attachment_path)
        
        log(f"Compilation successful...", "INFO")

    elif target_payload.name == "lnk_file_runned":
        log(f"Using template {target_payload.template}", "INFO")
        prepare_lnk(domain_name, port, recipient.id, target_payload.attachment_path)

    elif target_payload.name == "phishing_html_submit":
        log(f"Using template {target_payload.template}", "INFO")
        prepare_html(domain_name, port, recipient.id, target_payload.template, target_payload.attachment_path)

    else:
        return