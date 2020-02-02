# How to run the application
This is a test developed for PerfectPitchTech.

To execute and test the application run below commands in terminal:
<ul>
    <il>Download the project
        <br/><code>git clone https://github.com/alejandro-mosso/phone-api-rest</code>
    </il>
    <li>Then run below commands under phone-api-rest:
        <br/><code><b>$<b/> docker-compose build</code>
        <br/><code><b>$</b> docker-compose up</code>
    </li>
    <li>After starting Docker container, 
    run below commands from terminal:
    <code>
    <br/><b>$</b> curl -i -X POST -H "Content-Type: multipart/form-data" -F "numbers=@numbers.csv" http://localhost:9000/locate_numbers
    <br/><b>$</b> curl http://localhost:9000/locate_numbers?number=+13101231234
    </code></li>
</ul>
<br/>

After cloning the project you will find in your local 
directory below files:
<ul>
   <li>Formatted csv file: 
   <br/><code>phone-api-rest/numbers-response.csv</code></li>
   <li>Filtered phone numbers: 
   <br/><code>phone-api-rest/numbers-filterd.csv</code></li> 
</ul>

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
