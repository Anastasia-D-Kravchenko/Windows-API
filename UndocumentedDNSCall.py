import ctypes
from ctypes import wintypes

# 1. Load DLLs
# use_last_error=True is essential for capturing Windows system errors reliably
k_handle = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
dns_handle = ctypes.WinDLL("DNSAPI.dll", use_last_error=True)

# 2. Define the Undocumented Structure
# This represents a single node in the DNS cache linked list
class DNS_CACHE_ENTRY(ctypes.Structure):
    pass

# We define the fields separately to allow the self-referencing pNext pointer
DNS_CACHE_ENTRY._fields_ = [
    ("pNext", ctypes.POINTER(DNS_CACHE_ENTRY)), # Pointer to the next cache entry
    ("recName", wintypes.LPWSTR),               # Record Name (e.g., google.com)
    ("wType", wintypes.DWORD),                 # Record Type (e.g., A, AAAA, CNAME)
    ("wDataLength", wintypes.DWORD),           # Length of the data
    ("dwFlags", wintypes.DWORD),               # Cache flags
]

# 3. Setup API Prototype
# DnsGetCacheDataTable returns a Boolean success value
dns_handle.DnsGetCacheDataTable.argtypes = [ctypes.POINTER(ctypes.POINTER(DNS_CACHE_ENTRY))]
dns_handle.DnsGetCacheDataTable.restype = wintypes.BOOL

def dump_dns_cache():
    print("[INFO] Pulling DNS Cache Data From System...")

    # 4. Initialize the pointer
    # The API expects a pointer to a pointer to the first entry
    p_entry = ctypes.POINTER(DNS_CACHE_ENTRY)()

    # 5. Execute the Undocumented Call
    # Passing the address of our pointer (pointer to a pointer)
    success = dns_handle.DnsGetCacheDataTable(ctypes.byref(p_entry))

    if not success:
        error_code = k_handle.GetLastError()
        print(f"[ERROR] Failed to get DNS Cache Table. Error Code: {error_code}")
        return

    print("[INFO] Successfully retrieved DNS Cache Table. Parsing...")

    # 6. Iterate through the Linked List
    # Undocumented APIs often return a linked list structure
        
    current_node = p_entry
    count = 0

    while current_node:
        try:
            # Check if recName exists before printing to avoid Null Pointer exceptions
            record_name = current_node.contents.recName
            record_type = current_node.contents.wType
            
            if record_name:
                print(f"[ENTRY {count}] Name: {record_name} | Type: {record_type}")
                count += 1
            
            # Move current_node to the next pointer in the list
            current_node = current_node.contents.pNext
            
        except Exception as e:
            print(f"[DEBUG] Reached end of list or encountered error: {e}")
            break

    print(f"[INFO] DNS Cache Table Dumped. {count} records found.")

if __name__ == "__main__":
    dump_dns_cache()
