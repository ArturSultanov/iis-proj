# Animal shelter (Zvířecí útulek)

## Authors

  * **Lilit Movsesian (xmovse00)**\> [xmovse00@stud.fit.vutbr.cz](mailto:xmovse00@stud.fit.vutbr.cz) - Design and implementation of the application structure, database management (SQLAlchemy, MySQL), creation of models, design and implementation of the veterinarian role's router and HTML templates (Jinja2), implementation of static files (JavaScript, CSS), testing, and debugging the application.
  * **Kirill Shchetiniuk (xshche05)**\> [xshche05@stud.fit.vutbr.cz](mailto:xshche05@stud.fit.vutbr.cz) - Server creation for the application, implementation of SSL connection for secure communication, design and implementation of the application structure, database management (SQLAlchemy, MySQL), creation of models, design and implementation of the administrator and caregiver roles' routers and HTML templates (Jinja2), implementation of static files (JavaScript, CSS), testing, and debugging the application.
  * **Artur Sultanov (xsulta01)**\> [xsulta01@stud.fit.vutbr.cz](mailto:xsulta01@stud.fit.vutbr.cz) - Team leader, work planning, ensuring communication among members, design and implementation of the application structure, database management (SQLAlchemy, MySQL), creation of models, design and implementation of the volunteer role's router and HTML templates (Jinja2), implementation of static files (JavaScript, CSS), testing, and debugging the application.

## Application URL

[https://www.stud.fit.vutbr.cz/\~xsulta01/IIS/](https://www.stud.fit.vutbr.cz/~xsulta01/IIS/)
[https://funnyproject.me/](https://funnyproject.me/)

## System Users for Testing

| Login | Password | Role |
|---|---|---|
| admin | admin | Admin (Administrátor) |
| staff | staff | Caregiver (Pečovatel) |
| vet | vet | Veterinarian (Veterinář) |
| volunteer | volunteer | Volunteer (Dobrovolník) |
| user | user | Registered user (Registrovaný uživatel) |

### Video

## Implementation

This project is a web application developed using the FastAPI Python framework. The application uses a relational MySQL database defined with SQLAlchemy. The core of the application is implemented in the `app` module, which contains the main application logic: router connections, middleware configuration, template settings, database connection initialization, and application lifecycle management. Key functionalities are implemented in the `routers` folder, where the logic is separated for different user types. The project uses HTML templates processed with Jinja2 and a `static` folder containing supporting JavaScript and CSS files.

### Database

## IS Installation

\<p\>Before running the information system on your server, please ensure that your system meets the following requirements.\</p\>

### Requirements

  * **MySQL**: Version `8.0.40` for Linux on `x86_64`
  * **Python**: Version `3.12`
  * **Python Libraries**: All dependencies listed in `requirements.txt`

## Installing and Configuring MySQL

Please, note, that our program does not provide the instance of MySQL database. You need to configured and run mysql demon. The path to the database (host and port), name of the database as well as login and password should be saved to the `.env` file. The example of the `.env` file can be found in the `.env.template` file. In which you can also find additional information for database configuration.

The initial database structure, including all need tables, will be created AUTOMATICALLY, at the first server start.

The example of installation and configuration of MySQL database on Ubuntu with the required specifications:

### 1\. Install MySQL

1.  Install MySQL:
    ```
    sudo apt install mysql-server
    ```

### 2\. Start MySQL

1.  Start the MySQL service:
    ```
    sudo systemctl start mysql
    ```
2.  Run the security script to configure the MySQL installation:
    ```
    sudo mysql_secure_installation
    ```
3.  During this process:
      * Set the root password.
      * Disable remote root login.
      * Remove test databases.
      * Reload privilege tables.

### 3\. Create the Required Database and User

1.  Log in to MySQL as the root user:
    ```
    sudo mysql -u root -p
    ```
2.  Create the `iis` database:
    ```
    CREATE DATABASE iis;
    ```
3.  Create a new user with your credentials:
    ```
    CREATE USER 'user'@'localhost' IDENTIFIED BY 'user';
    ```
4.  Grant the user access to the `iis` database:
    ```
    GRANT ALL PRIVILEGES ON iis.* TO 'user'@'localhost';
    ```
5.  Apply changes:
    ```
    FLUSH PRIVILEGES;
    ```
6.  Exit the MySQL prompt:
    ```
    EXIT;
    ```

Note: The initial database structure, including all need tables, will be created AUTOMATICALLY, at the first server start.

## Setting Up the Environment File

1.  Update the `.env` file with your values. Example:
    ```
    
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=user
    DB_PASS=user
    DB_NAME=iis

    ```

## FastAPI Server Configuration and Startup

1.  **Install Dependencies:**
    ```
    pip install -r requirements.txt
    ```
2.  **Start the Server:**
    \<p\>Navigate to the root directory of the project and run the following command:\</p\>
    ```
    python main.py
    ```

## Knowing issues:

No issues.
