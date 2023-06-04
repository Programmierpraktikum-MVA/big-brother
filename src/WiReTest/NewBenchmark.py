import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from sklearn.utils import Bunch
import time
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DBM'))
from DatabaseManagement import BBDB


class BenchmarkApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Benchmark Program")
        self.geometry("300x200")

        self.label = tk.Label(self, text="Enter the number of iterations:")
        self.label.pack()

        self.entry = tk.Entry(self)
        self.entry.pack()

        self.button = tk.Button(self, text="Run Benchmark", command=self.run_benchmark)
        self.button.pack()

        self.progressbar = ttk.Progressbar(self, mode="determinate", length=200)
        self.progressbar.pack()

    def run_benchmark(self):
        try:
            iterations = int(self.entry.get())
            self.button.configure(state=tk.DISABLED)
            self.run_iterations(iterations)
            self.button.configure(state=tk.NORMAL)
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter a number.")

    def run_iterations(self, iterations):
        total_execution_time = 0
        results = []
        self.progressbar["maximum"] = iterations
        self.progressbar["value"] = 0

        for i in range(iterations):
            start_time = time.time()

            # Run code here and measure the execution time
            execution_time = self.run_code()

            end_time = time.time()
            iteration_execution_time = end_time - start_time
            total_execution_time += iteration_execution_time

            results.append((i + 1, iteration_execution_time))

            self.progressbar["value"] = i + 1
            self.update_idletasks()

        # Convert the results to a pandas DataFrame
        df = pd.DataFrame(results, columns=["Iteration", "Execution Time"])

        # Add total execution time to the dataframe
        df.loc["Total"] = ["", total_execution_time]

        # Specify time unit (seconds)
        df["Execution Time"] = df["Execution Time"].apply(lambda x: f"{x:.6f} s")

        messagebox.showinfo("Benchmark Results", df.to_string(index=False))

    def run_code(self):
        # Instantiate the BBDB class and perform database operations
        db = BBDB()

        # Example database operations
        start_time = time.time()

        # Delete existing users (uncomment if error "Username already in use!" appears)
        #existing_users = db.getUsers()
        #for user_id in existing_users:
        #    db.delUser(user_id)

        # Register multiple users
        user_ids = []
        for i in range(10):
            username = f"username{i + 1}"
            user_enc_res_id = f"user_enc_res_id{i + 1}"
            user_id = db.register_user(username, user_enc_res_id)
            user_ids.append(user_id)

        # Add admin relation for each user
        for user_id in user_ids:
            db.addAdminRelation(user_id)

        # Delete all users
        for user_id in user_ids:
            db.delUser(user_id)

        end_time = time.time()
        execution_time = end_time - start_time

        return execution_time


if __name__ == "__main__":
    app = BenchmarkApp()
    app.mainloop()
