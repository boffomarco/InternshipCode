# Installing CKAN from source

## 1. Install the required packages
    sudo apt-get install python-dev postgresql libpq-dev python-pip python-virtualenv git-core solr-jetty openjdk-8-jdk redis-server

## 2. Install CKAN into a Python virtual environment
### a. Create a Python virtual environment (virtualenv) to install CKAN into, and activate it:
    sudo mkdir -p /usr/lib/ckan/default
    sudo chown 'whoami' /usr/lib/ckan/default
    virtualenv --python=/usr/bin/python2.7 --no-site-packages /usr/lib/ckan/default
    . /usr/lib/ckan/default/bin/activate
### b. Install the recommended ``setuptools`` version:
    pip install setuptools==36.1
### c. Install the CKAN source code into your virtualenv.
    pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.8.2#egg=ckan'
### d. Install the Python modules that CKAN requires into your virtualenv:
    pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt
### e. Deactivate and reactivate your virtualenv, to make sure you’re using the virtualenv’s copies of commands like ``paster`` rather than any system-wide installed copies:
    deactivate
    . /usr/lib/ckan/default/bin/activate

## 3. Setup a PostgreSQL database
### a. Check that PostgreSQL was installed correctly by listing the existing databases:
    sudo -u postgres psql -l
### b. Create a new PostgreSQL database user called ckan_default, and enter a password(password) for the user when prompted. You’ll need this password later:
    sudo -u postgres createuser -S -D -R -P ckan_default
### c. Create a new PostgreSQL database, called ckan_default, owned by the database user you just created:
    sudo -u postgres createdb -O ckan_default ckan_default -E utf-8

## 4. Create a CKAN config file
### a. Create a directory to contain the site’s config files:
    sudo mkdir -p /etc/ckan/default
    sudo chown -R 'whoami' /etc/ckan/
    sudo chown -R 'whoami' ~/ckan/etc
### b. Create the CKAN config file:
    paster make-config ckan /etc/ckan/default/development.ini
### c. Edit the ``development.ini`` file in a text editor, changing the following options:
**sqlalchemy.url**: 
This should refer to the database we created in 3. Setup a PostgreSQL database above:

    sqlalchemy.url = postgresql://ckan_default:pass@localhost/ckan_default
        Replace ``pass`` with the password that you created in 3. Setup a PostgreSQL database above.
**site_id**:
Each CKAN site should have a unique ``site_id``, for example:

    ckan.site_id = default
**site_url**:
Provide the site’s URL (used when putting links to the site into the FileStore, notification emails etc). For example:

    ckan.site_url = http://demo.ckan.org
        Do not add a trailing slash to the URL.

## 5. Setup Solr
### a. Do this step only if you are using Ubuntu 18.04.
    sudo ln -s /etc/solr/solr-jetty.xml /var/lib/jetty9/webapps/solr.xml
### b. The Jetty port value must also be changed on jetty9. To do that, edit the jetty.port value in /etc/jetty9/start.ini:
    jetty.port=8983  # (line 23)
### c. Edit the Jetty configuration file (``/etc/default/jetty9``) and change the following variables:
    NO_START=0            # (line 4)
    JETTY_HOST=127.0.0.1  # (line 16)
    JETTY_PORT=8983       # (line 19)
### d. Start or restart the Jetty server.
    sudo service jetty9 restart
        You should now see a welcome page from Solr if you open http://localhost:8983/solr/
### e. Replace the default ``schema.xml`` file with a symlink to the CKAN schema file included in the sources.
    sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
    sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
### f. Now restart Solr:
    sudo service jetty9 restart
        Check that Solr is running by opening http://localhost:8983/solr/.
### g. Finally, change the solr_url setting in your CKAN configuration file (``/etc/ckan/default/development.ini``, ``/etc/ckan/default/production.ini``) to point to your Solr server, for example:
    solr_url=http://127.0.0.1:8983/solr

### h. Make the following solr updates:
    sudo mkdir /etc/systemd/system/jetty9.service.d
