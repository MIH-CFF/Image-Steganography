import os
import sys
import threading
import math
import zlib
import numpy as np
from PIL import Image, ImageTk
from bitarray import bitarray
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter import filedialog
from tkinter import messagebox as msg
from process import*
def main():
    app = tk.Tk()
    global bg,fg
    bg='black'
    fg='#00FF00'
    state=0
    app.title("Steganography")
    logo=ImageTk.PhotoImage(Image.open("images\\logo.png"))
    app.iconphoto(True,logo)
    app.geometry("800x600+300+100")
    app.update()
    app.configure(bg=bg)
    # Fuctions
    def encode_func():
        app.destroy()
        encode()
    def decode_func():
        app.destroy()
        decode()
    label = tk.Label(app, text="Choose operation :",font=('arial','35','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    label.place(relx=0.2, rely=0.2, relwidth=0.6)
    
     # encode button
    encode_btn = tk.Button(app, text="Encode text",relief='groove',bd=5, command=encode_func,font=('arial','26','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    encode_btn.place(relx=0.2, rely=0.4, relwidth=0.6, relheight=0.1)
    
     # decode button
    encode_btn = tk.Button(app, text="Decode text",relief='groove',bd=5, command=decode_func,font=('arial','26','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    encode_btn.place(relx=0.2, rely=0.6, relwidth=0.6, relheight=0.1)
    
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("Application Interrupted")

def encode():
    encode_ui = tk.Tk()
    global state,image_path,input_path,enc_img,tk_image,input_txt
    tk_image=None
    input_txt=None
    state=False
    global bg,fg
    bg='black'
    fg='#00FF00'
    state=0
    encode_ui.title("Steganography")
    logo=ImageTk.PhotoImage(Image.open("images\\logo.png"))
    encode_ui.iconphoto(True,logo)
    encode_ui.geometry("800x600+300+100")
    encode_ui.update()
    encode_ui.configure(bg=bg)
    # Fuctions
    def browse_image():
        global image_path
        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if image_path:
            try:
                show_image(image_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image:\n{e}")
    def show_image(path):
        img = res(Image.open(path),0.3,0.3)
        global tk_image
        tk_image = ImageTk.PhotoImage(img)
        image_label.config(image=tk_image)
    def download_img():
        global state
        if not state:
            msg.showerror("Error","Please select and encode first!") 
        else:
            global enc_img
            try:
                if enc_img!=None:
                    download_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
                    if download_path:
                        enc_img.save(download_path)
                    else:
                        msg.showerror("Error","Error try again")
            except:
                msg.showerror("Error","Encode Image first")
    def res(img,x,y):
        label_width = int(x * encode_ui.winfo_width())
        label_height= int(y * encode_ui.winfo_height())
        try:
            img = img.resize((label_width, label_height), Image.ANTIALIAS)
        except AttributeError:
            img = img.resize((label_width, label_height), Image.LANCZOS)
        return img 
    def encode_txt():
        global tk_image,input_txt
        input_txt=text_box.get("1.0", tk.END)
        if tk_image is None:
            msg.showerror("Error","Please Select image first!")
            return        
        if input_txt is None:
            msg.showerror("Error","Please Input text first!")
            return
        show_loading()
        threading.Thread(target=process_image, daemon=True).start() 
    def process_image():
        global image_path,input_txt,enc_img,tk_image2,state
        input_txt=input_txt.encode("utf-8")
        enc_img=encode_image(image_path,input_txt)
        state=True
        tk_image2 = ImageTk.PhotoImage(res(enc_img,0.3,0.3))
        encode_ui.after(0, update_gui) 

    def update_gui():
        close_loading()
        enc_image_label.config(image=tk_image2, bd=2)
        
    def show_loading():
        global loading_window, progress_bar

        loading_window = tk.Toplevel(encode_ui)
        loading_window.title("Encoding")
        loading_window.geometry("300x120+550+340")
        loading_window.configure(bg=bg)
        loading_window.resizable(False, False)

        label = tk.Label(
            loading_window,
            text="Encoding Image...\nPlease wait",
            font=('arial',12,'bold'),
            bg=bg,
            fg=fg
        )
        label.pack(pady=10)

        progress_bar = ttk.Progressbar(
            loading_window,
            mode='indeterminate',
            length=200
        )
        progress_bar.pack(pady=10)

        progress_bar.start(10)

        loading_window.transient(encode_ui)
        loading_window.grab_set()
    
    def close_loading():
        progress_bar.stop()
        loading_window.destroy()
        
    def back():
        encode_ui.destroy()
        main()
        
    def browse_text():
        global input_txt,input_path
        input_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if input_path:
            try:
                with open(input_path, "r", encoding="utf-8") as file:
                    input_txt = file.read()
                text_box.delete("1.0", tk.END)
                text_box.insert("1.0", input_txt)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file:\n{e}")
    
    # Browse Buttons
    img_browse_btn = tk.Button(encode_ui, text="Browse Image",relief='groove',bd=3, command=browse_image,font=('arial','10','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    img_browse_btn.place(relx=0.125, rely=0.02, relwidth=0.25, relheight=0.06)
    txt_browse_btn = tk.Button(encode_ui, text="Browse Plaintext",relief='groove',bd=3, command=browse_text,font=('arial','10','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    txt_browse_btn.place(relx=0.625, rely=0.02, relwidth=0.25, relheight=0.06)
    
    dem1=Image.open('images\\demo.jpg')
    demo=ImageTk.PhotoImage(res(dem1,0.3,0.3))
    dnld1=Image.open('images\\dw.png')
    dnld=ImageTk.PhotoImage(res(dnld1,0.03,0.03))
    # Image Display Label
    image_label = tk.Label(encode_ui,image=demo,bg=bg)
    image_label.place(relx=0.1, rely=0.1, relheight=0.3)
    
    image_1des = tk.Label(encode_ui,text='Original Image',font=('arial','10','bold'),bg=bg,fg=fg)
    image_1des.place(relx=0.15, rely=0.42, relwidth=0.2)
    
    frame = tk.Frame(encode_ui)
    frame.place(relx=0.6, rely=0.1, relheight=0.3,relwidth=0.3)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_box = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_box.yview)
    
    txt_1des = tk.Label(encode_ui,text='Plain text',font=('arial','10','bold'),bg=bg,fg=fg)
    txt_1des.place(relx=0.65, rely=0.42, relwidth=0.2)
    
    encode_btn = tk.Button(encode_ui, text="Encode text",relief='groove',bd=3, command=encode_txt,font=('arial','10','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    encode_btn.place(relx=0.375, rely=0.46, relwidth=0.25,relheight=0.06)
    
    enc_image_label = tk.Label(encode_ui,image=demo,bg=bg)
    enc_image_label.place(relx=0.35, rely=0.55, relheight=0.3)
    
    image_2des = tk.Label(encode_ui,text='encoded Image',font=('arial','10','bold'),bg=bg,fg=fg)
    image_2des.place(relx=0.4, rely=0.87, relwidth=0.15,relheight=0.05)
    
    download_btn = tk.Button(encode_ui,image=dnld,relief='flat',borderwidth=0, command=download_img,bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    download_btn.place(relx=0.56, rely=0.87, relwidth=0.04,relheight=0.05)
    
    back_btn = tk.Button(encode_ui, text="Back",relief='groove',bd=3, command=back,font=('arial','10','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    back_btn.place(relx=0.375, rely=0.93, relwidth=0.25,relheight=0.06)
    
    try:
        encode_ui.mainloop()
    except KeyboardInterrupt:
        print("Application Interrupted")

def decode():
    decode_ui = tk.Tk()
    global state,image_path,tk_image,plain_txt
    tk_image=None
    input_txt=None
    state=False
    global bg,fg
    bg='black'
    fg='#00FF00'
    state=0
    decode_ui.title("Steganography")
    logo=ImageTk.PhotoImage(Image.open("images\\logo.png"))
    decode_ui.iconphoto(True,logo)
    decode_ui.geometry("800x600+300+100")
    decode_ui.update()
    decode_ui.configure(bg=bg)
    # Fuctions
    def res(img,x,y):
        label_width = int(x * decode_ui.winfo_width())
        label_height= int(y * decode_ui.winfo_width())
        try:
            img = img.resize((label_width, label_height), Image.ANTIALIAS)
        except AttributeError:
            img = img.resize((label_width, label_height), Image.LANCZOS)
        return img
    def browse_image():
        global image_path
        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if image_path:
            try:
                show_image(image_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image:\n{e}")
    def show_image(path):
        img = res(Image.open(path),0.4,0.4)
        global tk_image
        tk_image = ImageTk.PhotoImage(img)
        image_label.config(image=tk_image)
    def download_txt():
        global state,plain_txt
        if not state:
            msg.showerror("Error", "Please select and decode first!") 
        else:
            if not plain_txt:
                msg.showerror("Error", "There is no text to save!")
                return
            try:
                download_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if download_path:
                    with open(download_path, "w", encoding="utf-8") as file:
                        file.write(plain_txt)
                    msg.showinfo("Success", "File saved successfully!")
                    
            except Exception as e:
                msg.showerror("Error", f"Failed to save file: {str(e)}")
    def decode_txt():
        global tk_image,input_txt
        if tk_image is None:
            msg.showerror("Error","Please Select image first!")
            return        
        show_loading()
        threading.Thread(target=process_image, daemon=True).start() 
    def process_image():
        global image_path,plain_txt,state
        plain_txt=decode_image(image_path)
        state=True
        decode_ui.after(0, update_gui) 

    def update_gui():
        close_loading()
        insert_text()
        
    def show_loading():
        global loading_window, progress_bar

        loading_window = tk.Toplevel(decode_ui)
        loading_window.title("Decoding")
        loading_window.geometry("300x120+550+340")
        loading_window.configure(bg=bg)
        loading_window.resizable(False, False)

        label = tk.Label(
            loading_window,
            text="Decoding Image...\nPlease wait",
            font=('arial',12,'bold'),
            bg=bg,
            fg=fg
        )
        label.pack(pady=10)

        progress_bar = ttk.Progressbar(
            loading_window,
            mode='indeterminate',
            length=200
        )
        progress_bar.pack(pady=10)

        progress_bar.start(10)

        loading_window.transient(decode_ui)
        loading_window.grab_set()
    
    def close_loading():
        progress_bar.stop()
        loading_window.destroy()
        
    def back():
        decode_ui.destroy()
        main()
        
    def insert_text():
        global plain_txt
        if plain_txt:
            try:
                text_box.delete("1.0", tk.END)
                text_box.insert("1.0", plain_txt)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file:\n{e}")
    
    # Browse Buttons
    img_browse_btn = tk.Button(decode_ui, text="Browse Image",relief='groove',bd=3, command=browse_image,font=('arial','10','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    img_browse_btn.place(relx=0.1, rely=0.05, relwidth=0.3, relheight=0.08)
    
    dem1=Image.open('images\\demo.jpg')
    demo=ImageTk.PhotoImage(res(dem1,0.4,0.4))
    dnld1=Image.open('images\\dw.png')
    dnld=ImageTk.PhotoImage(res(dnld1,0.03,0.03))
    # Image Display Label
    image_label = tk.Label(decode_ui,image=demo,bg=bg)
    image_label.place(relx=0.05, rely=0.15, relwidth=0.4)
    
    image_1des = tk.Label(decode_ui,text='Encoded Image',font=('arial','15','bold'),bg=bg,fg=fg)
    image_1des.place(relx=0.15, rely=0.7, relwidth=0.2)
    
    frame = tk.Frame(decode_ui)
    frame.place(relx=0.55, rely=0.15,relwidth=0.4,relheight=0.5)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_box = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_box.yview)
    
    txt_1des = tk.Label(decode_ui,text='Decoded text',font=('arial','15','bold'),bg=bg,fg=fg)
    txt_1des.place(relx=0.63, rely=0.7, relwidth=0.2)
    
    download_btn = tk.Button(decode_ui,image=dnld,relief='flat',borderwidth=0, command=download_txt,bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    download_btn.place(relx=0.83, rely=0.7, relwidth=0.04,relheight=0.05)
    
    encode_btn = tk.Button(decode_ui, text="Decode text",relief='groove',bd=3, command=decode_txt,font=('arial','15','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    encode_btn.place(relx=0.375, rely=0.8, relwidth=0.25,relheight=0.08)
    
    back_btn = tk.Button(decode_ui, text="Back",relief='groove',bd=3, command=back,font=('arial','15','bold'),bg=bg,fg=fg,activebackground=bg,activeforeground=fg)
    back_btn.place(relx=0.375, rely=0.9, relwidth=0.25,relheight=0.08)
    
    try:
        decode_ui.mainloop()
    except KeyboardInterrupt:
        print("Application Interrupted")

if __name__ == "__main__":
    main()