#!/bin/bash

cd /root/infection

echo "This is a C source file for testing encryption." > infect.c
echo "This is a document file with important data that should be encrypted." > infect.doc
echo "Plain text file content for ransomware testing." > infect.txt

echo "Spreadsheet data: Column1, Column2, Column3" > infect.xlsm
echo "Presentation content goes here." > infect.pptx

echo "CREATE TABLE users (id INT, name VARCHAR(50));" > infect.sql
echo "INSERT INTO data VALUES (1, 'test');" > infect.myi

echo "From: test@example.com\nSubject: Test Email\nBody: This is a test." > infect.ost
echo "Email message content for testing." > infect.eml

echo "using System;\nclass Program { static void Main() {} }" > infect.cs
echo "program Test; begin writeln('Hello'); end." > infect.pas
echo "<?php echo 'Hello World'; ?>" > infect.php

echo "File inside zip" > temp.txt
zip infect.zip temp.txt
rm temp.txt

echo "%PDF-1.4 Fake PDF content for testing" > infect.pdf

echo "Test files created successfully in /root/infection"
ls -lh /root/infection

echo "Container is ready. Use 'make run' to access the shell."
echo "To test Stockholm: /app/Stockholm"