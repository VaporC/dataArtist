REM create a portable version of dataArtist using 'pyinstaller'
REM the result is saved in /dist/dataArtist


REM rmdir /S /Q dist
REM rmdir /S /Q build

pyinstaller createPortable.spec

COPY packaging dist

REM would be cool to create azip file from all...
REM - this doesnt work: for /d %%a in (dist) do (ECHO zip -r -p "%%~na.zip" ".\%%a\*")