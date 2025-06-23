import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
import csv
from fpdf import FPDF
import cohere
import re

# ------------------------------
API_KEY = "uzJZyN9GN4xgmIAjbN6GuvCOhbUQa2SDLATPtQCy"
co = cohere.Client(API_KEY)
# ------------------------------

# قاعدة البيانات
def init_db():
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bug_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            title TEXT,
            steps TEXT,
            actual_result TEXT,
            expected_result TEXT,
            priority TEXT,
            solutions TEXT,
            bug_type TEXT,
            estimated_time TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_bug_report(desc):
    prompt = f"""
You are a professional QA engineer.

Based on this bug description: "{desc}"

Generate:
- Title:
- Steps to Reproduce:
- Actual Result:
- Expected Result:
- Priority:
- Bug Type:
- Estimated Time to Fix:
- Suggested Solutions:
"""
    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=400,
        temperature=0.3
    )
    return response.generations[0].text.strip()

def split_report(text):
    parts = re.split(r"Suggested Solutions\s*:", text, flags=re.IGNORECASE)
    return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

def parse_fields(text):
    patterns = {
        "title": r"Title\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "steps": r"Steps to Reproduce\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "actual_result": r"Actual Result\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "expected_result": r"Expected Result\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "priority": r"Priority\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "bug_type": r"Bug Type\s*:\s*(.+?)(?=\n[A-Z]|$)",
        "estimated_time": r"Estimated Time to Fix\s*:\s*(.+?)(?=\n[A-Z]|$)",
    }
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        result[key] = match.group(1).strip().replace("\n", " ") if match else ""
    return result

def save_to_db(desc, report, solutions):
    fields = parse_fields(report)
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO bug_reports (description, title, steps, actual_result, expected_result,
        priority, solutions, bug_type, estimated_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        desc,
        fields["title"], fields["steps"], fields["actual_result"], fields["expected_result"],
        fields["priority"], solutions, fields["bug_type"], fields["estimated_time"],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def open_details_window(id_):
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bug_reports WHERE id=?", (id_,))
    row = c.fetchone()
    conn.close()

    win = tk.Toplevel(root)
    win.title("Bug Report Details")
    win.geometry("800x600")
    fields = ["Description", "Title", "Steps", "Actual Result", "Expected Result", "Priority", "Solutions", "Bug Type", "Estimated Time", "Timestamp"]
    for i, val in enumerate(row[1:]):
        tk.Label(win, text=f"{fields[i]}:", font=("Arial", 10, "bold")).grid(row=i*2, column=0, sticky="w", padx=10, pady=(10,0))
        txt = scrolledtext.ScrolledText(win, height=2, wrap=tk.WORD)
        txt.grid(row=i*2+1, column=0, padx=10, sticky="ew")
        txt.insert(tk.END, val)
        txt.config(state=tk.DISABLED)

def refresh_reports():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("SELECT id, timestamp, title, priority FROM bug_reports WHERE DATE(timestamp)=?", (date_filter.get_date().isoformat(),))
    for row in c.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

def run_generator():
    desc = description_box.get("1.0", tk.END).strip()
    if not desc:
        messagebox.showwarning("Warning", "Please enter a bug description.")
        return
    try:
        result = generate_bug_report(desc)
        report, solutions = split_report(result)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, report)
        solutions_box.delete("1.0", tk.END)
        solutions_box.insert(tk.END, solutions)
        save_to_db(desc, report, solutions)
        refresh_reports()
    except Exception as e:
        messagebox.showerror("AI Error", str(e))

def on_double_click(event):
    sel = tree.selection()
    if sel:
        item = tree.item(sel[0])
        open_details_window(item["values"][0])

def delete_selected():
    sel = tree.selection()
    if sel:
        id_ = tree.item(sel[0])["values"][0]
        conn = sqlite3.connect("bug_reports.db")
        c = conn.cursor()
        c.execute("DELETE FROM bug_reports WHERE id=?", (id_,))
        conn.commit()
        conn.close()
        refresh_reports()

def export_pdf():
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bug_reports")
    rows = c.fetchall()
    conn.close()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for row in rows:
        for value in row[1:]:
            pdf.multi_cell(0, 10, str(value))
        pdf.ln()
    fn = filedialog.asksaveasfilename(defaultextension=".pdf")
    if fn:
        pdf.output(fn)
        messagebox.showinfo("Exported", "PDF exported successfully.")

def export_csv():
    conn = sqlite3.connect("bug_reports.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bug_reports")
    rows = c.fetchall()
    conn.close()
    fn = filedialog.asksaveasfilename(defaultextension=".csv")
    if fn:
        with open(fn, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Description", "Title", "Steps", "Actual", "Expected", "Priority", "Solutions", "Type", "ETA", "Timestamp"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", "CSV exported successfully.")

# واجهة المستخدم
init_db()
root = tk.Tk()
root.title("AI-Powered Bug Reporter")
root.geometry("1100x750")

tk.Label(root, text="Bug Description:").grid(row=0, column=0, sticky="w", padx=10)
description_box = scrolledtext.ScrolledText(root, width=140, height=6)
description_box.grid(row=1, column=0, columnspan=4, padx=10)

tk.Button(root, text="🎯 Generate Bug Report", command=run_generator, bg="green", fg="white").grid(row=2, column=0, pady=10)

tk.Label(root, text="Generated Report:").grid(row=3,column=0,sticky="w", padx=10)
output_box = scrolledtext.ScrolledText(root, width=140, height=10)
output_box.grid(row=4, column=0, columnspan=4, padx=10)

tk.Label(root, text="Suggested Solutions:").grid(row=5,column=0,sticky="w", padx=10)
solutions_box = scrolledtext.ScrolledText(root, width=140, height=5)
solutions_box.grid(row=6, column=0, columnspan=4, padx=10)

filter_frame = tk.Frame(root)
filter_frame.grid(row=7, column=0, columnspan=4, sticky="w", padx=10, pady=5)
tk.Label(filter_frame,text="Filter by Date:").grid(row=0,column=0)
date_filter=DateEntry(filter_frame, width=12)
date_filter.grid(row=0,column=1, padx=10)
date_filter.bind("<<DateEntrySelected>>", lambda e: refresh_reports())

columns=("ID","Timestamp","Title","Priority")
tree=ttk.Treeview(root,columns=columns,show="headings",height=12)
for c in columns:
    tree.heading(c,text=c)
    tree.column(c,width=400 if c=="Title" else 120)
tree.grid(row=8,column=0,columnspan=4,padx=10,pady=10, sticky="nsew")
tree.bind("<Double-1>", on_double_click)

tk.Button(root, text="📄 Export PDF", command=export_pdf, bg="#007acc", fg="white", width=15, height=2).grid(row=9, column=0, padx=10, pady=10)
tk.Button(root, text="🗂 Export CSV", command=export_csv, bg="#007acc", fg="white", width=15, height=2).grid(row=9, column=1, padx=10, pady=10)
tk.Button(root, text="🗑 Delete Selected", command=delete_selected, bg="#d9534f", fg="white", width=15, height=2).grid(row=9, column=2, padx=10, pady=10)

root.grid_rowconfigure(9, weight=1)
root.grid_columnconfigure(0, weight=1)

refresh_reports()
root.mainloop()
