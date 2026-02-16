import ctypes
from ctypes import wintypes

# 1. Load DLLs with error tracking enabled
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
u_handle = ctypes.WinDLL("User32.dll", use_last_error=True)

# 2. Access Rights Constants
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)

# Token Access Rights
TOKEN_QUERY = 0x0008
TOKEN_READ = (0x00020000 | TOKEN_QUERY) # STANDARD_RIGHTS_READ | TOKEN_QUERY
TOKEN_ALL_ACCESS = 0xF00FF # Simplified combined mask for all token rights

# 3. Setup API Prototypes for memory safety
u_handle.FindWindowA.argtypes = [wintypes.LPCSTR, wintypes.LPCSTR]
u_handle.FindWindowA.restype = wintypes.HWND

u_handle.GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]
u_handle.GetWindowThreadProcessId.restype = wintypes.DWORD

k_handle.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k_handle.OpenProcess.restype = wintypes.HANDLE

# OpenProcessToken expects (ProcessHandle, DesiredAccess, TokenHandlePointer)
k_handle.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
k_handle.OpenProcessToken.restype = wintypes.BOOL

def open_process_token():
    # 4. Target the Window
    window_title = input("Enter Window Name To Hook Into: ").encode('utf-8')
    h_wnd = u_handle.FindWindowA(None, window_title)

    if not h_wnd:
        print(f"[ERROR] Window not found. Error: {k_handle.GetLastError()}")
        return

    # 5. Retrieve PID
    pid = wintypes.DWORD()
    u_handle.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
    print(f"[INFO] Found PID: {pid.value}")

    # 6. Open Process Handle
    h_process = k_handle.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        print(f"[ERROR] Failed to open process. Error: {k_handle.GetLastError()}")
        return

    print("[INFO] Privileged Process Handle Opened...")

    # 7. Open the Access Token
    # An access token contains the security descriptor for the process
        
    h_token = wintypes.HANDLE()
    # We pass h_token by reference so the API can populate it with the token handle
    success = k_handle.OpenProcessToken(h_process, TOKEN_ALL_ACCESS, ctypes.byref(h_token))

    if success:
        print(f"[INFO] Process Token Handle Created! Handle ID: {h_token.value}")
        
        # 8. Cleanup
        # Always close handles when finished to free system resources
        k_handle.CloseHandle(h_token)
        print("[INFO] Token handle closed.")
    else:
        print(f"[ERROR] Could not open process token. Error: {k_handle.GetLastError()}")

    k_handle.CloseHandle(h_process)

if __name__ == "__main__":
    open_process_token()
