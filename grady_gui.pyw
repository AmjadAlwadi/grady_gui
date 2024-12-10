import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import signal
import shlex
import os
import platform

venv_path = "/mnt/c/Users/Admin/Desktop/grady-main/grady_linuxver/venv"


# Define commands and their descriptions
commands = {
    "grady grade": "Grade a student's assignment",
    "grady summary": "Summarize the exercise results",
    "grady checkout": "Download the entered Exercise",
    "grady show-exercise": "Show the Exercise",
    "grady update-grade": "Update grade for a submission",
    "grady show-submission": "show a specific submission"
}


terminal_types = ["native","wsl"]
terminal_type = terminal_types[1]



def get_os():
    return platform.system()
    



class CommandExecutor:
    def __init__(self):
        self.process = None
        self.venv_path = venv_path

    def run_command(self, command, arguments,interactive_arguments=None):
        def execute():
            update_status("Running...")
            try:
                # Prepend Python virtual environment activation to the command
                if terminal_type == terminal_types[0]:
                    full_command = f'bash -c "source {self.venv_path}/bin/activate && {command} {arguments}"'
                else:
                    full_command = f'wsl bash -c "source {self.venv_path}/bin/activate && {command} {arguments}"'                 
                    
 
                if get_os() == "Windows":
                    self.process = subprocess.Popen(
                        full_command, 
                        shell=True, 
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True, 
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    self.process = subprocess.Popen(
                    full_command, 
                    shell=True, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    preexec_fn=os.setsid
                    )
                
                if interactive_arguments:
                    for interactive_argument in interactive_arguments:
                        print(interactive_argument)
                        self.send_input(interactive_argument)
                
                stdout, stderr = self.process.communicate()
                append_to_tk_text(output_text, stdout)
                append_to_tk_text(output_text, stderr)
                if self.process:
                    update_status("Execution completed!" if self.process.returncode == 0 else f"Error: {stderr}")
            except Exception as e:
                append_to_tk_text(output_text,str(e))
                update_status(f"Error: {str(e)}")
            finally:
                self.process = None  # Reset the process after completion

        threading.Thread(target=execute).start()

    def stop_command(self):
        if self.process and self.process.poll() is None:  # Check if process is still running
            try:
                self.process.send_signal(signal.CTRL_BREAK_EVENT)  # Send CTRL+BREAK to the process group
                self.process.wait(timeout=5)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                self.process.kill()  # Forcefully kill the process if it doesn't terminate
            finally:
                update_status("Execution stopped!")
                append_output("Execution stopped!")
                self.process = None

    
    def send_input(self, input_data):
        input_data = input_data + '\n'
        self.process.stdin.write(input_data)
        self.process.stdin.flush()






def run_command(event=None):
    command = command_var.get()
    if not command:
        messagebox.showerror("Error", "No command selected!")
        return
    
    # Collect arguments based on the selected command
    arguments = ""
    interactive_arguments = None
    
    exercise_number = exercise_entry.get()
    
    if command == "grady grade":
        task_number = task_entry.get()
        id_number = id_entry.get()
        grade = grade_entry.get()
        comment = comment_text.get("1.0", tk.END).strip().replace("\n"," ")
        if comment and len(comment) > 0:
            comment = shlex.quote(comment)
            arguments = f'{id_number}/Exercise-0{str(exercise_number)} {task_number} --points {grade} --comment {comment}'
        else:
            arguments = f'{id_number}/Exercise-0{str(exercise_number)} {task_number} --points {grade}'

    elif command == "grady update-grade":
        task_number = task_entry.get()
        id_number = id_entry.get()
        arguments = f'{id_number}/Exercise-0{str(exercise_number)} {task_number}'
        grade = grade_entry.get()
        comment = comment_text.get("1.0", tk.END).strip().replace("\n"," ")
        
        if comment and len(comment) > 0:
            comment = shlex.quote(comment)
            interactive_arguments = ["y",grade,"y",comment]
        else:
            interactive_arguments = ["y",grade,"N"]
    
    
    elif command == "grady show-submission":
        task_number = task_entry.get()
        id_number = id_entry.get()
        grade = grade_entry.get()
        arguments = f'{id_number}/Exercise-0{str(exercise_number)}'
    
    else:
        arguments = f"Exercise-0{str(exercise_number)}"
        
    
    executor.run_command(command, arguments, interactive_arguments)
    
    
    
    

def stop_command():
    executor.stop_command()

def update_status(message):
    status_label.config(text=message)


def append_to_tk_text(text_widget, output):
    text_widget.insert(tk.END, output + '\n')
    text_widget.see(tk.END)  


def clear_output():
    output_text.delete(1.0, tk.END)


def update_terminal_type(event):
    global terminal_type
    terminal_type = terminal_type_var.get()





def run_custom_command(command, arguments, interactive_arguments, output_to=None):
    # Prepend Python virtual environment activation to the command
    full_command = ""
    
    def send_input(process, input_data):
        input_data = input_data + '\n'
        process.stdin.write(input_data)
        process.stdin.flush()
        
    
    def execute(output_to):
    
        if terminal_type == terminal_types[0]:
            full_command = f'bash -c "source {venv_path}/bin/activate && {command} {arguments}"'
        else:
            full_command = f'wsl bash -c "source {venv_path}/bin/activate && {command} {arguments}"'                 
            
            
        try:
            process = None
            
            if get_os() == "Windows":
                process = subprocess.Popen(
                    full_command, 
                    shell=True, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                full_command, 
                shell=True, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                preexec_fn=os.setsid
                )
            

            if interactive_arguments:
                for interactive_argument in interactive_arguments:
                    print(interactive_argument)
                    send_input(interactive_argument)
            
            stdout, stderr = process.communicate()
            
            if output_to is None:
                return stdout
            else:
                global_string.set("")
                global_string.set(stdout)
        
        except Exception as e:
            append_to_tk_text(output_text,str(e))
            update_status(f"Error: {str(e)}")
            return None
    
    
    
    if output_to is None:
        return execute(None)
    else:
        threading.Thread(target=execute,args=[tasks_points_text]).start()




def on_global_string_changed(*args):
    extract_tasks_and_points()     




def extract_tasks_and_points():
        
    input_text = global_string.get()

    if input_text is None or len(input_text) == 0:
        return None
        
    tasks_points = []

    # Split the input text into lines
    lines = input_text.split('\n')

    # Loop through the lines and extract tasks and points
    for line in lines:
        # Ignore lines that are not tasks or are separators
        if '|' in line and 'Task name' not in line and '=====' not in line:
            parts = line.split('|')
            if len(parts) >= 3:
                task = parts[1].strip()
                points = float(parts[2].strip())
                tasks_points.append((task, points))
    
    
    output_text = ""
    for task, points in tasks_points:
        output_text += f"{task} | {points:.2f}\n"
        
    tasks_points_text.delete(1.0, tk.END)
    append_to_tk_text(tasks_points_text,output_text)








# Ensure only one instance of Tk
if __name__ == "__main__":
    global global_string
    
    root = tk.Tk()
    root.title("Grady App")
    root.configure(bg="#131313")    
    
    global_string = tk.StringVar()
    
    # Configure the grid to be resizable
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(8, weight=1)

    # Create and place the widgets
    bg = "#131313"
    fg = "#d6dbe5"
    sbg = "#000000"

    command_label = tk.Label(root,justify="left", text="Select command:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    command_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

    command_var = tk.StringVar(value=list(commands.keys())[0])
    command_dropdown = ttk.Combobox(root, textvariable=command_var,state='readonly')
    command_dropdown['values'] = list(commands.keys())
    command_dropdown.grid(row=0, column=1, pady=10, padx=10, sticky="w")
    
    
    terminal_type_var = tk.StringVar(value=terminal_type)
    terminal_type_dropdown = ttk.Combobox(root, textvariable=terminal_type_var,state='readonly')
    terminal_type_dropdown['values'] = terminal_types
    terminal_type_dropdown.grid(row=0, column=1, pady=10, padx=10, sticky="e")
    
    
    exercise_label = tk.Label(root, text="Exercise number:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    exercise_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")
    exercise_entry = ttk.Entry(root, width=50)
    exercise_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

    id_label = tk.Label(root, text="Y-Number:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    id_label.grid(row=2, column=0, pady=10, padx=10, sticky="w")
    id_entry = ttk.Entry(root, width=50)
    id_entry.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

    task_label = tk.Label(root, text="Task Number:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    task_label.grid(row=3, column=0, pady=10, padx=10, sticky="w")
    task_entry = ttk.Entry(root, width=50)
    task_entry.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

    grade_label = tk.Label(root, text="Grade:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    grade_label.grid(row=4, column=0, pady=10, padx=10, sticky="w")
    grade_entry = ttk.Entry(root, width=50)
    grade_entry.grid(row=4, column=1, pady=10, padx=10, sticky="ew")

    comment_label = tk.Label(root, text="Comment:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    comment_label.grid(row=5, column=0, pady=10, padx=10, sticky="w")
    comment_text = tk.Text(root, wrap=tk.WORD, selectforeground=sbg, width=50, height=6, bg="#1f1f1f", fg=fg, insertbackground="#b9b9b9")
    comment_text.grid(row=5, column=1, pady=10, padx=10, sticky="ew")


    # Create a frame for the buttons
    button_frame = tk.Frame(root, bg=bg)
    button_frame.grid(row=6, column=1, columnspan=1)
    
    # Create the buttons
    run_button = ttk.Button(button_frame, text="Run", command=run_command)
    run_button.pack(side=tk.LEFT, pady=20, padx=30)
    stop_button = ttk.Button(button_frame, text="Stop", command=stop_command)
    stop_button.pack(side=tk.LEFT, pady=20, padx=30)




    status_label = tk.Label(root, text="", fg="#1081d6", bg=bg)
    status_label.grid(row=7, column=0, columnspan=3, pady=10, sticky="ew")

    output_label = tk.Label(root, justify="left", text="Output:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    output_label.grid(row=7, column=0, pady=10, padx=10, sticky="ew")

    output_text = tk.Text(root, wrap=tk.WORD,selectforeground=sbg, width=60, height=20, bg=bg, fg=fg, insertbackground="#b9b9b9")
    output_text.grid(row=8, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
    
    tasks_points_label = tk.Label(root, justify="left", text="Tasks and points:", bg=bg, fg=fg, font=('Helvetica', 10, 'bold'))
    tasks_points_label.grid(row=7, column=1, pady=10, padx=10, sticky="ew")
    
    tasks_points_text = tk.Text(root, wrap=tk.WORD,selectforeground=sbg, width=60, height=20, bg=bg, fg=fg, insertbackground="#b9b9b9")
    tasks_points_text.grid(row=8, column=1, columnspan=1, pady=10, padx=10, sticky="nsew")

    clear_button = ttk.Button(root, text="Clear", command=clear_output)
    clear_button.grid(row=9, column=0, columnspan=1, pady=10, padx=10, sticky="we")


    # Bind the Enter+Shift key to the run_command function
    root.bind("<Shift-Return>", run_command)

    global_string.trace_add("write", on_global_string_changed)
    terminal_type_dropdown.bind("<<ComboboxSelected>>", update_terminal_type)
    exercise_entry.bind("<FocusOut>", lambda e: run_custom_command("grady show-exercise",f"Exercise-0{exercise_entry.get()}",False, global_string))

    # Initialize the command executor
    executor = CommandExecutor()

    # Start the main loop
    root.mainloop()