### i. Edit ``/etc/systemd/system/jetty9.service.d/solr.conf`` and add
    [Service]
    ReadWritePaths=/var/lib/solr
### j. Edit ``/etc/solr/solr-jetty.xml`` and replace with the below configuration:
    <?xml version="1.0"  encoding="ISO-8859-1"?>
    <!DOCTYPE Configure PUBLIC "-//Jetty//Configure//EN" "http://www.eclipse.org/jetty/configure.dtd">

    <!-- Context configuration file for the Solr web application in Jetty -->

    <Configure class="org.eclipse.jetty.webapp.WebAppContext">
    <Set name="contextPath">/solr</Set>
    <Set name="war">/usr/share/solr/web</Set>

    <!-- Set the solr.solr.home system property -->
    <Call name="setProperty" class="java.lang.System">
        <Arg type="String">solr.solr.home</Arg>
        <Arg type="String">/usr/share/solr</Arg>
    </Call>

    <!-- Enable symlinks -->
    <!-- Disabled due to being deprecated
    <Call name="addAliasCheck">
        <Arg>
        <New class="org.eclipse.jetty.server.handler.ContextHandler$ApproveSameSuffixAliases"/>
        </Arg>
    </Call>
    -->
    </Configure>
### k. Restart jetty9 
    sudo service jetty9 restart
    systemctl daemon-reload

### l. Download a fix for the lucene error
    wget https://github.com/boffomarco/lucene3.6.2-core-fix/raw/master/lucene3-core-3.6.2.jar -P ~/Downloads/
### m. Copy the fix to the java directory
    cp ~/Downloads/lucene3-core-3.6.2.jar /usr/share/java/lucene3-core-3.6.2.jar
### k. Restart jetty9 
    sudo service jetty9 restart

### 5.1. https://www.liquidweb.com/kb/install-oracle-java-ubuntu-18-04/
### 5.2. http://deeplearning.lipingyang.org/2017/04/30/install-apache-solr-on-ubuntu-16-04/
    cd ~/Downloads
    wget http://archive.apache.org/dist/lucene/solr/6.5.0/solr-6.5.0.zip
    unzip solr-6.5.0.zip
    cd solr-6.5.0/bin
    sudo ./install_solr_service.sh ../../solr-6.5.0.zip
    cd /opt/solr/bin
### 5.3. https://github.com/ckan/ckan/wiki/Install-and-use-Solr-6.5-with-CKAN

## 6. Link to who.ini
### a. ``who.ini`` (the Repoze.who configuration file) needs to be accessible in the same directory as your CKAN config file, so create a symlink to it:
    ln -s /usr/lib/ckan/default/src/ckan/who.ini /etc/ckan/default/who.ini

## 7. Create database tables
### a. Create the database tables:
    cd /usr/lib/ckan/default/src/ckan
    paster db init -c /etc/ckan/default/development.ini
        You should see ``Initialising DB: SUCCESS``.

## 8. Set up the DataStore
### Setting up the DataStore is optional. If you do skip this step, the DataStore features will not be available
### Follow the instructions in [DataStore extension](https://docs.ckan.org/en/2.8/maintaining/datastore.html) to create the required databases and users, set the right permissions and set the appropriate values in your CKAN config file.

## 9. You’re done!
### You can now use the Paste development server to serve CKAN from the command-line. This is a simple and lightweight way to serve CKAN that is useful for development and testing:
    . /usr/lib/ckan/default/bin/activate
    cd /usr/lib/ckan/default/src/ckan
    paster serve /etc/ckan/default/development.ini
### Open http://127.0.0.1:5000/ in a web browser, and you should see the CKAN front page.

## 10. Getting started
### https://docs.ckan.org/en/2.8/maintaining/getting-started.html

## A. Deploying a source install
### If you want to use your CKAN site as a production site, not just for testing or development purposes, then deploy CKAN using a production web server such as Apache or Nginx. See [Deploying a source install](https://docs.ckan.org/en/2.8/maintaining/installing/deployment.html).