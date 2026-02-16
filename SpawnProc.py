import ctypes
from ctypes import wintypes
import sys

# 1. Load Kernel32 DLL
# use_last_error=True allows us to use ctypes.get_last_error() reliably
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)

# 2. Define Structures
# STARTUPINFOW is required for the "Wide" (Unicode) version of CreateProcess
class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

# 3. Setup API Prototypes
# Defining argtypes ensures Python passes the correct pointers and data types to the C function
k_handle.CreateProcessW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, 
    ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD, 
    ctypes.c_void_p, wintypes.LPCWSTR, 
    ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION)
]
k_handle.CreateProcessW.restype = wintypes.BOOL

def spawn_process():
    # 4. Parameters
    app_name = "C:\\Windows\\System32\\cmd.exe"
    creation_flags = 0x00000010  # CREATE_NEW_CONSOLE
    
    # 5. Initialize Structures
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.dwFlags = 0x1             # STARTF_USESHOWWINDOW
    si.wShowWindow = 0x1         # SW_SHOWNORMAL
    
    pi = PROCESS_INFORMATION()

    # 6. Execute CreateProcessW
    # We pass structures by reference (byref) so the API can populate them
    success = k_handle.CreateProcessW(
        app_name, None, None, None, False, 
        creation_flags, None, None, 
        ctypes.byref(si), ctypes.byref(pi)
    )

    if success:
        print(f"[INFO] Process Created! PID: {pi.dwProcessId}")
        
        # 7. Vital Cleanup
        # Windows keeps a reference to the process/thread until handles are closed
        k_handle.CloseHandle(pi.hProcess)
        k_handle.CloseHandle(pi.hThread)
        print("[INFO] Handles closed successfully.")
    else:
        error_code = ctypes.get_last_error()
        print(f"[ERROR] Could not create process. Error Code: {error_code}")

if __name__ == "__main__":
    spawn_process()
