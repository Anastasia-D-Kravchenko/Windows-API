# Windows API with Python (`ctypes`)

This repository contains a collection of Python scripts demonstrating how to interact directly with the **Windows API** using the `ctypes` library. The project covers a range of topics from basic UI elements to advanced system administrative tasks like token impersonation and DNS cache dumping.

---

## 📂 Project Structure

### 基础入门 (Basics)

* **`HelloWorld.py`**: The "Hello World" of Windows API. Demonstrates how to load `user32.dll` and call `MessageBoxW` with proper Unicode handling and user interaction evaluation.

### 进程管理 (Process Management)

* **`SpawnProc.py`**: Demonstrates the complex `CreateProcessW` call. It defines necessary C-structures like `STARTUPINFOW` and `PROCESS_INFORMATION` to spawn a new console process and properly close handles to avoid memory leaks.
* **`ProcKiller.py`**: A utility to terminate a process by its window title. It follows the workflow of: Find Window  Get PID  Open Privileged Handle  Terminate.

### 安全与令牌 (Security & Tokens)

* **`OpenToken.py`**: Shows how to access the security descriptor of a process by opening its **Access Token**.
* **`CheckTokenPrivs.py`**: Audits a process's security by translating privilege strings (like `SeDebugPrivilege`) into LUIDs and checking if they are enabled in the token.


* **`ModifyTokenPrivs.py`**: Actively toggles process privileges. It uses `AdjustTokenPrivileges` to enable or disable specific rights within an access token.
* **`Impersonate.py`**: An advanced administrative script that demonstrates **Token Duplication**. It enables `SeDebugPrivilege`, duplicates a target process token, and spawns a new process in that security context.

### 系统探测 (System Inspection)

* **`UndocumentedDNSCall.py`**: Explores undocumented APIs by calling `DnsGetCacheDataTable` from `DNSAPI.dll`. It traverses a C-style **Linked List** to dump the system's DNS resolver cache.

---

## 🛠️ Key Concepts Covered

* **DLL Loading**: Using `ctypes.WinDLL` for standard Windows calling conventions.
* **Structure Mapping**: Defining Python classes that inherit from `ctypes.Structure` to mirror Windows C-structs.
* **Memory Safety**: Explicitly defining `.argtypes` and `.restype` to ensure Python correctly handles pointers and data sizes.
* **Error Handling**: Utilizing `use_last_error=True` to capture system error codes via `kernel32.GetLastError()`.
* **Handle Hygiene**: Rigorous use of `CloseHandle` to maintain system stability and prevent resource leaks.

## ⚠️ Requirements & Usage

1. **Operating System**: Windows 10 or 11.
2. **Privileges**: Many scripts (especially those involving tokens and process termination) require **Administrative Privileges** to function correctly.
3. **Python**: 3.x installed.

```bash
# Example: Running the process killer
python ProcKiller.py

```

---

**Would you like me to create a summary table of the Windows Error Codes you might encounter while running these scripts?**