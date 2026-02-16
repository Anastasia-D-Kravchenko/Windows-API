import ctypes
from ctypes import wintypes
import sys

# 1. Load DLLs
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
u_handle = ctypes.WinDLL("User32.dll", use_last_error=True)

# 2. Access Rights constants
# PROCESS_ALL_ACCESS provides the necessary privileges to terminate a process.
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)

# 3. Setup API Function Prototypes (Best Practice)
# Explicitly defining argtypes prevents crashes and incorrect memory interpretation.
u_handle.FindWindowA.argtypes = [wintypes.LPCSTR, wintypes.LPCSTR]
u_handle.FindWindowA.restype = wintypes.HWND

u_handle.GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]
u_handle.GetWindowThreadProcessId.restype = wintypes.DWORD

k_handle.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k_handle.OpenProcess.restype = wintypes.HANDLE

k_handle.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
k_handle.TerminateProcess.restype = wintypes.BOOL

def kill_process():
    # 4. Get User Input
    # FindWindowA requires ANSI encoding (UTF-8 bytes).
    window_title = input("Enter Window Name To Kill: ").encode('utf-8')
    
    # 5. Grab Window Handle (HWND)
    h_wnd = u_handle.FindWindowA(None, window_title)
    
    if not h_wnd:
        print(f"[ERROR] Window not found. Last Error: {k_handle.GetLastError()}")
        return

    print("[INFO] Window handle retrieved...")

    # 6. Get PID from Window Handle
    # We pass by reference so the API can update our variable in memory.
    pid = wintypes.DWORD()
    u_handle.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
    
    print(f"[INFO] Target PID identified: {pid.value}")

    # 7. Open Privileged Handle
    # This step often requires Administrative privileges to avoid 'Access Denied' (Error 5).
    h_process = k_handle.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    
    if not h_process:
        print(f"[ERROR] Could not open privileged handle. Last Error: {k_handle.GetLastError()}")
        return

    print("[INFO] Privileged handle opened...")

    # 8. Terminate the Process
    exit_code = 0x1
    success = k_handle.TerminateProcess(h_process, exit_code)

    if success:
        print("[SUCCESS] Process terminated successfully.")
    else:
        print(f"[ERROR] Termination failed. Last Error: {k_handle.GetLastError()}")

    # Clean up the handle
    k_handle.CloseHandle(h_process)

if __name__ == "__main__":
    kill_process()
