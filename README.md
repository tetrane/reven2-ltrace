## Prerequisite

This script can only be run on Debian Buster.


## Installing

```
$ python3 -m pip install -r requirements.txt
```


## Sample usage

```
$ python3 -m reven2_ltrace --host localhost --port 42777 'c:/windows/explorer.exe'
Generating LALR tables
Generating LALR tables
#465986 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #469486
#468032 ? user32!__ClientCallWinEventProc() = 0x61a1f0 at #764066
#469498 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #760897
#760904 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #765525
#765537 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #2487992
#2487999 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #2494277
#2494289 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #2502468
#2502475 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #2507890
#2507902 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #6632295
#6632302 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #6636923
#6636935 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #7657375
#7657382 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = false at #7662797
#7662809 DWORD user32!MsgWaitForMultipleObjectsEx(DWORD nCount=0, const HANDLE * pHandles=0x0, DWORD dwMilliseconds=4294967295, DWORD dwWakeMask=15615, DWORD dwFlags=0) = 0 at #26668179
#26668186 BOOL user32!PeekMessage(LPMSG lpMsg=0x2a3f880, HWND hWnd=0x0, UINT wMsgFilterMin=0, UINT wMsgFilterMax=0, UINT wRemoveMsg=0) = true at #26671565
#26671572 DWORD kernelbase!GetTickCount() = 582687 at #26671578
#26671616 int user32!TranslateAccelerator(HWND hWnd=0x200b0, HACCEL hAccTable=0x100d9, LPMSG lpMsg=0x2a3f880) = 0 at #26671630
#26671634 BOOL user32!TranslateMessage(const MSG * lpMsg=0x2a3f880) = false at #26671649
#26671651 LRESULT user32!DispatchMessage(const MSG * lpmsg=0x2a3f880) = 0 at #26687018
...
```

Omit the binary path to get a list of all binary executed in the trace.

```
$ python3 -m reven2_ltrace --host localhost --port 42777
c:/windows/explorer.exe
c:/windows/system32/actxprxy.dll
c:/windows/system32/advapi32.dll
c:/windows/system32/apphelp.dll
...
```

## Sample outputs

- Known prototype from msdn: unknown types are processed as `void*` pointers.

```
#6371080 int ws2_32!WSASend(SOCKET s=0x18c, LPWSABUF lpBuffers=0x29fe648, DWORD dwBufferCount=1, LPDWORD lpNumberOfBytesSent=44033604, DWORD dwFlags=0, LPWSAOVERLAPPED lpOverlapped=0xc54f08, LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine=0x0) = 0 at #6389588
```

- Known prototye from `ltrace.conf`: no name for arguments and only pseudo type for arguments

```
#6370896 addr msvcrt!memcpy(addr arg1=0xc8d470, string arg2='Bob: Hello!\r\n' 0xc62359, ulong arg3=13) = 0xc8d470 at #6370940
```

- No prototype known: no argument information, assume return value is an integer.

```
#6785570 ? kernel32!GetLastErrorStub() = 258 at #6785574f
#6785975 ? kernel32!TlsGetValueStub() = 0xc5be80 at #6785984
```

## Resources files

### ltrace.conf

From the original ltrace tool.
See `man 5 ltrace.conf`

```
hex(int) getchar();

; arpa/inet.h
typedef in_addr = struct(hex(uint));
int inet_aton(string, +in_addr*);
```

### ltace-extra.conf

Extend ltrace.conf with custom information.

### msdn-types.conf

Information about types used when parsing prototypes (from msdn.xml or demangled symbol)

```
typedef HANDLE = PVOID;
typedef PHANDLE = HANDLE*;
typedef LPHANDLE = HANDLE*;

typedef HACCEL = HANDLE;
typedef HBITMAP = HANDLE;
```

### msdn.xml

Generated from legacy msdn website.

```
	<fct>
		<name>WSASend</name>
		<proto>int WSASend( __in SOCKET s, __in LPWSABUF lpBuffers, __in DWORD dwBufferCount, __out LPDWORD lpNumberOfBytesSent, __in DWORD dwFlags, __in LPWSAOVERLAPPED lpOverlapped, __in LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine);</proto>
		<cat>None</cat>
		<file>\winsock\wsasend_2.htm</file>
	</fct>
```

## Error messages


```
WAR: No symbol at #<transition>: <details>
```

- The symbol (or binary) is unknown of the ossi module.
- The prototype cannot be retrieved, no argument will be displayed and the return type will default to `int`.


```
WAR: No ret point found for <transition>
WAR: Cannot get ret point for <transition>: <details>
```

- The return point matching the function call cannot be retrieved.
- This might be caused by execution patterns or the actual `ret` not being recorded.
- The return value will not be displayed.


```
WAR: Cannot decode string arg at <transition>: <details>
```

- A decode error occured while trying to read a string from memory.
- Most likely due to the argument being used as an output value.
- Currently this script assumes all arguments are input values and reads them at the call timestamp, this cause garbage value to be read.


```
WAR: Cannot read memory arg at <transition>
WAR: Cannot read string arg at <transition>: <details>
```

- Some argument cannot be read in memory.
- Most likely due to memory not being mapped or pointer not allocated.
- Might be caused by erroneous prototype definition, incorrect symbol resolution or unsupported calling convention.
