# PyCoin
A basic implementation of a **cryptocurrencies** Blockchain API.

## blockchain.py
Contains the Blockchain class that manipulates the network chain.

## server.py
Using the **Flask** micro-framework, this file has the HTTP Server code to interact with the Blockchain.

# Usage
- **Micro-framework**

To install the Flask micro-framework:
```
pip install Flask==0.12.2 requests==2.18.4
```

**Important!**
I know it's obvious, but make sure you have Python 3+ installed before continue.

## HTTP Client
I strongly recommend the [Postman](https://www.getpostman.com/) HTTP Client to do the requests below.

You can fire up the application server navigating to the folder with the project and executing the following command:
```
python server.py
```

- **Mining a new block**

> GET localhost:5000/mine

- **Adding a new transaction

> POST localhost:5000/transactions/new

Don't forget to fill in the request body with the transaction's JSON:

```
{
  "sender": "some-address-here",
  "recipient": "another-address",
  "amount": 5
}
 ```
 
 - **Returning the full chain**
 
 > GET localhost:5000/chain
 
 - **Registering new nodes**
 
 You can grab a different machine if you like, and spin up different nodes on your network. 
 Or spin up processes using different ports on the same machine. Then:
 
 > POST localhost:5000/nodes/register
 
 Fill in the request body with your new node JSON, e.g.:
 
 ```
{
  "nodes": ["http://192.168.208.16:8080"]
}
```
 
 - **Consensus mechanism**
 
 To test the ```resolve()``` method and reach a consensus:
 
 > GET localhost:5000/nodes/resolve
