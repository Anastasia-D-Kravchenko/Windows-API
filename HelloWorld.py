import ctypes
from ctypes import wintypes

# 1. Load the DLLs using WinDLL (standard for Windows API)
user32 = ctypes.WinDLL("user32.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")

# 2. Define constants for clarity (uType)
# MB_OKCANCEL = 0x00000001
# IDOK = 1, IDCANCEL = 2
MB_OKCANCEL = 1 

# 3. Setup parameters using Unicode strings for MessageBoxW
hWnd = None
lpText = "Hello World"
lpCaption = "Hello Students!"
uType = MB_OKCANCEL

# 4. Explicitly define the argument types for MessageBoxW
# This prevents data type mismatches between Python and the C-based API
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]

# 5. Call the Windows API
# MessageBoxW expects pointers to wide characters (Unicode)
response = user32.MessageBoxW(hWnd, lpText, lpCaption, uType)

# 6. Check for system errors
error = kernel32.GetLastError()
if error != 0:
    print(f"System Error Code: {error}")
    exit(1)

# 7. Evaluate User Interaction
if response == 1:
    print("User clicked: OK")
elif response == 2:
    print("User clicked: Cancel/Exit")
