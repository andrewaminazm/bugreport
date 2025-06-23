import tkinter as tk
from tkinter import scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import threading
import time

def get_xpath(element):
    components = []
    child = element
    while child.tag_name.lower() != 'html':
        parent = child.find_element(By.XPATH, '..')
        children = parent.find_elements(By.XPATH, '*')
        index = 1
        for i, c in enumerate(children, start=1):
            if c == child:
                index = i
                break
        components.append(f'{child.tag_name}[{index}]')
        child = parent
    components.reverse()
    return '/' + '/'.join(components)

def get_css_selector(element):
    tag = element.tag_name
    css_class = element.get_attribute("class")
    if css_class:
        # CSS class ممكن يكون فيها مسافات، نحولها لنقاط
        return f"{tag}.{'.'.join(css_class.split())}"
    else:
        return tag

def scrape_locator(url, element_text, output_widget, btn):
    btn.config(state='disabled')
    output_widget.delete(1.0, tk.END)

    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")  # اختياري: تشغيل بدون واجهة
    edge_options.add_argument("--disable-gpu")

    service = EdgeService(r'C:\Users\Admin\Downloads\edgedriver_win64\msedgedriver.exe')

    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        driver.get(url)
        time.sleep(3)

        element = driver.find_element(By.XPATH, f"//*[text()='{element_text}']")

        # استخراج كل اللّوكيتورز
        xpath = get_xpath(element)
        css_selector = get_css_selector(element)
        element_id = element.get_attribute("id")
        element_name = element.get_attribute("name")
        tag_name = element.tag_name
        class_name = element.get_attribute("class")

        output_widget.insert(tk.END, "كل اللّوكيتورز للعنصر:\n\n")

        output_widget.insert(tk.END, f"XPath:\n{xpath}\n\n")
        output_widget.insert(tk.END, f"CSS Selector:\n{css_selector}\n\n")
        output_widget.insert(tk.END, f"ID:\n{element_id if element_id else 'لا يوجد'}\n\n")
        output_widget.insert(tk.END, f"Name:\n{element_name if element_name else 'لا يوجد'}\n\n")
        output_widget.insert(tk.END, f"Tag Name:\n{tag_name}\n\n")
        output_widget.insert(tk.END, f"Class Name:\n{class_name if class_name else 'لا يوجد'}\n\n")

    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    finally:
        driver.quit()
        btn.config(state='normal')

def on_start(output_widget, url_entry, text_entry, btn):
    url = url_entry.get()
    element_text = text_entry.get()
    if not url or not element_text:
        messagebox.showwarning("تحذير", "من فضلك أدخل رابط الموقع ونص العنصر")
        return
    threading.Thread(target=scrape_locator, args=(url, element_text, output_widget, btn)).start()

root = tk.Tk()
root.title("سحب كل اللّوكيتورز للعنصر باستخدام Edge")

tk.Label(root, text="رابط الموقع:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack()

tk.Label(root, text="نص العنصر (مثلاً: تسجيل الدخول):").pack(pady=5)
text_entry = tk.Entry(root, width=40)
text_entry.pack()

btn = tk.Button(root, text="سحب اللّوكيتورز", command=lambda: on_start(output_text, url_entry, text_entry, btn))
btn.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, width=80, height=20)
output_text.pack(padx=10, pady=10)

root.mainloop()
