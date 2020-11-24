const express = require('express')
const router = express.Router()
const redis = require('redis')
const client = redis.createClient()

client.on("error", function(error) {
  console.error(error)
});

const { promisify } = require('util')
const getAsync = promisify(client.get).bind(client)
const ttlAsync = promisify(client.ttl).bind(client)

/* GET home page. */
router.get('/', (req, res) => {

  client.sendCommand('RANDOMKEY', [], (err, key) => {

    let video = JSON.parse(key)

    console.log(key)
    console.log(video)

    const promiseGet = getAsync(key).then((value) => {
      video['fetched'] = value;
    }).catch(console.error)

    const promiseTtl = ttlAsync(key).then((value => {
      video['ttl'] = value
    })).catch(console.error)

    Promise.all([promiseGet, promiseTtl]).then(() => {
      console.log(video)
      res.render('index', { video: video })
    })

  })
})

module.exports = router;
