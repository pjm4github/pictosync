@echo off
REM build_grammar.bat
REM Compiles MermaidSequenceLexer.g4 + MermaidSequenceParser.g4 together.
REM Called by PyCharm External Tool — pass the directory of either .g4 file as %1

set JAR=C:\javalib\antlr-4.13.0-complete.jar
set G4_DIR=%1
set OUT_DIR=%G4_DIR%\generated

echo.
echo === ANTLR4 Grammar Compile ===
echo G4 dir:  %G4_DIR%
echo Out dir: %OUT_DIR%
echo.

java -jar "%JAR%" ^
     -Dlanguage=Python3 ^
     -visitor ^
     -no-listener ^
     -o "%OUT_DIR%" ^
     -lib "%OUT_DIR%" ^
     "%G4_DIR%\MermaidStateDiagramLexer.g4" ^
     "%G4_DIR%\MermaidStateDiagramParser.g4"

if %ERRORLEVEL% == 0 (
    echo.
    echo === Compile OK ===
) else (
    echo.
    echo === Compile FAILED ===
    exit /b 1
)