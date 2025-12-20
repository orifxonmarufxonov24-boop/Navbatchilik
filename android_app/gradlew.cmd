@rem
@rem Gradle startup script for Windows
@rem

@if "%DEBUG%"=="" @echo off
setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.

set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo.
echo ERROR: JAVA_HOME is not set and java not found in PATH.
echo.
goto end

:execute
set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar

set GRADLE_OPTS=-Xmx512m

"%JAVA_EXE%" %GRADLE_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
endlocal
