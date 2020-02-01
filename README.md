# phone-api-rest

This is a test developed for PerfectPitchTech.

Here you will find:
<ul>
   <li>Docker image under: app/phone-api-rest_app.gz</li>
   <li>Formatted csv file: app/numbers-response.csv</li>
   <li>Filtered phone numbers: app/numbers-filterd.csv</li> 
</ul>

# How to run the application
To execute and test the application follow below steps:
<ul>
    <il>Download Docker image from: app/phone-api-rest_app.gz </il>
    <li>Import and start Docker container</li>
</ul>

After importing and starting Docker container, 
run below commands from terminal:
<p><code>
curl -i -X POST -H "Content-Type: multipart/form-data" -F "numbers=@numbers.csv" http://localhost:9000/locate_numbers
curl http://localhost:9000/locate_numbers?number=+13101231234
</code></p>
<br/>

# Markdown with the improvements
In order to improve performance in phonenumber library 
I would review below functions:
<ul>
   <li><b>phonenumbers.parse</b>: 
   If the function would receive a standard phone number format
   would be faster the parsing process.</li>
   <li><b>phonenumbers.is_valid_number</b>: 
   This function takes a lot of time to perform validations, 
   the function need to be optimized.</li> 
</ul>
