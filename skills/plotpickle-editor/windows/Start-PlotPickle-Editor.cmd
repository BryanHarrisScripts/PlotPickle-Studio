@echo off
setlocal EnableExtensions
rem PlotPickle Creative Editor - Windows launcher (v0.8.30)
rem Use a user-writable local root; preserve an existing legacy draft if found.
set "DATA_ROOT=%LOCALAPPDATA%\PlotPickle\Projects\The Third Bell\Editor"
if not defined LOCALAPPDATA set "DATA_ROOT=%USERPROFILE%\AppData\Local\PlotPickle\Projects\The Third Bell\Editor"
if exist "%USERPROFILE%\Videos\PlotPickle\The Third Bell\Editor\editor-draft.json" set "DATA_ROOT=%USERPROFILE%\Videos\PlotPickle\The Third Bell\Editor"
if defined PLOTPICKLE_EDITOR_ROOT set "DATA_ROOT=%PLOTPICKLE_EDITOR_ROOT%"

rem Pick Python 3.11 or newer, not the default 'py -3' (which may be Python 3.8).
where py >nul 2>nul
if not errorlevel 1 (
  for %%V in (3.14 3.13 3.12 3.11) do (
    py -%%V -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 (
      set "PYTHON_CMD=py -%%V"
      goto :python_ready
    )
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_ready
  )
)

echo.
echo [PlotPickle] Python 3.11 or newer is required.
echo The previous starter selected Python 3.8. Please install Python 3.11+.
echo Visit https://www.python.org/downloads/windows/
echo If Python is already installed, check 'py -0p' in Command Prompt.
echo.
pause
exit /b 1

:python_ready
if not exist "%DATA_ROOT%\." mkdir "%DATA_ROOT%" 2>nul
if not exist "%DATA_ROOT%\." (
  echo [PlotPickle] Cannot create local media folder:
  echo %DATA_ROOT%
  echo Set PLOTPICKLE_EDITOR_ROOT to a writable folder, then retry.
  pause
  exit /b 1
)
echo [PlotPickle] Using media folder: %DATA_ROOT%
%PYTHON_CMD% "%~dp0editor_server.py" --root "%DATA_ROOT%" --seed "%~dp0the-third-bell-seed.json"
if errorlevel 1 (
  echo [PlotPickle] Startup failed. See the error above.
  pause
  exit /b 1
)
endlocal
