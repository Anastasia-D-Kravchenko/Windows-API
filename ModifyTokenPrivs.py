import ctypes
from ctypes import wintypes

# 1. Load DLLs with strict error checking
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
u_handle = ctypes.WinDLL("User32.dll", use_last_error=True)
a_handle = ctypes.WinDLL("Advapi32.dll", use_last_error=True)

# 2. Security Constants
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
# For adjusting, we need QUERY (to see current state) and ADJUST_PRIVILEGES (to change it)
TOKEN_ALL_ACCESS = 0xF00FF 
SE_PRIVILEGE_ENABLED = 0x00000002
SE_PRIVILEGE_DISABLED = 0x00000000

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
        ("Privileges", LUID_AND_ATTRIBUTES * 1),
    ]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", wintypes.DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 1),
    ]

# 4. Setup API Function Prototypes
a_handle.LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]
a_handle.LookupPrivilegeValueW.restype = wintypes.BOOL

a_handle.PrivilegeCheck.argtypes = [wintypes.HANDLE, ctypes.POINTER(PRIVILEGE_SET), ctypes.POINTER(wintypes.BOOL)]
a_handle.PrivilegeCheck.restype = wintypes.BOOL

# AdjustTokenPrivileges Prototype
a_handle.AdjustTokenPrivileges.argtypes = [
    wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(TOKEN_PRIVILEGES),
    wintypes.DWORD, ctypes.POINTER(TOKEN_PRIVILEGES), ctypes.POINTER(wintypes.DWORD)
]
a_handle.AdjustTokenPrivileges.restype = wintypes.BOOL

def modify_privilege():
    # 5. Acquire Handles
    window_name = input("Enter Window Name To Hook Into: ").encode('utf-8')
    h_wnd = u_handle.FindWindowA(None, window_name)
    if not h_wnd: return

    pid = wintypes.DWORD()
    u_handle.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
    
    h_process = k_handle.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    h_token = wintypes.HANDLE()
    k_handle.OpenProcessToken(h_process, TOKEN_ALL_ACCESS, ctypes.byref(h_token))

    # 6. Lookup LUID for SeDebugPrivilege
    target_luid = LUID()
    priv_name = "SeDebugPrivilege"
    a_handle.LookupPrivilegeValueW(None, priv_name, ctypes.byref(target_luid))

    # 7. Check Current Status
    priv_set = PRIVILEGE_SET()
    priv_set.PrivilegeCount = 1
    priv_set.Privileges[0].Luid = target_luid
    priv_set.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
    
    is_enabled = wintypes.BOOL()
    a_handle.PrivilegeCheck(h_token, ctypes.byref(priv_set), ctypes.byref(is_enabled))

    # 8. Setup New State (Toggle)
    new_state = TOKEN_PRIVILEGES()
    new_state.PrivilegeCount = 1
    new_state.Privileges[0].Luid = target_luid
    
    if is_enabled.value:
        print(f"[INFO] {priv_name} is Enabled. Disabling...")
        new_state.Privileges[0].Attributes = SE_PRIVILEGE_DISABLED
    else:
        print(f"[INFO] {priv_name} is Disabled. Enabling...")
        new_state.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

    # 9. Adjust the Token
        
    # We pass the new_state and ignore PreviousState/ReturnLength by passing None/Null pointers
    success = a_handle.AdjustTokenPrivileges(h_token, False, ctypes.byref(new_state), 0, None, None)

    # Note: AdjustTokenPrivileges can return True even if it failed to adjust ALL privileges.
    # We must check GetLastError for ERROR_NOT_ALL_ASSIGNED (1300).
    last_err = k_handle.GetLastError()
    
    if success and last_err == 0:
        print(f"[SUCCESS] {priv_name} status has been flipped.")
    else:
        print(f"[ERROR] Modification failed. Error Code: {last_err}")

    # 10. Final Cleanup
    k_handle.CloseHandle(h_token)
    k_handle.CloseHandle(h_process)

if __name__ == "__main__":
    modify_privilege()
