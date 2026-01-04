import tkinter as tk
from tkinter import messagebox

# ------------------ Prediction Logic ------------------ #
def predict_disease(symptoms):
    fever = symptoms['fever']
    headache = symptoms['headache']
    vomiting = symptoms['vomiting']
    joint_pain = symptoms['joint_pain']
    fatigue = symptoms['fatigue']

    # Simple rule-based prediction
    if fever and headache and fatigue and joint_pain:
        return "Dengue"
    elif fever and vomiting and headache:
        return "Typhoid"
    elif fever and fatigue and vomiting:
        return "Malaria"
    elif fever and headache:
        return "Flu"
    else:
        return "Unknown — Please consult a doctor"

# ------------------ GUI Functions ------------------ #
def on_predict():
    symptoms = {
        'fever': fever_var.get(),
        'headache': headache_var.get(),
        'vomiting': vomiting_var.get(),
        'joint_pain': jointpain_var.get(),
        'fatigue': fatigue_var.get()
    }
    disease = predict_disease(symptoms)
    messagebox.showinfo("Prediction Result", f"Predicted Disease: {disease}")

# ------------------ GUI ------------------ #
root = tk.Tk()
root.title("Disease Prediction App")
root.geometry("350x350")

title = tk.Label(root, text="Select Symptoms", font=("Arial", 16))
title.pack(pady=10)

# Variables for checkboxes
fever_var = tk.IntVar()
headache_var = tk.IntVar()
vomiting_var = tk.IntVar()
jointpain_var = tk.IntVar()
fatigue_var = tk.IntVar()

# Symptom checkboxes
tk.Checkbutton(root, text="Fever", variable=fever_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Headache", variable=headache_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Vomiting", variable=vomiting_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Joint Pain", variable=jointpain_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Fatigue / Thakan", variable=fatigue_var).pack(anchor="w", padx=20)

# Predict button
predict_btn = tk.Button(root, text="Predict Disease", font=("Arial", 12), command=on_predict)
predict_btn.pack(pady=20)

# Run the GUI
root.mainloop()
