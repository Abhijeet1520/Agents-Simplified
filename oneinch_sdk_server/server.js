// server.js
const express = require('express');
const bodyParser = require('body-parser');
const { SDK, HashLock, PresetEnum, NetworkEnum } = require('@1inch/cross-chain-sdk');
const Web3 = require('web3');

const app = express();
app.use(bodyParser.json());

// Load environment variables (e.g., from a .env file)
require('dotenv').config();

const authKey = process.env.ONEINCH_API_KEY; // Your 1inch API key
const privateKey = process.env.WALLET_PRIVATE_KEY; // Your wallet's private key
const rpcUrl = process.env.WEB3_PROVIDER_URL; // Your Web3 provider URL

if (!authKey || !privateKey || !rpcUrl) {
  console.error("Please set ONEINCH_API_KEY, WALLET_PRIVATE_KEY, and WEB3_PROVIDER_URL in your environment variables.");
  process.exit(1);
}

const web3 = new Web3(rpcUrl);
const walletAddress = web3.eth.accounts.privateKeyToAccount(privateKey).address;

const { PrivateKeyProviderConnector } = require('@1inch/limit-order-protocol-utils');

const blockchainProvider = new PrivateKeyProviderConnector(privateKey, web3);

const sdk = new SDK({
  url: 'https://api.1inch.dev/fusion-plus',
  authKey,
  blockchainProvider, // Required for order creation
});

// Endpoint to get a quote
app.post('/getQuote', async (req, res) => {
  try {
    const params = req.body;
    const quote = await sdk.getQuote(params);
    res.json(quote);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to create an order
app.post('/createOrder', async (req, res) => {
  try {
    const { quote, preset = 'fast', source = 'sdk-tutorial' } = req.body;
    const secretsCount = quote.presets[preset].secretsCount;

    // Generate secrets
    const secrets = Array.from({ length: secretsCount }).map(() => '0x' + require('crypto').randomBytes(32).toString('hex'));
    const hashLock = secrets.length === 1
      ? HashLock.forSingleFill(secrets[0])
      : HashLock.forMultipleFills(HashLock.getMerkleLeaves(secrets));

    const secretHashes = secrets.map((s) => HashLock.hashSecret(s));

    const orderData = await sdk.createOrder(quote, {
      walletAddress,
      hashLock,
      preset,
      source,
      secretHashes,
    });

    res.json({ ...orderData, secrets });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to submit an order
app.post('/submitOrder', async (req, res) => {
  try {
    const { srcChainId, order, quoteId, secretHashes } = req.body;

    const orderInfo = await sdk.submitOrder(srcChainId, order, quoteId, secretHashes);
    res.json(orderInfo);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to get order status
app.get('/orderStatus/:orderHash', async (req, res) => {
  try {
    const { orderHash } = req.params;
    const status = await sdk.getOrderStatus(orderHash);
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to get fills ready to accept secrets
app.get('/readyToAcceptSecretFills/:orderHash', async (req, res) => {
  try {
    const { orderHash } = req.params;
    const fills = await sdk.getReadyToAcceptSecretFills(orderHash);
    res.json(fills);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to submit a secret
app.post('/submitSecret', async (req, res) => {
  try {
    const { orderHash, secret } = req.body;
    await sdk.submitSecret(orderHash, secret);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add more endpoints as needed...

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
