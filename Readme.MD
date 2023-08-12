<div class="site-section">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-7">
                <h2 class="h3 mb-3 text-black">Онлайн Магазин с Джанго</h2>
                <p class="h3 mb-3 text-black"></p>
            </div>
        </div>
    </div>
</div>
<p align="center">
  <p align="center">
    <a href="http://vladi-ivanov.eu/wp-content/uploads/2023/08/logo.jpg" target="_blank">
      <img src="http://vladi-ivanov.eu/wp-content/uploads/2023/08/logo.jpg" alt="JustDjango" height="72">
    </a>
  </p>

</p>

This project was created for almost one month.

---

# Django E-commerce

This is a e-commerce website built with Django.


## Project Summary

The website displays products. Users can add and remove products to/from their cart while also specifying the quantity of each item. They can then enter their address and Firm for invoice and can choose delivery or bank payment.

---

## Running this project

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
virtualenv env
```

That will create a new folder `env` in your project directory. Next activate it with this command on mac/linux:

```
source env/bin/active
```
or use this command for windows:

```
env\Scripts\activate
```

Then install the project dependencies with

```
pip install -r requirements.txt
```

Now you can run the project with this command

```
python manage.py runserver
```

And you have to set up .env file in ecom directory with this variables and with your values:

```
SECRET_KEY="your_secret_key"
DEBUG="True or False"
ALLOWED_HOSTS="your hosts separated by space"
POSTGRES_DB="name of your postgres db"
POSTGRES_PASSWORD="your password of your user for postgres db"
POSTGRES_USER="your user for postgres db"
POSTGRES_HOST="your host for postgres db"
POSTGRES_PORT="your port for postgres db the dafault is 5432"
DEFAULT_FROM_EMAIL="your email with which to send emails to users"
NOTIFY_EMAIL="your email to which will send emails for notify"
EMAIL_HOST_USER="if you not defined DEFAULT_FROM_EMAIL you need to define this with the same email"
EMAIL_HOST_PASSWORD="""your password for the host_email if you use gmaail you need 
to get the password from 'your Google Account/Security/Two-Step Verification/
Application Passwords (on the bottom of the page)/
Add a Application Password and use it here'"""
EMAIL_HOST="smtp.gmail.com or your smtp server"
EMAIL_PORT="587 or your port"
EMAIL_USE_TLS="True or False"
```


## Support

If you need help to run the project or you ant to use it for sell and you must have to setup the project you can connect me by:

### Email: profin.e.store@gmail.com

---

<div align="center">

<i>Other places you can find me:</i><br>

<a href="https://twitter.com/VladiR_Ivanov" target="_blank"><img src="https://img.shields.io/badge/Twitter-%231877F2.svg?&style=flat-square&logo=twitter&logoColor=white" alt="Twitter"></a>

</div>