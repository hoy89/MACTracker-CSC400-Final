# MACTracker-CSC400-Final
NOTE: Raspberry Pi image for nodes has not been uploaded due to very large file size. Cannot upload full source code as the majority of the work involved does not directly involve programming - work involved largely involves in depth configuration of hardware. The code in 'Modified Probemon' is the main program used to tie all the components together involved within the node as needed in the project. Other resources used include: Aircrack, Scapy. Do note that the unmodified Probemon with the default arguments does not work as is.

# Directory Structure of MACTracker:
  * flaskr: Main Application
    * -> static: Contains ChartJS and CSS resources
    * -> templates: Contains the HTML framework for the web application portion
      * -> auth: Contains default flask authentication HTML
        * -> login.html
        * -> register.html
      * -> main: Contains bulk of web application HTML
        * -> areaconfig.html: Select task to be done for areas
        * -> createarea.html: Area creation
        * -> index.html: Main page where graphs showing all statistics are located
        * -> maclist.html: View raw MAC address data collection in table form
        * -> nodeconfig.html: Select task to be done for nodes
        * -> registernode.html: Add a node
        * -> selectarea.html: View available areas, and delete option
        * -> selectnode.html: View registered nodes
      * -> base.html: The basis for every HTML page. Sets CSS and Javascript as well as layout
    * -> init.py: Important, sets up flask and Log Reader/Scheduler
    * -> auth.py: Default flask authentication
    * -> db.py: Default flask database set up and connection
    * -> logreader.py: Singular most important program, handles all of the data collection
    * -> main.py: Handles most of the web application back end, as well as statistics processing on demand
    * -> scheduler.py: Keeps track of MAC addresses in reguards to detection time and current detection status
    * -> schema.sql: Sqlite database
    
