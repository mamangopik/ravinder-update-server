const express = require('express')
const app = express()
const version = require('./v1.1/version.json')
const port = 3000


app.use('/files', express.static('public'))

app.get('/', (req, res) => {
  res.send('Hello World!')
})
app.get('/dev/ravinder-update-path', (req, res) => {
    res.json({"script_link": version.script_link})
})
app.get('/dev/ravinder-latest-version', (req, res) => {
    res.json({"ravinder": {"version": version.version}})
})

app.listen(port, () => {
  console.log(`app listening on port ${port}`)
})