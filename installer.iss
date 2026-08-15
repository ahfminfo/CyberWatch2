; ═══════════════════════════════════════════════════════
; سامانه کاربران تحت نظارت در فضای مجازی
; نصب‌کننده حرفه‌ای - نسخه 11.0
; ═══════════════════════════════════════════════════════

#define MyAppName "سامانه نظارت"
#define MyAppFullName "سامانه کاربران تحت نظارت در فضای مجازی"
#define MyAppVersion "11.0"
#define MyAppPublisher "AHFMInfo"
#define MyAppExeName "SamanehNezarat.exe"

[Setup]
; ═══ تنظیمات پایه ═══
AppId={{A3F5B8D2-7C4E-4E5B-9B1F-8D3C2A1F5E9B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppFullName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/ahfminfo/CyberWatch2
AppSupportURL=https://github.com/ahfminfo/CyberWatch2/issues
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppFullName}
VersionInfoProductName={#MyAppFullName}

; ═══ مسیر نصب ═══
DefaultDirName={autopf}\SamanehNezarat
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableWelcomePage=no

; ═══ خروجی ═══
OutputDir=.
OutputBaseFilename=SamanehNezarat-Setup-v{#MyAppVersion}
Compression=lzma2/ultra
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ═══ رابط کاربری ═══
WizardStyle=modern
WizardResizable=no
ShowLanguageDialog=no
DisableReadyPage=no
DisableFinishedPage=no
AllowNoIcons=yes

; ═══ آیکون‌ها ═══
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppFullName}

; ═══ نیازمندی‌ها ═══
MinVersion=6.1
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64 x86
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; ═══ راست به چپ ═══
LanguageDetectionMethod=none

; ═══ رنگ‌بندی ═══
BackColor=$0F172A
BackColor2=$1E293B
BackSolid=no
WindowVisible=no

; ═══ پیام‌های پایان ═══
CloseApplications=yes
RestartApplications=yes

[Languages]
Name: "farsi"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
farsi.WelcomeLabel1=به راه‌اندازی سامانه نظارت خوش آمدید
farsi.WelcomeLabel2=این نصب‌کننده %n را روی کامپیوتر شما نصب می‌کند.%n%nقبل از ادامه، تمام برنامه‌های در حال اجرا را ببندید.
farsi.FinishedLabel=%1 با موفقیت روی کامپیوتر شما نصب شد.
farsi.ClickFinish=روی پایان کلیک کنید تا نصب‌کننده بسته شود.
farsi.LaunchProgram=اجرای %1

[Tasks]
Name: "desktopicon"; Description: "ایجاد آیکون روی دسکتاپ"; \
    GroupDescription: "آیکون‌های اضافی:"; Flags: checkablealone

Name: "quicklaunchicon"; Description: "ایجاد آیکون Quick Launch"; \
    GroupDescription: "آیکون‌های اضافی:"; Flags: unchecked

[Files]
; ═══ فایل‌های اصلی ═══
Source: "dist\SamanehNezarat\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; ═══ آیکون ═══
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; ═══ README ═══
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; ═══ Start Menu ═══
Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\icon.ico"; \
    Comment: "{#MyAppFullName}"

; ═══ Desktop ═══
Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\icon.ico"; \
    Tasks: desktopicon; \
    Comment: "{#MyAppFullName}"

; ═══ Quick Launch ═══
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\icon.ico"; \
    Tasks: quicklaunchicon

; ═══ Uninstall Shortcut ═══
Name: "{group}\حذف {#MyAppName}"; \
    Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "اجرای {#MyAppName}"; \
    Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
; در Uninstall، فایل‌های تولیدی برنامه پاک بشن
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"

[Code]
// ═══════════════════════════════════════════════════════
// متغیرهای سراسری
// ═══════════════════════════════════════════════════════
var
  DataChoicePage: TInputOptionWizardPage;
  ExistingDataPath: String;
  HasExistingData: Boolean;
  RecordCount: Integer;

// ═══════════════════════════════════════════════════════
// شمارش رکوردهای دیتابیس قبلی (تقریبی)
// ═══════════════════════════════════════════════════════
function CountExistingRecords(): Integer;
var
  FileSize: Integer;
begin
  Result := 0;
  if FileExists(ExistingDataPath + '\users.db') then
  begin
    // برآورد تعداد بر اساس حجم فایل
    // هر رکورد تقریباً 500 بایت
    FileSize := FileSize;
    Result := 1; // فقط برای نشان دادن که داده هست
  end;
end;

// ═══════════════════════════════════════════════════════
// چک کردن وجود دیتابیس قبلی
// ═══════════════════════════════════════════════════════
function CheckExistingData(): Boolean;
begin
  ExistingDataPath := ExpandConstant('{commonappdata}') + '\SamanehNezarat';

  if DirExists(ExistingDataPath) and 
     FileExists(ExistingDataPath + '\users.db') then
  begin
    Result := True;
    RecordCount := CountExistingRecords();
  end
  else
  begin
    Result := False;
    RecordCount := 0;
  end;
end;

// ═══════════════════════════════════════════════════════
// پاک کردن دیتابیس قبلی
// ═══════════════════════════════════════════════════════
procedure ClearExistingData();
begin
  if DirExists(ExistingDataPath) then
  begin
    DelTree(ExistingDataPath, True, True, True);
    Log('Existing database cleared: ' + ExistingDataPath);
  end;
end;

// ═══════════════════════════════════════════════════════
// راه‌اندازی نصب‌کننده
// ═══════════════════════════════════════════════════════
procedure InitializeWizard();
begin
  // چک وجود داده قبلی
  HasExistingData := CheckExistingData();

  // اگر داده قبلی وجود داشت، صفحه انتخاب رو نمایش بده
  if HasExistingData then
  begin
    DataChoicePage := CreateInputOptionPage(
      wpSelectDir,
      '📦 داده‌های قبلی یافت شد',
      'سامانه‌ای از قبل روی این سیستم نصب شده است',
      'داده‌های سامانه قبلی در مسیر زیر یافت شد:' + #13#10 + 
      ExistingDataPath + #13#10 + #13#10 +
      'لطفاً یکی از گزینه‌های زیر را انتخاب کنید:',
      True,
      False
    );

    DataChoicePage.Add('🔒 حفظ داده‌های قبلی (توصیه شده)' + #13#10 + 
      '     دیتابیس فعلی حفظ می‌شود و سامانه از همان استفاده می‌کند');

    DataChoicePage.Add('🗑️ پاک کردن و شروع تازه' + #13#10 +
      '     تمام داده‌های قبلی حذف می‌شود و باید فایل اکسل جدید بارگذاری کنید');

    // پیش‌فرض: حفظ داده
    DataChoicePage.SelectedValueIndex := 0;
  end;
end;

// ═══════════════════════════════════════════════════════
// قبل از نصب - اعمال انتخاب کاربر
// ═══════════════════════════════════════════════════════
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  // اگر صفحه انتخاب داده هست و کاربر روی Next زد
  if HasExistingData and (DataChoicePage <> nil) then
  begin
    if CurPageID = DataChoicePage.ID then
    begin
      // اگر گزینه "پاک کردن" انتخاب شده
      if DataChoicePage.SelectedValueIndex = 1 then
      begin
        if MsgBox(
          '⚠️ هشدار!' + #13#10 + #13#10 +
          'تمام داده‌های قبلی به طور کامل حذف خواهند شد.' + #13#10 +
          'آیا مطمئن هستید؟',
          mbConfirmation, MB_YESNO
        ) = IDYES then
        begin
          ClearExistingData();
        end
        else
        begin
          Result := False; // برگردون به همون صفحه
        end;
      end;
    end;
  end;
end;

// ═══════════════════════════════════════════════════════
// در حال Uninstall - سوال درباره داده‌ها
// ═══════════════════════════════════════════════════════
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
      '📦 آیا می‌خواهید داده‌های سامانه نیز حذف شوند؟' + #13#10 + #13#10 +
      'داده‌ها در مسیر:' + #13#10 +
      DataPath + #13#10 + #13#10 +
      'اگر "بله" را انتخاب کنید، تمام رکوردها و بک‌آپ‌ها حذف می‌شوند.' + 
      #13#10 + #13#10 +
      'اگر "خیر" را انتخاب کنید، داده‌ها برای نصب بعدی حفظ می‌شوند.',
      mbConfirmation, MB_YESNO
    );

    if Response = IDYES then
    begin
      DelTree(DataPath, True, True, True);
    end;
  end;
end;
