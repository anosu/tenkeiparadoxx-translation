const fs = require('fs')
const path = require('path')
const cors = require('cors')
const express = require('express')
const compression = require('compression')

const routers = {}

const app = express()
const PORT = process.env.PORT || 12315

app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`)
    next()
})

app.use(cors())
app.use(compression())
app.use(express.json())

Object.entries(routers).forEach(([path, router]) => {
    app.use(`/${path}`, router)
})

app.all('/', (req, res) => {
    res.redirect('https://github.com/anosu/tenkeiparadoxx-translation')
})

Array.from(['names', 'titles', 'scenes']).forEach(cls => {
    app.get(`/translation/${cls}/*`, (req, res) => {
        const filePath = path.join(__dirname, 'translation', `${cls}/${req.params[0]}`)
        res.sendFile(filePath, err => err && res.sendStatus(404))
    })
})

app.get('/existed/scenes', (req, res) => {
    fs.readdir(path.join(__dirname, 'translation', 'scenes'), (err, files) => {
        if (err) {
            return res.status(500).send(err.message)
        }
        res.send(files)
    })
})

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`)
})
