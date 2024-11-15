// server.js
const express = require('express');
const bodyParser = require('body-parser');
const { SDK } = require('@1inch/cross-chain-sdk');

const app = express();
app.use(bodyParser.json());

const sdk = new SDK({
  url: 'https://api.1inch.dev/fusion-plus',
  authKey: 'your-auth-key', // Replace with your actual API key
});

app.post('/getQuote', async (req, res) => {
  try {
    const params = req.body;
    const quote = await sdk.getQuote(params);
    res.json(quote);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add more endpoints as needed...

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
