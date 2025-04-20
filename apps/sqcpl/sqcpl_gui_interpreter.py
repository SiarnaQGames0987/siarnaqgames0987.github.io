import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog  # Ensure messagebox is imported
import re
import time  # Import time module for the stp command


class SQCPLInterpreter:

    
     def __init__(self, master):
        self.master = master
        master.title("SQCPL Interpreter - Dark Mode")
        master.geometry("800x600")

        # Set dark theme colors
        bg_color = "#2E2E2E"
        fg_color = "#FFFFFF"
        text_bg_color = "#1E1E1E"
        button_bg_color = "#444444"
        button_fg_color = "#FFFFFF"

        master.configure(bg=bg_color)

        self.code_text = scrolledtext.ScrolledText(
            master, height=20, font=("Consolas", 12), bg=text_bg_color, fg=fg_color, insertbackground=fg_color
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Add syntax highlighting
        self.code_text.bind("<KeyRelease>", self.syntax_highlight)

        self.run_button = tk.Button(
            master, text="Run", command=self.run_code, bg=button_bg_color, fg=button_fg_color
        )
        self.run_button.pack(pady=5)

        # Add Save and Open buttons
        self.save_button = tk.Button(
            master, text="Save", command=self.save_file, bg=button_bg_color, fg=button_fg_color
        )
        self.save_button.pack(pady=5)

        self.open_button = tk.Button(
            master, text="Open", command=self.open_file, bg=button_bg_color, fg=button_fg_color
        )
        self.open_button.pack(pady=5)

        self.error_counter_label = tk.Label(
            master, text="Errors: 0", bg=bg_color, fg=fg_color, font=("Consolas", 12)
        )
        self.error_counter_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(
            master, height=10, font=("Consolas", 12), bg=text_bg_color, fg=fg_color, insertbackground=fg_color
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for syntax highlighting
        self.code_text.tag_configure("keyword", foreground="blue")

        self.error_count = 0  # Initialize the error counter

     def save_file(self):
        """Save the current code to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sqplf",
            filetypes=[("SQCPL Files", "*.sqplf"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.code_text.get("1.0", tk.END).strip())
                messagebox.showinfo("Save File", f"File saved successfully: {file_path}")
            except Exception as e:
                messagebox.showerror("Save File", f"An error occurred while saving the file: {e}")

     def open_file(self):
        """Open a file and load its content into the code editor."""
        file_path = filedialog.askopenfilename(
            filetypes=[("SQCPL Files", "*.sqplf"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert(tk.END, content)
                messagebox.showinfo("Open File", f"File opened successfully: {file_path}")
            except Exception as e:
                messagebox.showerror("Open File", f"An error occurred while opening the file: {e}")

     def update_error_counter(self):
        """Updates the error counter label."""
        self.error_counter_label.config(text=f"Errors: {self.error_count}")

     def syntax_highlight(self, event=None):
        # List of keywords to highlight
        keywords = ["print", "char", "execute", "if", "else", "elsif", "pass", "crint", "text", "stp"]
        text = self.code_text.get("1.0", tk.END)

        # Remove all existing tags
        for tag in self.code_text.tag_names():
            self.code_text.tag_remove(tag, "1.0", tk.END)

        # Highlight keywords
        for keyword in keywords:
            start_idx = "1.0"
            while True:
                start_idx = self.code_text.search(rf"\b{keyword}\b", start_idx, stopindex=tk.END, regexp=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(keyword)}c"
                self.code_text.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

     def interpret_sqcpl(self, code):
        if ";" in code and "?" not in code:
            return "Fatal error: Use ? instead of ;."
        if not code.strip().endswith('?'):
            return "Error: Code must end with ? character."

        lines = code.strip().split('?')
        variables = {}
        output = ""
        condition_met = None
        self.error_count = 0  # Reset error counter at the start of interpretation
        empty_line_count = 0  # Track the number of empty but correct lines

        for line_no, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:  # Count empty but correct lines
                empty_line_count += 1
                continue

            if line.startswith("#") or line.startswith("!"):  # Ignore comment lines
                continue

            elif line.startswith("crint"):
                if "=" not in line:
                    output += f"❌ Line {line_no}: Missing equals sign in crint command.\n"
                    self.error_count += 1
                    continue
                parts = line[6:].split("=")
                if len(parts) < 2:
                    output += f"❌ Line {line_no}: Invalid crint declaration.\n"
                    self.error_count += 1
                    continue
                var = parts[0].strip()
                val_str = parts[1].strip()
                try:
                    val = int(val_str)
                    variables[var] = val
                except ValueError:
                    output += f"❌ Line {line_no}: Invalid value for {var}.\n"
                    self.error_count += 1
                    continue

            elif line.startswith("stp"):
                try:
                    time_to_wait = int(line[3:].strip())
                    output += f"⏳ Waiting for {time_to_wait} second(s)...\n"
                    time.sleep(time_to_wait)
                except ValueError:
                    output += f"❌ Line {line_no}: Invalid time value for stp command.\n"
                    self.error_count += 1

            elif line.startswith("char"):
                if "=" not in line:
                    output += f"❌ Line {line_no}: Missing equals sign in char command.\n"
                    self.error_count += 1
                    continue
                parts = line[5:].split("=")
                if len(parts) < 2:
                    output += f"❌ Line {line_no}: Invalid char declaration.\n"
                    self.error_count += 1
                    continue
                var = parts[0].strip()
                val = parts[1].strip()
                if len(val) == 1:
                    variables[var] = val
                else:
                    output += f"❌ Line {line_no}: Invalid value for char {var} (Only single characters allowed).\n"
                    self.error_count += 1

            elif line.startswith("text"):
                if "=" not in line:
                    output += f"❌ Line {line_no}: Missing equals sign in text command.\n"
                    self.error_count += 1
                    continue
                parts = line[5:].split("=")
                if len(parts) < 2:
                    output += f"❌ Line {line_no}: Invalid text declaration.\n"
                    self.error_count += 1
                    continue
                var = parts[0].strip()
                val = parts[1].strip()
                if len(val) <= 14000:
                    variables[var] = val
                else:
                    output += f"❌ Line {line_no}: Invalid value for text {var} (Maximum 14000 characters allowed).\n"
                    self.error_count += 1

            elif line.startswith("math"):
                if "=" not in line:
                    output += f"❌ Line {line_no}: Missing equals sign in math command.\n"
                    self.error_count += 1
                    continue
                parts = line[5:].split("=")
                if len(parts) < 2:
                    output += f"❌ Line {line_no}: Invalid math declaration.\n"
                    self.error_count += 1
                    continue
                var = parts[0].strip()
                expression = parts[1].strip()
                try:
                    # Replace variable names in the expression with their values
                    for key, value in variables.items():
                        expression = expression.replace(key, str(value))
                    # Evaluate the math expression
                    result = eval(expression)
                    variables[var] = result
                except Exception as e:
                    output += f"❌ Line {line_no}: Error in math expression: {expression} ({e}).\n"
                    self.error_count += 1

            elif line.startswith("print"):
                content = line[5:].strip()
                if content.startswith('"') and content.endswith('"'):
                    output += content[1:-1] + "\n"
                else:
                    content = content.replace("(", "").replace(")", "").strip()
                    if content in variables:
                        output += str(variables[content]) + "\n"
                    else:
                        output += f"❌ Line {line_no}: Undefined variable {content}.\n"
                        self.error_count += 1

            elif line.startswith("if"):
                if ":" not in line:
                    output += f"❌ Line {line_no}: Missing colon in if statement.\n"
                    self.error_count += 1
                    continue
                condition, command = line[2:].split(":", 1)
                condition = condition.strip()
                if "==" in condition:
                    var, value = condition.split("==")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) == int(value):
                            condition_met = True
                            output += f"Condition met for {var} == {value}\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} == {value}\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif "x=" in condition:  # Handle NOT equals (x=) operator
                    var, value = condition.split("x=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) != int(value):
                            condition_met = True
                            output += f"Condition met for {var} x= {value}\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} != {value}\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif ">=" in condition:  # Handle greater than or equal to (>=) operator
                    var, value = condition.split(">=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) >= int(value):
                            condition_met = True
                            output += f"Condition met for {var} >= {value}\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} >= {value}\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif "<=" in condition:  # Handle less than or equal to (<=) operator
                    var, value = condition.split("<=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) <= int(value):
                            condition_met = True
                            output += f"Condition met for {var} <= {value}\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} <= {value}\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1

            elif line.startswith("elsif") and condition_met is False:
                if ":" not in line:
                    output += f"❌ Line {line_no}: Missing colon in elsif statement.\n"
                    self.error_count += 1
                    continue
                condition, command = line[5:].split(":", 1)
                condition = condition.strip()
                if "==" in condition:
                    var, value = condition.split("==")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) == int(value):
                            condition_met = True
                            output += f"Condition met for {var} == {value} (elsif)\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} == {value} (elsif)\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif "x=" in condition:  # Handle NOT equals (x=) operator
                    var, value = condition.split("x=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) != int(value):
                            condition_met = True
                            output += f"Condition met for {var} != {value} (elsif)\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} != {value} (elsif)\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif ">=" in condition:  # Handle greater than or equal to (>=) operator
                    var, value = condition.split(">=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) >= int(value):
                            condition_met = True
                            output += f"Condition met for {var} >= {value} (elsif)\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} >= {value} (elsif)\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1
                elif "<=" in condition:  # Handle less than or equal to (<=) operator
                    var, value = condition.split("<=")
                    var = var.strip()
                    value = value.strip()
                    if value.isdigit():  # Check if value is a valid integer
                        if variables.get(var, None) <= int(value):
                            condition_met = True
                            output += f"Condition met for {var} <= {value} (elsif)\n"
                            output += self.execute_command(command.strip(), variables)
                        else:
                            condition_met = False
                            output += f"Condition not met for {var} <= {value} (elsif)\n"
                    else:
                        output += f"❌ Line {line_no}: Invalid condition value '{value}' (must be an integer).\n"
                        self.error_count += 1

            elif line.startswith("else") and condition_met is False:
                if ":" not in line:
                    output += f"❌ Line {line_no}: Missing colon in else statement.\n"
                    self.error_count += 1
                    continue
                command = line[5:].strip()
                output += "Else block executed\n"
                condition_met = True
                output += self.execute_command(command, variables)

            elif line.startswith("pass"):
                continue
            elif line.startswith("MB.Show"):  # Handle MB.Show command
                try:
                    args = line[7:].split(",")
                    if len(args) != 2:
                        output += f"❌ Line {line_no}: Invalid MB.Show syntax. Expected 2 arguments.\n"
                        self.error_count += 1
                        continue
                    content = args[0].strip()
                    title = args[1].strip()

                    # Handle variables or text
                    if content.startswith('"') and content.endswith('"'):
                        content = content[1:-1]
                    elif content in variables:
                        content = variables[content]
                    else:
                        output += f"❌ Line {line_no}: Undefined variable {content}.\n"
                        self.error_count += 1
                        continue

                    if title.startswith('"') and title.endswith('"'):
                        title = title[1:-1]
                    elif title in variables:
                        title = variables[title]
                    else:
                        output += f"❌ Line {line_no}: Undefined variable {title}.\n"
                        self.error_count += 1
                        continue

                    # Show the message box
                    messagebox.showinfo(title, content)
                    output += f"✅ MessageBox shown with title '{title}' and content '{content}'.\n"
                except Exception as e:
                    output += f"❌ Line {line_no}: Error in MB.Show command: {e}\n"
                    self.error_count += 1
            

            else:
                # Handle unknown commands
                output += f"❌ Line {line_no}: Unknown command: {line}\n"
                self.error_count += 1

        # Update the error counter label after processing
        self.update_error_counter()

        # Add error and empty line summary
        if self.error_count > 0:
            output += f"\n❌ Found {self.error_count} error(s). The incorrect lines were not executed.\n"
        if empty_line_count > 0:
            output += f"⚠️ Found {empty_line_count} empty but correct line(s).\n"

        return output

    # ...existing code...

     def execute_command(self, command, variables):
        if command.startswith("print"):
            content = command[5:].strip()
            if content.startswith('"') and content.endswith('"'):
                return content[1:-1] + "\n"
            else:
                content = content.replace("(", "").replace(")", "").strip()
                if content in variables:
                    return str(variables[content]) + "\n"
                else:
                    return f"<Undefined {content}>\n"
        elif command.startswith("MB.Show"):  # Added MB.Show command
            args = command[7:].split(",")
            if len(args) != 2:
                return "❌ Invalid MB.Show syntax. Expected 2 arguments.\n"
            content = args[0].strip()
            title = args[1].strip()

            # Handle variables or text
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            elif content in variables:
                content = variables[content]
            else:
                return f"❌ Undefined variable {content}.\n"

            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            elif title in variables:
                title = variables[title]
            else:
                return f"❌ Undefined variable {title}.\n"

            # Show the message box
            messagebox.showinfo(title, content)
            return f"✅ MessageBox shown with title '{title}' and content '{content}'.\n"
        return f"<Unknown command: {command}>\n"

     def run_code(self):
        code = self.code_text.get("1.0", tk.END)
        output = self.interpret_sqcpl(code)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQCPLInterpreter(root)
    root.mainloop()

    def run_code(self):
        code = self.code_text.get("1.0", tk.END)
        output = self.interpret_sqcpl(code) 
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQCPLInterpreter(root)
    root.mainloop()