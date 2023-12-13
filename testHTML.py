import os
import subprocess

myEnv = dict(os.environ)
lp_key = 'LD_LIBRARY_PATH'
lp_orig = myEnv.get(lp_key + '_ORIG')
if lp_orig is not None:
    myEnv[lp_key] = lp_orig
else:
    lp = myEnv.get(lp_key)
    if lp is not None:
        myEnv.pop(lp_key)

def open_html_file(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    # Use xdg-open to open the file in the default web browser
    try:
        subprocess.run(['xdg-open', file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to open '{file_path}' with xdg-open.")
        print(e)

if __name__ == "__main__":
    # Replace the file path with the actual path to your HTML file
    html_file_path = r"P:\Quality Systems\Test Engineering\Test Equipment\Common Test System\Logs\2023\11\457042_225_A_[290+73][4 49 59 PM][11 6 2023].html"
    open_html_file(html_file_path)

