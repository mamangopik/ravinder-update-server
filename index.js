const express = require('express')
const app = express()
const version = require('./v3.0/version.json')
const port = 6500


app.use('/files', express.static('public'))

app.get('/', (req, res) => {
  res.send('Ravinder Update Server')
})
app.get('/ravinder-update-path', (req, res) => {
    res.json({"script_link": version.script_link})
})
app.get('/ravinder-latest-version', (req, res) => {
    res.json({"ravinder": {"version": version.version}})
})

app.listen(port, () => {
  console.log(`app listening on port ${port}`)
})
