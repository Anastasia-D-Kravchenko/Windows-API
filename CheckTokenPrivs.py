import ctypes
from ctypes import wintypes
import sys

# 1. Load DLLs with error tracking enabled
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
u_handle = ctypes.WinDLL("User32.dll", use_last_error=True)
a_handle = ctypes.WinDLL("Advapi32.dll", use_last_error=True)

# 2. Security Constants
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x00000002

# 3. Define Required Structures
class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG),
    ]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", wintypes.DWORD),
    ]

class PRIVILEGE_SET(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", wintypes.DWORD),
        ("Control", wintypes.DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 1), # Define as an array of size 1
    ]

# 4. Setup API Function Prototypes
a_handle.LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]
a_handle.LookupPrivilegeValueW.restype = wintypes.BOOL

a_handle.PrivilegeCheck.argtypes = [wintypes.HANDLE, ctypes.POINTER(PRIVILEGE_SET), ctypes.POINTER(wintypes.BOOL)]
a_handle.PrivilegeCheck.restype = wintypes.BOOL

def check_privilege():
    # 5. Target the Window and get Handle/PID
    window_title = input("Enter Window Name To Hook Into: ").encode('utf-8')
    h_wnd = u_handle.FindWindowA(None, window_title)
    
    if not h_wnd:
        print(f"[ERROR] Window not found. Error: {k_handle.GetLastError()}")
        return

    pid = wintypes.DWORD()
    u_handle.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))

    # 6. Open Process and Token
    # We only need TOKEN_QUERY access to check for privileges
    h_process = k_handle.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    h_token = wintypes.HANDLE()
    k_handle.OpenProcessToken(h_process, TOKEN_QUERY, ctypes.byref(h_token))

    # 7. Map Privilege String to LUID
    # This translates "SeDebugPrivilege" into the system's LUID format
        
    target_luid = LUID()
    priv_name = "SeDebugPrivilege"
    
    if not a_handle.LookupPrivilegeValueW(None, priv_name, ctypes.byref(target_luid)):
        print(f"[ERROR] Lookup failed. Error: {k_handle.GetLastError()}")
        return

    print(f"[INFO] LUID for {priv_name} retrieved...")

    # 8. Perform the Privilege Check
    # We populate the PRIVILEGE_SET structure to ask: "Is this specific LUID enabled?"
    priv_set = PRIVILEGE_SET()
    priv_set.PrivilegeCount = 1
    priv_set.Privileges[0].Luid = target_luid
    priv_set.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
    
    is_result_enabled = wintypes.BOOL()
    
    success = a_handle.PrivilegeCheck(h_token, ctypes.byref(priv_set), ctypes.byref(is_result_enabled))

    if success:
        status = "ENABLED" if is_result_enabled.value else "NOT ENABLED"
        print(f"[RESULT] {priv_name} is currently {status}")
    else:
        print(f"[ERROR] PrivilegeCheck failed. Error: {k_handle.GetLastError()}")

    # 9. Cleanup Handles
    k_handle.CloseHandle(h_token)
    k_handle.CloseHandle(h_process)

if __name__ == "__main__":
    check_privilege()
