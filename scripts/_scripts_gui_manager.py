import customtkinter as ctk


app = ctk.CTk()
app.title("DP Icons")
app.geometry("500x600")


def segmented_button_callback(value):
    print("segmented button clicked:", value)

segemented_button = ctk.CTkSegmentedButton(app, values=["Value 1", "Value 2", "Value 3"],
                                                     command=segmented_button_callback)
segemented_button.set("Value 1")
segemented_button.grid(row=0, column=0, padx=150, pady=0)



frame = ctk.CTkFrame(master=app, width=500, height=580)
frame.grid(row=1, column=0)

app.mainloop()