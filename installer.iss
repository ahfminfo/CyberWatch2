; Samaneh Nezarat Setup Script
; Version 11.0

#define MyAppName "Samaneh Nezarat"
#define MyAppVersion "11.2"
#define MyAppPublisher "AHFMInfo"
#define MyAppExeName "SamanehNezarat.exe"

[Setup]
AppId={{A3F5B8D2-7C4E-4E5B-9B1F-8D3C2A1F5E9B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SamanehNezarat
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=SamanehNezarat-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
MinVersion=6.1
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Additional icons:"; Flags: checkablealone

[Files]
Source: "dist\SamanehNezarat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent unchecked

[Code]
var
  DataChoicePage: TInputOptionWizardPage;
  ExistingDataPath: String;
  HasExistingData: Boolean;

function CheckExistingData(): Boolean;
begin
  ExistingDataPath := ExpandConstant('{commonappdata}') + '\SamanehNezarat';
  if DirExists(ExistingDataPath) and FileExists(ExistingDataPath + '\users.db') then
    Result := True
  else
    Result := False;
end;

procedure ClearExistingData();
begin
  if DirExists(ExistingDataPath) then
    DelTree(ExistingDataPath, True, True, True);
end;

procedure InitializeWizard();
begin
  HasExistingData := CheckExistingData();
  
  if HasExistingData then
  begin
    DataChoicePage := CreateInputOptionPage(
      wpSelectDir,
      'Previous Data Found',
      'A previous installation was detected',
      'Data from a previous version was found at:' + #13#10 + 
      ExistingDataPath + #13#10 + #13#10 +
      'Please choose an option:',
      True,
      False
    );
    
    DataChoicePage.Add('Keep existing data (Recommended)');
    DataChoicePage.Add('Delete and start fresh');
    DataChoicePage.SelectedValueIndex := 0;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if HasExistingData and (DataChoicePage <> nil) then
  begin
    if CurPageID = DataChoicePage.ID then
    begin
      if DataChoicePage.SelectedValueIndex = 1 then
      begin
        if MsgBox('Warning! All previous data will be permanently deleted. Are you sure?', mbConfirmation, MB_YESNO) = IDYES then
          ClearExistingData()
        else
          Result := False;
      end;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  DataPath: String;
  Response: Integer;
begin
  Result := True;
  DataPath := ExpandConstant('{commonappdata}') + '\SamanehNezarat';
  
  if DirExists(DataPath) then
  begin
    Response := MsgBox(
      'Do you want to delete all application data?' + #13#10 + #13#10 +
      'Data location: ' + DataPath + #13#10 + #13#10 +
      'YES = Delete everything' + #13#10 +
      'NO = Keep data for future installation',
      mbConfirmation, MB_YESNO
    );
    
    if Response = IDYES then
      DelTree(DataPath, True, True, True);
  end;
end;
