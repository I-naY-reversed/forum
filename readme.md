
# Forking

## Config

Navigate to config.yaml

  

- websitename -> name of the website

- MAIL_DEFAULT_SENDER -> email address

- email_expiration -> expiration time for confirmation emails (default=3600)

- SQLALCHEMY_DATABASE_URI -> database location (default="default")

- postsPerPage -> "hot" posts to display

- contactEmail -> contact email address

- prohibited_words[list] -> deny creation of posts with set parameters

  

## Env vars

*These are the environment variables that will be needed for the program to run without modification.*

  

Google login/registration

```

c-id -> google client id

c-sec -> google client sec

(related functions are loginG and loginGcb[callback])

```
To get client id and client sec visit [Google console](https://console.developers.google.com/)

  

Email

```

e-user -> email username

e-pwd -> email password

```

  

Security

```

pwd-salt -> password salt

s-key -> secret key

```

  

**How to set:**

  

through python

```

import os

os.environ['s-key'] = "dLA5NTfwgG"

```

through replit

1. Navigate to Secrets tab

*Sidebar > Secrets*

2. Enter data

Key == Key

Value == Value

*ie: Key=s-key, value=dLA5NTfwgG*

  
  

## Running

If you require to init a db, in shell write

```

python

from main import db

db.create_all()

```

or in python write

```

from main import db # note main is refering to main.py, can differ

```

  

## Adding admin

To add a user with admin privileges, run the following in shell

```

python

from main import db, User

User.query.filter_by(username="username").first().admin = True

db.session.commit()

```

or in python run

```

from main import db, User

User.query.filter_by(username="username").first().admin = True

db.session.commit()

```

# Contributing

To contribute to this project through replit:
- Fork the project
- Modify it as you want
- DM me (@ENIAC1) with details of the branch (ie. URL to branch)

To contribute through GitHub:
The git can be found [Here](https://github.com/I-naY-reversed/forum)

For a guide on how to contribute visit [MarcDiethelm/Contributing.md](https://github.com/ReplDepot/replit-desktop/blob/dev/.github/CONTRIBUTING.md).