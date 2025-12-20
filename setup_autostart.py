import subprocess
import os
import sys

# Bu skript Windows Task Scheduler ga server uchun vazifa qo'shadi
# Foydalanish: python setup_autostart.py

script_dir = os.path.dirname(os.path.abspath(__file__))
server_path = os.path.join(script_dir, "yangi", "face_server.py")
python_path = sys.executable

# Vazifa nomi
task_name = "FaceRecognitionServer"

# XML fayl yaratish
xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{server_path}"</Arguments>
      <WorkingDirectory>{os.path.join(script_dir, "yangi")}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''

# XML faylni saqlash
xml_path = os.path.join(script_dir, "face_server_task.xml")
with open(xml_path, "w", encoding="utf-16") as f:
    f.write(xml_content)

print("=" * 50)
print("Face Recognition Server - Avtostart O'rnatish")
print("=" * 50)
print()

# Task Scheduler ga qo'shish
try:
    # Avval eski vazifani o'chirish
    subprocess.run(
        ["schtasks", "/delete", "/tn", task_name, "/f"],
        capture_output=True
    )
    
    # Yangi vazifa qo'shish
    result = subprocess.run(
        ["schtasks", "/create", "/tn", task_name, "/xml", xml_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("[OK] Server avtomatik ishga tushish sozlandi!")
        print()
        print("Vazifa:", task_name)
        print("Server: http://localhost:5000")
        print()
        print("Kompyuter yoqilganda va internetga ulanganda")
        print("server avtomatik ishga tushadi.")
    else:
        print("[XATOLIK]", result.stderr)
        print()
        print("Qo'lda o'rnatish:")
        print("1. Win+R bosing")
        print("2. taskschd.msc yozing")
        print("3. 'Vazifa yaratish' ni tanlang")
        print(f"4. Python: {python_path}")
        print(f"5. Argument: {server_path}")
        
except Exception as e:
    print(f"[XATOLIK] {e}")

# XML faylni o'chirish
try:
    os.unlink(xml_path)
except:
    pass

print()
print("=" * 50)
input("Davom etish uchun Enter bosing...")
