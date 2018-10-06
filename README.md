<h1>Udactiy Catalog project</h1>
<h2>Countries Catalog Project Description</h2>
<p>This project mimics a "What to do in..." list. It contains a set of Countries, Places (within these countries) and Activities (within these places) you can do.</p>
<p>This project is written in python3 using sqlite database and flask framework. <b>Please make sure that you have all required packages installed:</b></p>
<ul>
 <li>flask</li>
 <li>sqlalchemy (If not using vagrant)</li>
 <li>You need to have python 3 installed. Follow the instruction in the link below depending on your OS system https://realpython.com/installing-python/</li>
 <li>Install VirtualBox. VirtualBox is the software that actually runs the virtual machine. You can download it from virtualbox.org, in the following link https://www.virtualbox.org/wiki/Download_Old_Builds_5_1</li>
 <li>Install Vagrant. Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. Download it from vagrantup.com. In order to access the project you need to have VM and vagrant installed. First cd vagrant and run vagrant ssh and vagrant up</li>
</ul>

<h2>To Start</h2>
<p>First of all you need to create and populate countriescatalog database.</p>
<ul>
 <li>Run db_setup.py</li>
 <li>Run populate_db.py and  populate_image.py</li>
 <li>You are all set. Run project.py</li>
</ul>

