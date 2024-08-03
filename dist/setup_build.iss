[Setup]
AppName=Charlie Dont Surf
AppVersion=1.0
DefaultDirName={pf}\CharlieDontSurf
DefaultGroupName=CharlieDontSurf
OutputBaseFilename=CharlieDontSurfSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "cds\cds.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "cds\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Charlie Dont Surf"; Filename: "{app}\cds.exe"

[Run]
Filename: "{app}\cds.exe"; Description: "{cm:LaunchProgram,Charlie Dont Surf}"; Flags: nowait postinstall skipifsilent
