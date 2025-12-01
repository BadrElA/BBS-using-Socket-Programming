import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox

class BulletinBoardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulletin Board Client")

        self.sock = None
        self.running = False
        self.name_sent = False

        # Top connection frame
        conn_frame = ttk.LabelFrame(root, text="Connection")
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="e", padx=3, pady=3)
        self.host_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(conn_frame, textvariable=self.host_var, width=15).grid(row=0, column=1, padx=3, pady=3)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="e", padx=3, pady=3)
        self.port_var = tk.StringVar(value="65432")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=7).grid(row=0, column=3, padx=3, pady=3)

        ttk.Label(conn_frame, text="Username:").grid(row=0, column=4, sticky="e", padx=3, pady=3)
        self.username_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.username_var, width=15).grid(row=0, column=5, padx=3, pady=3)

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_btn.grid(row=0, column=6, padx=5, pady=3)

        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_from_server, state="disabled")
        self.disconnect_btn.grid(row=0, column=7, padx=5, pady=3)

        # Middle: messages area
        msg_frame = ttk.LabelFrame(root, text="Messages")
        msg_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.text = tk.Text(msg_frame, wrap="word", state="disabled", height=20)
        self.text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(msg_frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text["yscrollcommand"] = scrollbar.set

        # Bottom: actions
        actions_frame = ttk.LabelFrame(root, text="Group Actions")
        actions_frame.pack(fill="x", padx=10, pady=5)

        # Row 0: group name
        ttk.Label(actions_frame, text="Group:").grid(row=0, column=0, sticky="e", padx=3, pady=3)
        self.group_var = tk.StringVar(value="default")
        ttk.Entry(actions_frame, textvariable=self.group_var, width=15).grid(row=0, column=1, padx=3, pady=3)

        self.join_btn = ttk.Button(actions_frame, text="Join Group", command=self.join_group)
        self.join_btn.grid(row=0, column=2, padx=3, pady=3)

        self.leave_btn = ttk.Button(actions_frame, text="Leave Group", command=self.leave_group)
        self.leave_btn.grid(row=0, column=3, padx=3, pady=3)

        self.users_btn = ttk.Button(actions_frame, text="List Users", command=self.list_users)
        self.users_btn.grid(row=0, column=4, padx=3, pady=3)

        self.groups_btn = ttk.Button(actions_frame, text="List All Groups", command=self.list_groups)
        self.groups_btn.grid(row=0, column=5, padx=3, pady=3)

        # Row 1: subject / message
        ttk.Label(actions_frame, text="Subject:").grid(row=1, column=0, sticky="e", padx=3, pady=3)
        self.subject_var = tk.StringVar()
        ttk.Entry(actions_frame, textvariable=self.subject_var, width=30).grid(row=1, column=1, columnspan=2, padx=3, pady=3, sticky="we")

        ttk.Label(actions_frame, text="Message:").grid(row=2, column=0, sticky="ne", padx=3, pady=3)
        self.message_entry = tk.Text(actions_frame, height=3, width=40)
        self.message_entry.grid(row=2, column=1, columnspan=4, padx=3, pady=3, sticky="we")

        self.post_btn = ttk.Button(actions_frame, text="Post", command=self.post_message)
        self.post_btn.grid(row=2, column=5, padx=3, pady=3)

        # Row 3: message id
        ttk.Label(actions_frame, text="Message ID:").grid(row=3, column=0, sticky="e", padx=3, pady=3)
        self.msg_id_var = tk.StringVar()
        ttk.Entry(actions_frame, textvariable=self.msg_id_var, width=10).grid(row=3, column=1, padx=3, pady=3, sticky="w")

        self.get_msg_btn = ttk.Button(actions_frame, text="Get Message", command=self.get_message)
        self.get_msg_btn.grid(row=3, column=2, padx=3, pady=3)

        self.exit_btn = ttk.Button(actions_frame, text="Exit (Server)", command=self.exit_server)
        self.exit_btn.grid(row=3, column=5, padx=3, pady=3)

        # make columns stretch evenly
        for col in range(0, 6):
            actions_frame.columnconfigure(col, weight=1)

        self.append_text("Fill in host/port/username and press Connect.\n")

        # On window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Utility methods

    def append_text(self, msg: str):
        """Append text safely from any thread."""
        def inner():
            self.text.configure(state="normal")
            self.text.insert("end", msg)
            if not msg.endswith("\n"):
                self.text.insert("end", "\n")
            self.text.see("end")
            self.text.configure(state="disabled")
        self.root.after(0, inner)

    def connect_to_server(self):
        if self.sock is not None:
            messagebox.showinfo("Info", "Already connected.")
            return

        host = self.host_var.get().strip()
        port_str = self.port_var.get().strip()
        username = self.username_var.get().strip()

        if not host or not port_str or not username:
            messagebox.showerror("Error", "Host, port, and username are required.")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be an integer.")
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect: {e}")
            return

        self.sock = s
        self.running = True
        self.name_sent = False

        self.append_text(f"Connected to {host}:{port}")

        # Start receiver thread
        recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
        recv_thread.start()

        # Immediately send username to server
        try:
            self.sock.sendall(username.encode("utf-8"))
            self.name_sent = True
            self.append_text(f"Username '{username}' sent to server.")
        except Exception as e:
            self.append_text(f"Error sending username: {e}")

        self.connect_btn.configure(state="disabled")
        self.disconnect_btn.configure(state="normal")

    def disconnect_from_server(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.append_text("Disconnected from server.")
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")

    def receive_messages(self):
        """Background thread: receive messages from server."""
        while self.running and self.sock:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.append_text("Server disconnected.")
                    break
                msg = data.decode("utf-8", errors="replace")
                self.append_text(msg)
            except OSError:
                break
            except Exception as e:
                self.append_text(f"Receive error: {e}")
                break

        # Clean up on thread exit
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.root.after(0, lambda: (
            self.connect_btn.configure(state="normal"),
            self.disconnect_btn.configure(state="disabled")
        ))

    def send_json(self, payload: dict):
        """Send a JSON command to the server."""
        if not self.sock:
            messagebox.showerror("Error", "Not connected to server.")
            return
        try:
            data = json.dumps(payload).encode("utf-8")
            self.sock.sendall(data)
        except Exception as e:
            self.append_text(f"Send error: {e}")

    # Command handlers

    def join_group(self):
        group = self.group_var.get().strip()
        if not group:
            messagebox.showerror("Error", "Group name is required.")
            return
        payload = {"command": "%groupjoin", "group": group}
        self.send_json(payload)

    def leave_group(self):
        group = self.group_var.get().strip()
        if not group:
            messagebox.showerror("Error", "Group name is required.")
            return
        payload = {"command": "%groupleave", "group": group}
        self.send_json(payload)

    def list_users(self):
        group = self.group_var.get().strip()
        if not group:
            messagebox.showerror("Error", "Group name is required.")
            return
        payload = {"command": "%groupusers", "group": group}
        self.send_json(payload)

    def list_groups(self):
        payload = {"command": "%groups"}
        self.send_json(payload)

    def post_message(self):
        group = self.group_var.get().strip()
        subject = self.subject_var.get().strip()
        message = self.message_entry.get("1.0", "end").strip()

        if not group or not subject or not message:
            messagebox.showerror("Error", "Group, subject, and message are required.")
            return

        payload = {
            "command": "%grouppost",
            "group": group,
            "subject": subject,
            "message": message,
        }
        self.send_json(payload)

    def get_message(self):
        group = self.group_var.get().strip()
        msg_id_str = self.msg_id_var.get().strip()
        if not group or not msg_id_str:
            messagebox.showerror("Error", "Group and message ID are required.")
            return
        try:
            msg_id = int(msg_id_str)
        except ValueError:
            messagebox.showerror("Error", "Message ID must be an integer.")
            return

        payload = {
            "command": "%groupmessage",
            "group": group,
            "message_id": msg_id,
        }
        self.send_json(payload)

    def exit_server(self):
        """Send %exit to server (removes you from groups) and disconnect."""
        payload = {"command": "%exit"}
        self.send_json(payload)
        self.disconnect_from_server()

    def on_close(self):
        """Handle window close."""
        # Try to send exit command
        if self.sock:
            try:
                self.send_json({"command": "%exit"})
            except:
                pass
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BulletinBoardGUI(root)
    root.mainloop()
